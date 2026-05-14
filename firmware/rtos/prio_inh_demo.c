/**
 * rtos/prio_inh_demo.c — Priority Inheritance Ölçüm Demosu
 * ==========================================================
 * PTHREAD_PRIO_INHERIT ile priority inversion'ın önlendiğini
 * kanıtlamak için kullanılır. Hem standalone çalışır hem
 * Python ctypes ile shared library olarak yüklenebilir.
 *
 * Derleme (standalone):
 *   gcc -O2 -o prio_inh_demo prio_inh_demo.c -lpthread -lrt
 *   sudo ./prio_inh_demo
 *
 * Derleme (Python ctypes için shared library):
 *   gcc -shared -fPIC -O2 -o prio_inh_mutex.so prio_inh_demo.c -lpthread -lrt
 *
 * ÇALIŞTIĞI YER: Raspberry Pi 3B (ve Linux PC)
 */

#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <string.h>

/* ─── Yapılandırma ─────────────────────────────────────── */
#define PRIO_LOW    20   /* Logger task — mutex'i tutan    */
#define PRIO_MED    50   /* Comm task  — CPU yükü oluştur  */
#define PRIO_HIGH   80   /* IMU task   — mutex'i bekleyen  */
#define MUTEX_HOLD_NS  50000000L   /* 50ms — mutex tutma süresi  */
#define CPU_STRESS_NS  30000000L   /* 30ms — orta öncelik CPU yükü */

/* ─── Veri yapıları ────────────────────────────────────── */
typedef struct {
    long   delay_ns;      /* Yüksek öncelikli thread'in bekleme süresi */
    int    use_inherit;   /* 1: PRIO_INHERIT kullan, 0: kullanma         */
} MeasurementResult;

static pthread_mutex_t shared_mutex;
static volatile int experiment_done = 0;

/* ─── Fonksiyon bildirimleri ───────────────────────────── */

/**
 * init_mutex_with_inherit:
 *   PTHREAD_PRIO_INHERIT protokollü mutex oluşturur.
 *   Bu ayar olmadan priority inversion yaşanır;
 *   bu ayarla LOW prio thread geçici olarak HIGH prio alır.
 *
 * Yapması gerekenler:
 * - pthread_mutexattr_t başlat
 * - pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT) ayarla
 * - pthread_mutex_init(&shared_mutex, &attr) çağır
 * - attr'ı temizle
 * - 0 döndür (başarı), negatif (hata)
 */
int init_mutex_with_inherit(void);

/**
 * init_mutex_without_inherit:
 *   Standart (PTHREAD_PRIO_NONE) mutex oluşturur.
 *   Karşılaştırma için — priority inversion gözlemlemek için.
 *
 * Yapması gerekenler:
 * - pthread_mutexattr_t başlat (protocol ayarı YOK)
 * - pthread_mutex_init(&shared_mutex, &attr) çağır
 */
int init_mutex_without_inherit(void);

/**
 * low_priority_thread:
 *   Düşük öncelikli thread (PRIO_LOW = 20).
 *   Mutex'i alır, MUTEX_HOLD_NS ns tutar, bırakır.
 *   Gerçek sistemde: Logger task
 *
 * Yapması gerekenler:
 * - SCHED_FIFO, PRIO_LOW önceliği ayarla
 * - pthread_mutex_lock(&shared_mutex)
 * - MUTEX_HOLD_NS nanosaniye meşgul döngü (busy-wait, sleep değil!)
 * - pthread_mutex_unlock(&shared_mutex)
 */
void* low_priority_thread(void* arg);

/**
 * medium_priority_thread:
 *   Orta öncelikli thread (PRIO_MED = 50).
 *   Priority inversion'da LOW prio'yu preempt ederek HIGH'ı bloklar.
 *   Gerçek sistemde: Comm task
 *
 * Yapması gerekenler:
 * - SCHED_FIFO, PRIO_MED önceliği ayarla
 * - CPU_STRESS_NS nanosaniye meşgul döngü (preemption simülasyonu)
 */
void* medium_priority_thread(void* arg);

/**
 * high_priority_thread:
 *   Yüksek öncelikli thread (PRIO_HIGH = 80).
 *   Mutex almak için bekler — bekleme süresi ölçülür.
 *   Gerçek sistemde: IMU task
 *
 * Yapması gerekenler:
 * - SCHED_FIFO, PRIO_HIGH önceliği ayarla
 * - clock_gettime(CLOCK_MONOTONIC) ile bekleme başlangıcını kaydet
 * - pthread_mutex_lock(&shared_mutex)   ← bekleme burada olur
 * - clock_gettime ile bekleme bitişini kaydet
 * - Bekleme süresini hesapla, arg (MeasurementResult*)'a yaz
 * - pthread_mutex_unlock(&shared_mutex)
 */
void* high_priority_thread(void* arg);

/**
 * run_experiment:
 *   Tek bir deney koşusunu yürütür (with veya without inherit).
 *
 * Yapması gerekenler:
 * - use_inherit'e göre mutex başlat
 * - LOW, MED, HIGH thread'lerini belirli sırayla başlat:
 *   1. LOW thread başlar (mutex alır)
 *   2. Kısa bekle (LOW mutex'i tutarken)
 *   3. HIGH thread başlar (mutex için bekler)
 *   4. MED thread başlar (CPU yükü oluşturur)
 * - Tüm thread'lerin bitmesini bekle (pthread_join)
 * - HIGH thread'in bekleme süresini MeasurementResult'a kaydet
 * - Mutex temizle
 */
MeasurementResult run_experiment(int use_inherit);

/**
 * print_results:
 *   İki deneyin sonuçlarını karşılaştırmalı yazdırır.
 *
 * Yapması gerekenler:
 * - "Without PRIO_INHERIT: HIGH prio bekledi X ms" satırı
 * - "With    PRIO_INHERIT: HIGH prio bekledi Y ms" satırı
 * - İyileşme yüzdesini hesapla: (X - Y) / X * 100
 * - Rapora konacak tablo formatında çıktı ver
 */
void print_results(MeasurementResult without_inherit, MeasurementResult with_inherit);

/**
 * main:
 *   İki deneyi sırayla çalıştırır ve sonuçları karşılaştırır.
 *
 * Yapması gerekenler:
 * - Root kontrolü yap (SCHED_FIFO için gerekli)
 * - run_experiment(0) → without_inherit sonucu
 * - run_experiment(1) → with_inherit sonucu
 * - print_results() ile karşılaştır
 * - 0 döndür
 */
int main(int argc, char* argv[]);

/* ─── Python ctypes arayüzü (shared library için) ─────── */

/**
 * veloguard_mutex_init:
 *   Python ctypes'tan çağrılacak mutex başlatma fonksiyonu.
 *   ctypes.CDLL("prio_inh_mutex.so").veloguard_mutex_init(1) şeklinde çağrılır.
 *
 * Parametreler:
 *   use_inherit: 1 → PRIO_INHERIT, 0 → standart
 * Dönüş: 0 başarı, -1 hata
 */
int veloguard_mutex_init(int use_inherit);

/**
 * veloguard_mutex_lock:
 *   Python ctypes'tan mutex lock çağrısı.
 *   Dönüş: 0 başarı, pthread_mutex_lock hata kodu
 */
int veloguard_mutex_lock(void);

/**
 * veloguard_mutex_unlock:
 *   Python ctypes'tan mutex unlock çağrısı.
 */
int veloguard_mutex_unlock(void);

/**
 * veloguard_mutex_destroy:
 *   Mutex'i temizler.
 */
void veloguard_mutex_destroy(void);
