/*
 * firmware/rtos/hello_rt.c — SCHED_FIFO Gerçek Zamanlı Thread Demo
 * ==================================================================
 * 3 thread farklı SCHED_FIFO öncelikleriyle çalışır.
 * Öncelik sıralamasının gerçek zamanlı zamanlayıcı tarafından
 * nasıl uygulandığını gösterir.
 *
 * Derleme:
 *   gcc -O2 -o hello_rt hello_rt.c -lpthread -lrt
 *
 * Çalıştırma (root gerektirir):
 *   sudo ./hello_rt
 *
 * ÇALIŞTIĞI YER: Raspberry Pi 3B (PREEMPT veya PREEMPT_RT kernel)
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

#define NUM_THREADS     3
#define ITERATIONS      5
#define SLEEP_MS        200

/* Thread parametreleri */
typedef struct {
    int   id;
    int   priority;
    const char *name;
} ThreadParams;

/* Nanosaniye cinsinden monotonic saat */
static long long now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (long long)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

static void sleep_ms(int ms) {
    struct timespec ts = { .tv_sec = ms / 1000,
                           .tv_nsec = (ms % 1000) * 1000000L };
    nanosleep(&ts, NULL);
}

/* Thread çalıştırıcı */
static void *rt_thread(void *arg) {
    ThreadParams *p = (ThreadParams *)arg;

    /* Bu thread'in önceliğini ayarla */
    struct sched_param sp = { .sched_priority = p->priority };
    int ret = pthread_setschedparam(pthread_self(), SCHED_FIFO, &sp);
    if (ret != 0) {
        fprintf(stderr, "[%s] UYARI: SCHED_FIFO ayarlanamadı: %s "
                "(root ile çalıştırın)\n", p->name, strerror(ret));
    }

    long long t_start = now_ns();
    for (int i = 0; i < ITERATIONS; i++) {
        long long elapsed_us = (now_ns() - t_start) / 1000;
        printf("[%6lld µs] Thread %-12s | Prio %2d | İterasyon %d/%d\n",
               elapsed_us, p->name, p->priority, i + 1, ITERATIONS);
        fflush(stdout);
        sleep_ms(SLEEP_MS);
    }

    printf("[Thread %-12s] Tamamlandı.\n", p->name);
    return NULL;
}

int main(void) {
    pthread_t threads[NUM_THREADS];
    ThreadParams params[NUM_THREADS] = {
        { 0, 80, "HIGH-Prio"   },
        { 1, 50, "MID-Prio"    },
        { 2, 20, "LOW-Prio"    },
    };

    printf("=== VeloGuard SCHED_FIFO Demo ===\n");
    printf("Kernel: ");
    fflush(stdout);
    system("uname -r");
    printf("Öncelik sırası: HIGH(80) > MID(50) > LOW(20)\n\n");

    /* Thread'leri oluştur */
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_attr_t attr;
        pthread_attr_init(&attr);
        pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
        pthread_attr_setschedpolicy(&attr, SCHED_FIFO);

        struct sched_param sp = { .sched_priority = params[i].priority };
        pthread_attr_setschedparam(&attr, &sp);

        int ret = pthread_create(&threads[i], &attr, rt_thread, &params[i]);
        if (ret != 0) {
            fprintf(stderr, "pthread_create hatası: %s\n", strerror(ret));
            exit(EXIT_FAILURE);
        }
        pthread_attr_destroy(&attr);
    }

    /* Tümünü bekle */
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("\n=== Demo tamamlandı ===\n");
    return 0;
}
