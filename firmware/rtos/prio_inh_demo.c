/*
 * firmware/rtos/prio_inh_demo.c — Priority Inversion & Inheritance Demo
 * =======================================================================
 * Priority Inversion problemi ve PTHREAD_PRIO_INHERIT çözümünü ölçer.
 *
 * SENARYO:
 *   Thread LOW  (prio 20): mutex alır, 3sn CPU işi yapar, mutex bırakır
 *   Thread MID  (prio 50): CPU yakar (mutex almaz) → priority inversion nedeni
 *   Thread HIGH (prio 80): mutex almak ister → bekler
 *
 * BEKLENEN SONUÇLAR:
 *   PRIO_NONE:    HIGH, LOW'un işi bitene kadar BEKLER (~3sn)
 *                 Çünkü MID, LOW'u preempt eder ve LOW mutex'i bırakamaz
 *   PRIO_INHERIT: LOW'un önceliği geçici olarak HIGH'a yükselir
 *                 MID preempt edemez → HIGH ~3sn bekleme yerine ~0sn bekler
 *
 * Derleme:
 *   gcc -O2 -o prio_inh_demo prio_inh_demo.c -lpthread -lrt -lm
 *
 * Çalıştırma:
 *   sudo ./prio_inh_demo          (PRIO_INHERIT aktif)
 *   sudo ./prio_inh_demo none     (PRIO_NONE — inversion görmek için)
 *
 * CSV çıktısı:  prio_results.csv  (prio_inv_plot.py ile grafik çizilir)
 *
 * ÇALIŞTIĞI YER: Raspberry Pi 3B
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <math.h>

/* ── Ayarlar ──────────────────────────────────────────────────────────────── */
#define LOW_WORK_S      3       /* LOW thread'in mutex tutma süresi (sn) */
#define MID_BURN_S      5       /* MID thread'in CPU yakma süresi (sn) */
#define HIGH_WAIT_LIMIT 10      /* HIGH'ın maksimum bekleme süresi (sn) */

#define PRIO_LOW        20
#define PRIO_MID        50
#define PRIO_HIGH       80

/* ── Global değişkenler ───────────────────────────────────────────────────── */
static pthread_mutex_t g_mutex;
static int  g_use_inherit = 1;
static FILE *g_csv = NULL;

/* Zaman yardımcıları */
static long long now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static double ns_to_ms(long long ns) { return (double)ns / 1e6; }

static void csv_log(const char *thread, const char *event, double elapsed_ms) {
    if (g_csv)
        fprintf(g_csv, "%.3f,%s,%s\n", elapsed_ms, thread, event);
}

/* Yoğun CPU döngüsü (MID thread için priority inversion baskısı) */
static void burn_cpu(double seconds) {
    struct timespec end;
    clock_gettime(CLOCK_MONOTONIC, &end);
    end.tv_sec  += (time_t)seconds;
    end.tv_nsec += (long)((seconds - (time_t)seconds) * 1e9);
    if (end.tv_nsec >= 1000000000L) {
        end.tv_sec++;
        end.tv_nsec -= 1000000000L;
    }
    volatile double x = 1.0;
    struct timespec now;
    do {
        for (int i = 0; i < 10000; i++) x = sqrt(x + 1.0);
        clock_gettime(CLOCK_MONOTONIC, &now);
    } while (now.tv_sec < end.tv_sec ||
             (now.tv_sec == end.tv_sec && now.tv_nsec < end.tv_nsec));
    (void)x;
}

/* ── Thread'ler ───────────────────────────────────────────────────────────── */

static long long g_t0;  /* Başlangıç zamanı */

static void set_rt_prio(int prio) {
    /* Tüm thread'leri CPU 0'a sabitle — Priority Inversion ancak
     * tek çekirdekte görünür (çok çekirdekte threadler paralel koşar) */
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);

    struct sched_param sp = { .sched_priority = prio };
    int ret = pthread_setschedparam(pthread_self(), SCHED_FIFO, &sp);
    if (ret != 0)
        fprintf(stderr, "UYARI: SCHED_FIFO ayarlanamadı (prio=%d): %s\n",
                prio, strerror(ret));
}

/* LOW thread: mutex al → yavaş CPU işi → bırak */
static void *thread_low(void *arg) {
    (void)arg;
    set_rt_prio(PRIO_LOW);

    double t = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] LOW  başladı (prio=%d)\n", t, PRIO_LOW);
    csv_log("LOW", "start", t);

    /* Mutex al */
    pthread_mutex_lock(&g_mutex);
    t = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] LOW  mutex ALDI — %dsn CPU işi yapıyor...\n", t, LOW_WORK_S);
    csv_log("LOW", "mutex_acquired", t);

    burn_cpu(LOW_WORK_S);

    /* Mutex bırak */
    t = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] LOW  mutex BIRAKTI\n", t);
    csv_log("LOW", "mutex_released", t);
    pthread_mutex_unlock(&g_mutex);

    t = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] LOW  tamamlandı\n", t);
    csv_log("LOW", "done", t);
    return NULL;
}

