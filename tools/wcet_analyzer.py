"""
tools/wcet_analyzer.py — WCET (En Kötü Durum Yürütme Süresi) Analiz Aracı
===========================================================================
Pi'dan alınan GPIO toggle loglarını veya clock_gettime ölçümlerini analiz eder.
Min/Avg/Max/P99 değerlerini hesaplar ve tablo+grafik üretir.

Çalıştırma: python3 tools/wcet_analyzer.py --input sensor_data.csv

ÇALIŞTIĞI YER: PC (geliştirici bilgisayarı) veya Pi
"""

import argparse
import sys
from typing import List, Dict


def load_timing_data(filepath: str) -> Dict[str, List[float]]:
    """
    CSV dosyasından zamanlama verilerini yükler.

    CSV formatı (her satır): timestamp, task_name, duration_us
    Örnek: 1717000000.123, imu_sampling, 1250.5

    Yapması gerekenler:
    - CSV dosyasını aç
    - task_name bazında grupla
    - Döndür: {"imu_sampling": [1250.5, 1180.2, ...], "fsm_core": [...], ...}
    - Dosya bulunamazsa FileNotFoundError fırlat
    """
    pass


def compute_statistics(durations: List[float]) -> dict:
    """
    Zamanlama listesinden istatistiksel metrikleri hesaplar.

    Yapması gerekenler:
    - min, max, mean, median, std hesapla
    - P95 (95. yüzdelik), P99 (99. yüzdelik) hesapla (sorted list ile)
    - Döndür: {"min": f, "max": f, "mean": f, "p95": f, "p99": f, "count": int}
    """
    pass


def check_wcet_budget(task_name: str, max_us: float, budget_us: float) -> bool:
    """
    Ölçülen WCET'in bütçe içinde olup olmadığını kontrol eder.

    Yapması gerekenler:
    - max_us <= budget_us ise True ve "✅ PASS" yazdır
    - max_us > budget_us ise False ve "❌ FAIL (bütçe: X µs, ölçülen: Y µs)" yazdır
    """
    pass


def print_wcet_table(all_stats: Dict[str, dict], budgets: Dict[str, float]):
    """
    Tüm task'ların WCET tablosunu konsola yazdırır.

    Çıktı formatı:
    ┌──────────────────┬────────┬────────┬─────────┬──────────┬──────────┬────────┐
    │ Task             │ Min µs │ Avg µs │ Max µs  │ P99 µs   │ Bütçe µs │ Durum  │
    ├──────────────────┼────────┼────────┼─────────┼──────────┼──────────┼────────┤
    │ imu_sampling     │  850   │ 1100   │  1420   │  1380    │  1500    │ ✅     │
    ...

    Yapması gerekenler:
    - Her task için compute_statistics() sonuçlarını tablola
    - check_wcet_budget() ile bütçe kontrolü yap
    """
    pass


def plot_wcet_histogram(task_name: str, durations: List[float], budget_us: float):
    """
    Tek task için WCET dağılım histogramı çizer.
    Bütçe sınırını kırmızı dikey çizgi ile işaretler.

    ÇALIŞTIĞI YER: PC (matplotlib GUI)

    Yapması gerekenler:
    - matplotlib.pyplot ile histogram çiz (50 bin)
    - Dikey kırmızı çizgi: budget_us'da
    - Başlık: f"{task_name} WCET Dağılımı"
    - X ekseni: "Yürütme Süresi (µs)", Y ekseni: "Frekans"
    - docs/figures/wcet_{task_name}.png olarak kaydet
    - plt.show() çağır
    """
    pass


def main():
    """
    Komut satırı arayüzü.

    Yapması gerekenler:
    - argparse ile --input (CSV dosyası) ve --plot (grafik çiz?) parametrelerini al
    - load_timing_data() çağır
    - Her task için compute_statistics() ve print_wcet_table() çağır
    - --plot verilmişse plot_wcet_histogram() çağır
    """
    pass


if __name__ == "__main__":
    main()
