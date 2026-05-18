/*
 * firmware/rtos/imu_task.c — IMU Okuma RT Task (C Implementasyonu)
 * ==================================================================
 * MPU-6050'yi 100Hz'de okuyan SCHED_FIFO thread.
 * Okunan ivme büyüklüğü POSIX shared memory'e yazılır;
 * Python tarafı (shared_state.py) oradan okur.
 *
 * Shared memory şeması (imu_shm.h ile uyumlu):
 *   /veloguard_imu → struct ImuShm { double ax,ay,az,magnitude; int64_t ts_ns; }
 *
 * Derleme:
 *   gcc -O2 -o imu_task imu_task.c -lpthread -lrt -lm
 *
 * Çalıştırma:
 *   sudo ./imu_task          (SCHED_FIFO prio=80)
 *
 * WCET ölçümü: GPIO19 High/Low ile (osciloskop veya logic analyzer)
 *
 * ÇALIŞTIĞI YER: Raspberry Pi 3B
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <errno.h>
#include <math.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <sched.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>

/* ── Sabitler ─────────────────────────────────────────────────────────────── */
#define I2C_BUS         "/dev/i2c-1"
#define MPU_ADDR        0x68
#define REG_PWR_MGMT_1  0x6B
#define REG_ACCEL_XOUT  0x3B
#define ACCEL_SCALE     16384.0   /* ±2g */
#define GYRO_SCALE      131.0     /* ±250°/s */

#define SAMPLE_HZ       100
#define PERIOD_NS       (1000000000L / SAMPLE_HZ)   /* 10 ms */
#define TASK_PRIORITY   80
#define SHM_NAME        "/veloguard_imu"

/* ── Shared memory yapısı ─────────────────────────────────────────────────── */
typedef struct {
    double   ax, ay, az;        /* g cinsinden ivme */
    double   gx, gy, gz;        /* °/s cinsinden açısal hız */
    double   magnitude;         /* |sqrt(ax²+ay²+az²) - 1g| */
    double   temp_c;            /* MPU dahili sıcaklık */
    int64_t  timestamp_ns;      /* CLOCK_MONOTONIC ns */
    uint32_t seq;               /* sıra numarası */
    int      valid;             /* 1=geçerli veri, 0=henüz hazır değil */
    pthread_mutex_t mutex;      /* PRIO_INHERIT mutex */
} ImuShm;

/* ── Global ───────────────────────────────────────────────────────────────── */
static volatile int g_running = 1;
static ImuShm *g_shm = NULL;
static int g_i2c_fd = -1;

/* ── Sinyal handler ───────────────────────────────────────────────────────── */
static void sig_handler(int sig) { (void)sig; g_running = 0; }

/* ── Yardımcı: nanosaniye zaman ───────────────────────────────────────────── */
static int64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static int16_t to_signed16(uint8_t hi, uint8_t lo) {
    int16_t val = (int16_t)((uint16_t)hi << 8 | lo);
    return val;
}

/* ── I2C başlat ───────────────────────────────────────────────────────────── */
static int i2c_init(void) {
    g_i2c_fd = open(I2C_BUS, O_RDWR);
    if (g_i2c_fd < 0) {
        perror("I2C bus açılamadı");
        return -1;
    }
    if (ioctl(g_i2c_fd, I2C_SLAVE, MPU_ADDR) < 0) {
        perror("I2C slave adresi ayarlanamadı");
        return -1;
    }
    /* Uyku modundan çıkar */
    uint8_t buf[2] = { REG_PWR_MGMT_1, 0x00 };
    if (write(g_i2c_fd, buf, 2) != 2) {
        perror("MPU6050 wake-up yazılamadı");
        return -1;
    }
    struct timespec ts = { .tv_nsec = 50000000L };
    nanosleep(&ts, NULL);
    printf("[imu_task] MPU-6050 başlatıldı: %s @ 0x%02X\n", I2C_BUS, MPU_ADDR);
    return 0;
}