/* MID thread: mutex almaz, sadece CPU yakar → priority inversion baskısı */
static void *thread_mid(void *arg) {
    (void)arg;
    set_rt_prio(PRIO_MID);

    /* LOW'un mutex almasını bekle */
    struct timespec ts = { .tv_nsec = 100000000L }; /* 100ms */
    nanosleep(&ts, NULL);

    double t = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] MID  başladı (prio=%d) — CPU yakıyor...\n", t, PRIO_MID);
    csv_log("MID", "start", t);

    burn_cpu(MID_BURN_S);

    t = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] MID  tamamlandı\n", t);
    csv_log("MID", "done", t);
    return NULL;
}

/* HIGH thread: mutex ister → bekler → alır */
static void *thread_high(void *arg) {
    (void)arg;
    set_rt_prio(PRIO_HIGH);

    /* LOW'un mutex almasını bekle */
    struct timespec ts = { .tv_nsec = 200000000L }; /* 200ms */
    nanosleep(&ts, NULL);

    double t_request = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] HIGH mutex istiyor (prio=%d) ← BEKLEME BAŞLIYOR\n",
           t_request, PRIO_HIGH);
    csv_log("HIGH", "mutex_request", t_request);

    /* KRİTİK ölçüm: mutex için ne kadar bekledi? */
    pthread_mutex_lock(&g_mutex);
    double t_acquired = ns_to_ms(now_ns() - g_t0);
    double wait_ms = t_acquired - t_request;

    printf("[%.1fms] HIGH mutex ALDI — bekleme süresi: %.1fms ← ÖLÇÜM\n",
           t_acquired, wait_ms);
    csv_log("HIGH", "mutex_acquired", t_acquired);

    /* Kısa iş */
    struct timespec ts2 = { .tv_nsec = 10000000L }; /* 10ms */
    nanosleep(&ts2, NULL);

    pthread_mutex_unlock(&g_mutex);
    double t_done = ns_to_ms(now_ns() - g_t0);
    printf("[%.1fms] HIGH tamamlandı\n", t_done);
    csv_log("HIGH", "done", t_done);

    /* Sonuç özeti */
    printf("\n╔══════════════════════════════════════════════════╗\n");
    printf("║  %-16s │ HIGH bekleme süresi: %8.1f ms  ║\n",
           g_use_inherit ? "PRIO_INHERIT" : "PRIO_NONE   ", wait_ms);
    printf("╚══════════════════════════════════════════════════╝\n\n");

    return NULL;
}

/* ── Mutex başlatıcı ──────────────────────────────────────────────────────── */
static void init_mutex(int use_inherit) {
    pthread_mutexattr_t attr;
    pthread_mutexattr_init(&attr);
    pthread_mutexattr_settype(&attr, PTHREAD_MUTEX_ERRORCHECK);

    if (use_inherit) {
        pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);
        printf("Mutex protokolü: PTHREAD_PRIO_INHERIT ← Priority Inversion önlendi\n");
    } else {
        pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_NONE);
        printf("Mutex protokolü: PTHREAD_PRIO_NONE ← Priority Inversion görülecek\n");
    }

    pthread_mutex_init(&g_mutex, &attr);
    pthread_mutexattr_destroy(&attr);
}

/* ── Thread oluşturucu ────────────────────────────────────────────────────── */
static pthread_t create_rt_thread(void *(*fn)(void*), int prio) {
    pthread_t tid;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    struct sched_param sp = { .sched_priority = prio };
    pthread_attr_setschedparam(&attr, &sp);
    pthread_create(&tid, &attr, fn, NULL);
    pthread_attr_destroy(&attr);
    return tid;
}

/* ── main ─────────────────────────────────────────────────────────────────── */
int main(int argc, char *argv[]) {
    g_use_inherit = 1;
    if (argc > 1 && strcmp(argv[1], "none") == 0)
        g_use_inherit = 0;

    /* CSV dosyası */
    const char *csv_name = g_use_inherit ? "prio_inherit.csv" : "prio_none.csv";
    g_csv = fopen(csv_name, "w");
    if (g_csv) {
        fprintf(g_csv, "elapsed_ms,thread,event\n");
        printf("CSV log: %s\n", csv_name);
    }

    printf("\n=== VeloGuard Priority Inversion Demo ===\n");
    printf("Kernel: "); fflush(stdout); system("uname -r");
    printf("Senaryo: LOW(prio=%d) mutex tutar, MID(prio=%d) CPU yakar, "
           "HIGH(prio=%d) mutex ister\n\n", PRIO_LOW, PRIO_MID, PRIO_HIGH);

    init_mutex(g_use_inherit);
    g_t0 = now_ns();

    /* LOW önce başlar (mutex alacak) */
    pthread_t t_low  = create_rt_thread(thread_low,  PRIO_LOW);
    struct timespec ts = { .tv_nsec = 50000000L }; /* 50ms */
    nanosleep(&ts, NULL);

    /* MID ve HIGH başlar */
    pthread_t t_mid  = create_rt_thread(thread_mid,  PRIO_MID);
    pthread_t t_high = create_rt_thread(thread_high, PRIO_HIGH);

    pthread_join(t_low,  NULL);
    pthread_join(t_mid,  NULL);
    pthread_join(t_high, NULL);

    pthread_mutex_destroy(&g_mutex);
    if (g_csv) fclose(g_csv);

    printf("CSV kaydedildi: %s\n", csv_name);
    printf("Grafik için: python3 tools/prio_inv_plot.py\n");
    return 0;
}
