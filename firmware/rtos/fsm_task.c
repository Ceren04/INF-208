/*
 * firmware/rtos/fsm_task.c — FSM RT Task (C Implementasyonu)
 * ===========================================================
 * IMU shared memory'den hareket büyüklüğünü okur,
 * 5-durumlu FSM kararını verir ve sonucu ayrı shared memory'e yazar.
 * Python tarafı FSM durumunu buradan okuyarak LED/alarm yönetir.
 *
 * Shared memory:
 *   /veloguard_imu  (imu_task'tan okur)
 *   /veloguard_fsm  (FSM durumunu yazar)
 *
 * Derleme:
 *   gcc -O2 -o fsm_task fsm_task.c -lpthread -lrt -lm
 *
 * Çalıştırma:
 *   sudo ./fsm_task
 *
 * ÇALIŞTIĞI YER: Raspberry Pi 3B (PREEMPT_RT)
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <signal.h>
#include <pthread.h>
#include <sched.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>

#define TASK_PRIORITY   70
#define PERIOD_NS       10000000L   /* 10 ms = 100 Hz */
#define SHM_IMU         "/veloguard_imu"
#define SHM_FSM         "/veloguard_fsm"

/* Eşikler (config.py ile uyumlu) */
#define THRESHOLD_LOW   0.30
#define THRESHOLD_HIGH  0.80
#define ARM_DELAY_S     1.5

/* ── IMU Shared Memory (imu_task.c ile aynı yapı) ────────────────────────── */
typedef struct {
    double   ax, ay, az, gx, gy, gz;
    double   magnitude, temp_c;
    int64_t  timestamp_ns;
    uint32_t seq;
    int      valid;
    pthread_mutex_t mutex;
} ImuShm;

/* ── FSM durumları ────────────────────────────────────────────────────────── */
typedef enum {
    FSM_DISARMED  = 0,
    FSM_ARMED     = 1,
    FSM_PRE_ALARM = 2,
    FSM_ALARM     = 3,
    FSM_RIDE      = 4,
} FsmState;

static const char *STATE_NAMES[] = {
    "DISARMED", "ARMED", "PRE_ALARM", "ALARM", "RIDE"
};

/* ── FSM Shared Memory ────────────────────────────────────────────────────── */
typedef struct {
    int32_t  state;          /* FsmState enum */
    int32_t  is_tamper;
    double   threshold_low;
    double   threshold_high;
    double   last_magnitude;
    int64_t  state_enter_ns;
    uint32_t alarm_count;
    int      valid;
    pthread_mutex_t mutex;
} FsmShm;

/* ── Global ───────────────────────────────────────────────────────────────── */
static volatile int g_running = 1;
static ImuShm *g_imu_shm = NULL;
static FsmShm *g_fsm_shm = NULL;

static void sig_handler(int sig) { (void)sig; g_running = 0; }

static int64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

/* ── Shared memory bağlantısı ─────────────────────────────────────────────── */
static void *shm_open_existing(const char *name, size_t size) {
    int fd = shm_open(name, O_RDWR, 0666);
    if (fd < 0) { perror(name); return NULL; }
    void *ptr = mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    return (ptr == MAP_FAILED) ? NULL : ptr;
}

