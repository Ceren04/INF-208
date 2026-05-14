"""
tools/motion_test_laptop.py — Laptop Kamerası ile OpenCV Hareket Testi
======================================================================
Pi Camera olmadan laptop webcam'i ile OpenCV motion detection'ı test eder.
Pi'ya port edilmeden önce algoritma burada geliştirilir.

Çalıştırma: python3 tools/motion_test_laptop.py

ÇALIŞTIĞI YER: PC (geliştirici bilgisayarı) — Pi'da çalışmaz
"""


def open_webcam(device_id: int = 0):
    """
    Laptop webcam'ini açar.

    Yapması gerekenler:
    - cv2.VideoCapture(device_id) ile kamerayı aç
    - Çözünürlüğü 640×480'e ayarla (Pi ile aynı)
    - Kamera açılamadıysa RuntimeError fırlat
    - VideoCapture nesnesini döndür
    """
    pass


def detect_motion_in_frame(prev_frame, curr_frame, min_area: int = 500):
    """
    İki ardışık kare arasında hareket tespit eder.
    (CameraDriver.detect_motion_region() ile aynı algoritma — test için kopya)

    Yapması gerekenler:
    - Her iki frame'i gri tonlamaya çevir
    - absdiff → threshold → dilate → findContours
    - Büyük konturlar için boundingRect döndür
    - Hareket yoksa None döndür
    """
    pass


def draw_overlay(frame, bbox, fps: float):
    """
    Kare üzerine hareket kutusu ve FPS bilgisi çizer.

    Yapması gerekenler:
    - bbox varsa: kırmızı dikdörtgen çiz, "MOTION" yaz
    - FPS'i sol üstte yaz
    - Fonksiyon yardımı için "Q: çıkış" yaz
    - İşlenmiş frame'i döndür
    """
    pass


def run_motion_demo():
    """
    Canlı webcam akışında motion detection döngüsü çalıştırır.

    Yapması gerekenler:
    - open_webcam() ile kamera aç
    - İlk frame'i al (prev_frame olarak sakla)
    - Döngü (q tuşuna kadar):
      - Yeni frame oku
      - detect_motion_in_frame() çağır
      - draw_overlay() çağır
      - cv2.imshow() ile göster
      - FPS hesapla
      - prev_frame = curr_frame
      - cv2.waitKey(1) == ord('q') ise çık
    - cv2.destroyAllWindows()
    - Kamerayı kapat
    """
    pass


if __name__ == "__main__":
    run_motion_demo()


# ─────────────────────────────────────────────────────────────────
"""
tools/imu_live_plot.py — IMU Canlı Grafik Aracı
================================================
Pi üzerinde çalışırken ivme verilerini canlı grafik olarak gösterir.
Bisikleti sallayarak hareket eşiklerini görsel olarak ayarlamak için kullanılır.

Çalıştırma: python3 tools/imu_live_plot.py --duration 30

ÇALIŞTIĞI YER: Raspberry Pi 3B (matplotlib backend: Agg veya TkAgg)
"""


def collect_imu_samples(duration_s: float, sample_hz: int = 50):
    """
    Belirtilen süre boyunca IMU verisi toplar.

    Yapması gerekenler:
    - IMUDriver başlat
    - duration_s * sample_hz kadar örnek topla
    - Her örnekte: read() → magnitude hesapla → listeye ekle
    - Döndür: {"timestamps": List[float], "magnitudes": List[float],
               "ax": List[float], "ay": List[float], "az": List[float]}
    """
    pass


def plot_imu_data(data: dict, threshold_low: float, threshold_high: float,
                  output_file: str = "docs/imu_sample.png"):
    """
    Toplanan IMU verisini grafik olarak çizer.

    Yapması gerekenler:
    - 3 alt grafik (subplot):
      1. ax, ay, az zaman serisi (3 renkli çizgi)
      2. Hareket büyüklüğü (magnitude) + eşik çizgileri
      3. Kalman filtreli büyüklük karşılaştırması
    - Eşik çizgileri:
      - threshold_low: sarı noktalı yatay çizgi
      - threshold_high: kırmızı noktalı yatay çizgi
    - output_file'a kaydet
    """
    pass


if __name__ == "__main__":
    import argparse
    # argparse: --duration, --hz, --output
    pass
