"""
tools/energy_logger.py — INA219 Enerji Loglama Aracı
======================================================
Pi'da belirli süre boyunca enerji tüketimini loglar.
Her FSM durumu için ayrı ölçüm alır (DISARMED, ARMED, ALARM, RIDE).
Sonuçlar rapordaki enerji tablosu için kullanılır.

Çalıştırma: sudo python3 tools/energy_logger.py --duration 300 --output energy.csv

ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import argparse
import time


def log_energy_for_state(state_name: str, duration_s: float, output_file: str):
    """
    Belirtilen süre boyunca enerji verilerini loglar.

    Yapması gerekenler:
    - INA219Driver başlat
    - CSV dosyasına header yaz (ilk çağrıda): timestamp, state, voltage_v, current_ma, power_mw
    - duration_s süresince döngü:
      - INA219'dan oku
      - CSV'ye yaz
      - 0.5 sn bekle
    - "Ölçüm tamamlandı: N örnek, ortalama P mW" yazdır
    """
    pass


def compute_energy_summary(csv_file: str) -> dict:
    """
    Kaydedilen enerji CSV'sinden her durum için ortalama güç hesaplar.

    Yapması gerekenler:
    - CSV oku
    - state bazında grupla
    - Her state için: mean_mw, min_mw, max_mw hesapla
    - Pil ömrü tahmini: (3000mAh * 3.7V) / mean_w_armed = saat
    - Tablo yazdır ve dict döndür
    """
    pass


def main():
    """
    Yapması gerekenler:
    - argparse: --duration, --state, --output
    - log_energy_for_state() çağır
    - compute_energy_summary() çağır
    """
    pass


if __name__ == "__main__":
    main()