static FsmShm *fsm_shm_create(void) {
    int fd = shm_open(SHM_FSM, O_CREAT|O_RDWR, 0666);
    if (fd < 0) { perror("fsm shm_open"); return NULL; }
    ftruncate(fd, sizeof(FsmShm));
    FsmShm *shm = mmap(NULL, sizeof(FsmShm), PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
    close(fd);
    if (shm == MAP_FAILED) return NULL;

    memset(shm, 0, sizeof(FsmShm));
    shm->state          = FSM_DISARMED;
    shm->threshold_low  = THRESHOLD_LOW;
    shm->threshold_high = THRESHOLD_HIGH;
    shm->state_enter_ns = now_ns();

    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
    pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
    pthread_mutex_init(&shm->mutex, &attr);
    pthread_mutexattr_destroy(&attr);
    return shm;
}

/* ── Basit Kalman filtresi ────────────────────────────────────────────────── */
static double kalman_update(double *x, double *p, double z,
                             double q, double r) {
    double p_pred = *p + q;
    double k = p_pred / (p_pred + r);
    *x = *x + k * (z - *x);
    *p = (1.0 - k) * p_pred;
    return *x;
}

/* ── FSM geçiş mantığı ────────────────────────────────────────────────────── */
static void fsm_transition(FsmShm *fsm, FsmState new_state) {
    if (fsm->state == new_state) return;
    printf("[fsm_task] %s → %s\n",
           STATE_NAMES[fsm->state], STATE_NAMES[new_state]);
    fsm->state          = new_state;
    fsm->state_enter_ns = now_ns();
    if (new_state == FSM_ALARM) fsm->alarm_count++;
}

/* ── Ana döngü ────────────────────────────────────────────────────────────── */
static void *fsm_loop(void *arg) {
    (void)arg;

    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);

    struct sched_param sp = { .sched_priority = TASK_PRIORITY };
    if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &sp) != 0)
        fprintf(stderr, "[fsm_task] UYARI: SCHED_FIFO ayarlanamadı\n");

    printf("[fsm_task] Döngü başladı — prio=%d\n", TASK_PRIORITY);

    double kf_x = 0.0, kf_p = 1.0;
    int64_t armed_at = 0;
    int64_t pre_alarm_at = 0;
    const int64_t PRE_ALARM_TIMEOUT_NS = 5000000000LL; /* 5 sn */
    const int64_t ARM_DELAY_NS = (int64_t)(ARM_DELAY_S * 1e9);

    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);

    uint32_t last_imu_seq = 0;

    while (g_running) {
        int64_t now = now_ns();

        /* IMU verisini oku */
        double magnitude = 0.0;
        int imu_ok = 0;
        pthread_mutex_lock(&g_imu_shm->mutex);
        if (g_imu_shm->valid && g_imu_shm->seq != last_imu_seq) {
            magnitude = g_imu_shm->magnitude;
            last_imu_seq = g_imu_shm->seq;
            imu_ok = 1;
        }
        pthread_mutex_unlock(&g_imu_shm->mutex);

        if (imu_ok) {
            /* Kalman filtrele */
            double filtered = kalman_update(&kf_x, &kf_p, magnitude,
                                            0.01, 0.1);

            pthread_mutex_lock(&g_fsm_shm->mutex);
            g_fsm_shm->last_magnitude = filtered;

            FsmState state = (FsmState)g_fsm_shm->state;
            double thr_lo  = g_fsm_shm->threshold_low;
            double thr_hi  = g_fsm_shm->threshold_high;

            switch (state) {
            case FSM_DISARMED:
                /* Python tarafı ARM komutu gönderene kadar bekle */
                break;

            case FSM_ARMED:
                if (now - armed_at < ARM_DELAY_NS) break; /* suppress */
                if (filtered > thr_hi)
                    fsm_transition(g_fsm_shm, FSM_ALARM);
                else if (filtered > thr_lo) {
                    fsm_transition(g_fsm_shm, FSM_PRE_ALARM);
                    pre_alarm_at = now;
                }
                break;

            case FSM_PRE_ALARM:
                if (filtered > thr_hi)
                    fsm_transition(g_fsm_shm, FSM_ALARM);
                else if (now - pre_alarm_at > PRE_ALARM_TIMEOUT_NS)
                    fsm_transition(g_fsm_shm, FSM_ARMED);
                break;

            case FSM_ALARM:
                /* Python DISARM komutu gönderene kadar alarm */
                break;

            case FSM_RIDE:
                /* Sadece tamper aktif, hareket alarmı kapalı */
                break;
            }

            g_fsm_shm->valid = 1;
            pthread_mutex_unlock(&g_fsm_shm->mutex);
        }

        /* ARM geçişini izle (Python tarafından yazılır) */
        static FsmState prev_state = FSM_DISARMED;
        FsmState cur = (FsmState)g_fsm_shm->state;
        if (cur == FSM_ARMED && prev_state != FSM_ARMED) {
            armed_at = now;
            kf_x = 0.0; kf_p = 1.0; /* detector sıfırla */
        }
        prev_state = cur;

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
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    printf("=== VeloGuard FSM Task (C/SCHED_FIFO) ===\n");
    printf("Kernel: "); fflush(stdout); system("uname -r");

    /* IMU shared memory'e bağlan */
    printf("[fsm_task] IMU shared memory bekleniyor (%s)...\n", SHM_IMU);
    for (int i = 0; i < 30; i++) {
        g_imu_shm = shm_open_existing(SHM_IMU, sizeof(ImuShm));
        if (g_imu_shm) break;
        struct timespec ts = { .tv_sec = 1 };
        nanosleep(&ts, NULL);
    }
    if (!g_imu_shm) {
        fprintf(stderr, "IMU shared memory bulunamadı. imu_task çalışıyor mu?\n");
        return EXIT_FAILURE;
    }
    printf("[fsm_task] IMU shared memory bağlandı.\n");

    g_fsm_shm = fsm_shm_create();
    if (!g_fsm_shm) return EXIT_FAILURE;
    printf("[fsm_task] FSM shared memory hazır: %s\n", SHM_FSM);

    pthread_t tid;
    pthread_create(&tid, NULL, fsm_loop, NULL);
    pthread_join(tid, NULL);

    munmap(g_imu_shm, sizeof(ImuShm));
    munmap(g_fsm_shm, sizeof(FsmShm));
    shm_unlink(SHM_FSM);
    printf("[fsm_task] Kapatıldı.\n");
    return EXIT_SUCCESS;
}