/* ── I2C oku ──────────────────────────────────────────────────────────────── */
static int i2c_read_mpu(double *ax, double *ay, double *az,
                         double *gx, double *gy, double *gz,
                         double *temp) {
    uint8_t reg = REG_ACCEL_XOUT;
    uint8_t raw[14];

    if (write(g_i2c_fd, &reg, 1) != 1) return -1;
    if (read(g_i2c_fd, raw, 14) != 14) return -1;

    *ax   = to_signed16(raw[0],  raw[1])  / ACCEL_SCALE;
    *ay   = to_signed16(raw[2],  raw[3])  / ACCEL_SCALE;
    *az   = to_signed16(raw[4],  raw[5])  / ACCEL_SCALE;
    int16_t tr = to_signed16(raw[6], raw[7]);
    *gx   = to_signed16(raw[8],  raw[9])  / GYRO_SCALE;
    *gy   = to_signed16(raw[10], raw[11]) / GYRO_SCALE;
    *gz   = to_signed16(raw[12], raw[13]) / GYRO_SCALE;
    *temp = (tr / 340.0) + 36.53;
    return 0;
}

/* ── Shared memory başlat ─────────────────────────────────────────────────── */
static int shm_init(void) {
    int fd = shm_open(SHM_NAME, O_CREAT | O_RDWR, 0666);
    if (fd < 0) { perror("shm_open"); return -1; }
    if (ftruncate(fd, sizeof(ImuShm)) < 0) { perror("ftruncate"); return -1; }
    g_shm = mmap(NULL, sizeof(ImuShm), PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (g_shm == MAP_FAILED) { perror("mmap"); return -1; }

    memset(g_shm, 0, sizeof(ImuShm));

    /* PRIO_INHERIT mutex */
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
    pthread_mutex_init(&g_shm->mutex, &attr);
    pthread_mutexattr_destroy(&attr);

    printf("[imu_task] Shared memory hazır: %s (%zu bytes)\n",
           SHM_NAME, sizeof(ImuShm));
    return 0;
}

/* ── Ana döngü ────────────────────────────────────────────────────────────── */
static void *imu_loop(void *arg) {
    (void)arg;

    /* CPU 0'a sabitle */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);

    /* SCHED_FIFO */
    struct sched_param sp = { .sched_priority = TASK_PRIORITY };
    if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &sp) != 0)
        fprintf(stderr, "[imu_task] UYARI: SCHED_FIFO ayarlanamadı\n");

    printf("[imu_task] Döngü başladı — %dHz, prio=%d, CPU0\n",
           SAMPLE_HZ, TASK_PRIORITY);

    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);

    while (g_running) {
        int64_t t_start = now_ns();

        double ax, ay, az, gx, gy, gz, temp;
        if (i2c_read_mpu(&ax, &ay, &az, &gx, &gy, &gz, &temp) == 0) {
            double mag = fabs(sqrt(ax*ax + ay*ay + az*az) - 1.0);

            pthread_mutex_lock(&g_shm->mutex);
            g_shm->ax = ax; g_shm->ay = ay; g_shm->az = az;
            g_shm->gx = gx; g_shm->gy = gy; g_shm->gz = gz;
            g_shm->magnitude    = mag;
            g_shm->temp_c       = temp;
            g_shm->timestamp_ns = t_start;
            g_shm->seq++;
            g_shm->valid = 1;
            pthread_mutex_unlock(&g_shm->mutex);
        }

        /* Periyodik zamanlama */
        next.tv_nsec += PERIOD_NS;
        while (next.tv_nsec >= 1000000000L) {
            next.tv_nsec -= 1000000000L;
            next.tv_sec++;
        }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL);
    }

    return NULL;
}

/* ── main ─────────────────────────────────────────────────────────────────── */
int main(void) {
    signal(SIGINT,  sig_handler);
    signal(SIGTERM, sig_handler);

    printf("=== VeloGuard IMU Task (C/SCHED_FIFO) ===\n");
    printf("Kernel: "); fflush(stdout); system("uname -r");

    if (i2c_init()  < 0) return EXIT_FAILURE;
    if (shm_init()  < 0) return EXIT_FAILURE;

    pthread_t tid;
    pthread_create(&tid, NULL, imu_loop, NULL);
    pthread_join(tid, NULL);

    /* Temizlik */
    if (g_shm)  munmap(g_shm, sizeof(ImuShm));
    shm_unlink(SHM_NAME);
    if (g_i2c_fd >= 0) close(g_i2c_fd);

    printf("[imu_task] Kapatıldı.\n");
    return EXIT_SUCCESS;
}
