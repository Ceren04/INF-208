"""
tools/pareto_sweep.py — Pareto Analizi (Enerji ↔ Tepki Süresi)
===============================================================
Farklı IMU örnekleme frekanslarında enerji tüketimi ve
alarm tepki süresini ölçerek Pareto cephesi çizer.

Çalıştırma:
  Pi'da: sudo python3 tools/pareto_sweep.py --measure   (gerçek ölçüm)
  PC'de: python3 tools/pareto_sweep.py --plot           (önceki veriyi çiz)

ÇALIŞTIĞI YER:
  --measure: Raspberry Pi 3B
  --plot:    PC (matplotlib GUI) veya Pi
"""

import argparse
from typing import List, Tuple


# Konfigürasyonlar: (IMU_Hz, beklenen_güç_mW, beklenen_tepki_ms)
# Gerçek ölçüm sonuçları buraya yazılır
SWEEP_CONFIGS = [
    {"imu_hz": 10,  "label": "ECO"},
    {"imu_hz": 25,  "label": "Düşük"},
    {"imu_hz": 50,  "label": "Orta"},
    {"imu_hz": 100, "label": "Normal (seçilen)"},
    {"imu_hz": 200, "label": "Yüksek"},
]


def measure_single_config(imu_hz: int, measurement_duration_s: float = 60.0) -> dict:
    """
    Tek bir IMU frekansı konfigürasyonu için enerji ve tepki süresi ölçer.

    Yapması gerekenler:
    - IMU örnekleme frekansını imu_hz'e ayarla (IMUDriver.set_sample_rate)
    - energy_logger ile 60 sn enerji logla → ortalama güç (mW)
    - Tepki süresi ölçümü:
      - Sistemi ARMED moduna al
      - Bisikleti elle salla (veya simüle et)
      - ARM → ALARM geçiş süresini ölç (ms)
    - Döndür: {"imu_hz": int, "power_mw": float, "reaction_ms": float}
    """
    pass


def run_full_sweep() -> List[dict]:
    """
    Tüm konfigürasyonlar için measure_single_config() çağırır.

    Yapması gerekenler:
    - SWEEP_CONFIGS üzerinde döngü
    - Her config için measure_single_config() çağır
    - Sonuçları listeye ekle
    - "pareto_data.json" dosyasına kaydet (sonraki --plot için)
    - Sonuç listesini döndür
    """
    pass


def is_pareto_optimal(point: dict, all_points: List[dict]) -> bool:
    """
    Bir noktanın Pareto-optimal olup olmadığını kontrol eder.
    (Başka bir nokta hem daha az güç hem daha az tepki süresi sağlıyorsa dominated)

    Yapması gerekenler:
    - all_points içinde herhangi bir p var mı?
      p["power_mw"] <= point["power_mw"] AND p["reaction_ms"] <= point["reaction_ms"]
      AND (en az birinde kesin daha iyi)
    - Varsa: False (dominated)
    - Yoksa: True (Pareto-optimal)
    """
    pass


def plot_pareto_front(data: List[dict], output_file: str = "docs/figures/pareto_front.png"):
    """
    Pareto cephesini scatter plot olarak çizer.

    ÇALIŞTIĞI YER: PC (matplotlib GUI)

    Yapması gerekenler:
    - matplotlib.pyplot kullan
    - Tüm noktaları gri scatter ile çiz
    - Pareto-optimal noktaları mavi ve dolu marker ile çiz
    - Pareto cephesini kırmızı kesikli çizgi ile birleştir
    - Her noktaya label ekle (imu_hz + label)
    - "Normal (seçilen)" noktasını yıldız ile işaretle
    - X ekseni: "Ortalama Güç (mW)", Y ekseni: "Alarm Tepki Süresi (ms)"
    - Başlık: "VeloGuard Pareto Cephesi: Enerji ↔ Tepki Süresi"
    - output_file'a kaydet ve plt.show() çağır
    """
    pass


def main():
    """
    Yapması gerekenler:
    - argparse: --measure (Pi'da çalıştır), --plot (PC'de çiz), --input JSON dosyası
    - --measure ise run_full_sweep() çağır
    - --plot ise JSON yükle, plot_pareto_front() çağır
    """
    pass


if __name__ == "__main__":
    main()
