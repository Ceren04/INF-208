"""
tools/thermal_model.py — Termal Model Doğrulama Aracı
======================================================
Pi 3B CPU sıcaklığını RC termal modeli ile karşılaştırır.
DHT22 çevre sıcaklığı ve CPU yükü verilerini kullanır.

Çalıştırma:
  Pi'da ölçüm: sudo python3 tools/thermal_model.py --measure --duration 600
  PC'de grafik: python3 tools/thermal_model.py --plot --input thermal_data.csv

ÇALIŞTIĞI YER:
  --measure: Raspberry Pi 3B
  --plot:    PC veya Pi
"""

import argparse
import math
from typing import List


# Pi 3B termal model parametreleri
R_TH = 5.0   # °C/W (heatsink yoksa — Pi 3B için Pi 4'ten biraz yüksek)
C_TH = 45.0  # J/°C (Pi 3B toplam ısıl kapasite)
TAU  = R_TH * C_TH  # 225 saniye zaman sabiti


def measure_thermal_data(duration_s: float, output_csv: str):
    """
    Belirtilen süre boyunca CPU sıcaklığı, DHT22 ve CPU yükünü loglar.

    Yapması gerekenler:
    - DHTDriver başlat
    - stress-ng'yi subprocess ile başlat (4 CPU çekirdeği % 100 yük)
    - duration_s süresince her 5 sn:
      - vcgencmd measure_temp → CPU sıcaklığı
      - DHT22 → çevre sıcaklığı + nem
      - psutil.cpu_percent() → CPU yük yüzdesi
      - CSV'ye yaz: timestamp, cpu_temp_c, ambient_temp_c, cpu_load_pct
    - stress-ng'yi durdur
    """
    pass


def rc_thermal_model(t: float, t_amb: float, p_watts: float,
                     t_initial: float) -> float:
    """
    RC termal modeli ile t saniyedeki CPU sıcaklığını tahmin eder.

    Formül: T(t) = T_amb + P*R_th*(1 - e^(-t/tau)) + (T_initial - T_amb)*e^(-t/tau)

    Yapması gerekenler:
    - Yukarıdaki formülü hesapla
    - float döndür
    """
    pass


def fit_model_to_data(timestamps: List[float], measured_temps: List[float],
                      ambient_temp: float, power_watts: float) -> dict:
    """
    Model tahminlerini gerçek ölçüm verileriyle karşılaştırır.

    Yapması gerekenler:
    - Her timestamp için rc_thermal_model() çağır
    - RMSE (Root Mean Square Error) hesapla
    - Döndür: {"modeled": List[float], "rmse": float, "r_squared": float}
    """
    pass


def plot_thermal_comparison(timestamps: List[float], measured: List[float],
                             modeled: List[float], output_file: str):
    """
    Ölçülen ve modellenen sıcaklıkları aynı grafikte çizer.

    ÇALIŞTIĞI YER: PC

    Yapması gerekenler:
    - matplotlib ile çizdir
    - Ölçülen: mavi çizgi
    - Modellenen (RC): kırmızı kesikli çizgi
    - Eşik çizgileri: 75°C (warn), 80°C (camera off) sarı/kırmızı yatay
    - Başlık, eksen etiketleri, legend
    - output_file'a kaydet
    """
    pass


def main():
    pass


if __name__ == "__main__":
    main()
