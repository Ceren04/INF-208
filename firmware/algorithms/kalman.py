"""
algorithms/kalman.py — 1D Kalman Filtresi
==========================================
IMU ham ivme büyüklüğündeki gürültüyü temizlemek için
basit 1 boyutlu Kalman filtresi uygular.

Kullanım yeri: motion_detector.py içinde IMU okumaları filtrelenir.

ÇALIŞTIĞI YER: Raspberry Pi 3B (ve PC testlerde)
"""

import logging
from firmware.config import IMUConfig

logger = logging.getLogger(__name__)


class KalmanFilter1D:
    """
    Tek boyutlu skaler Kalman filtresi.
    Durum: ivme büyüklüğü (g cinsinden skalerde)

    Durum geçiş modeli sabit (identity): x_k = x_{k-1} + gürültü
    Ölçüm modeli: z_k = x_k + ölçüm gürültüsü
    """

    def __init__(self,
                 q: float = IMUConfig.KALMAN_Q,
                 r: float = IMUConfig.KALMAN_R):
        self.q = q
        self.r = r
        self.x = 0.0   # durum tahmini
        self.p = 1.0   # hata kovaryansı

    def update(self, measurement: float) -> float:
        # Tahmin adımı
        x_pred = self.x
        p_pred = self.p + self.q

        # Güncelleme adımı
        k = p_pred / (p_pred + self.r)   # Kalman kazancı
        self.x = x_pred + k * (measurement - x_pred)
        self.p = (1.0 - k) * p_pred

        return self.x

    def reset(self, initial_value: float = 0.0):
        self.x = initial_value
        self.p = 1.0

    def set_noise_params(self, q: float, r: float):
        self.q = q
        self.r = r
