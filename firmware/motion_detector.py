"""
firmware/motion_detector.py — Adaptif Hareket Dedektörü
==========================================================
IMU'dan gelen filtrelenmiş ivme büyüklüğünü analiz eder.
Baseline gürültü seviyesini öğrenerek dinamik eşik belirler.

ÇALIŞTIĞI YER: Raspberry Pi 3B (ve PC testlerde)
"""

import math
import collections
import logging
from enum import Enum
from typing import Optional
from firmware.config import IMUConfig
from firmware.algorithms.kalman import KalmanFilter1D

logger = logging.getLogger(__name__)


class MotionLevel(Enum):
    NONE = 0
    LOW  = 1
    HIGH = 2


class MotionDetector:
    """
    Adaptif eşikli hareket dedektörü.
    30 saniyelik baseline penceresi + Kalman filtresi.
    """

    def __init__(self):
        self._kalman = KalmanFilter1D()
        window = int(IMUConfig.BASELINE_WINDOW_S * IMUConfig.SAMPLE_RATE_HZ)
        self._baseline_window: collections.deque = collections.deque(maxlen=window)
        self._is_calibrated = False
        self._adaptive_k = IMUConfig.ADAPTIVE_K
        self._threshold_low  = IMUConfig.THRESHOLD_LOW_G
        self._threshold_high = IMUConfig.THRESHOLD_HIGH_G

    def update_baseline(self, magnitude: float, current_state: str):
        if current_state != "ARMED":
            return
        if magnitude < self._threshold_high:
            self._baseline_window.append(magnitude)
        min_samples = int(IMUConfig.SAMPLE_RATE_HZ * 5)
        if len(self._baseline_window) >= min_samples:
            self._is_calibrated = True
            self._recalculate_thresholds()

    def _recalculate_thresholds(self):
        n = len(self._baseline_window)
        if n < 2:
            return
        mu = math.fsum(self._baseline_window) / n
        variance = math.fsum((x - mu) ** 2 for x in self._baseline_window) / (n - 1)
        sigma = math.sqrt(variance)

        low  = mu + 1.5 * sigma
        high = mu + self._adaptive_k * sigma

        self._threshold_low  = max(low,  IMUConfig.THRESHOLD_LOW_G)
        self._threshold_high = max(high, IMUConfig.THRESHOLD_HIGH_G)
        logger.debug(f"Adaptif eşik: low={self._threshold_low:.4f}g  high={self._threshold_high:.4f}g")

    def detect(self, raw_magnitude: float) -> MotionLevel:
        filtered = self._kalman.update(raw_magnitude)
        if filtered > self._threshold_high:
            return MotionLevel.HIGH
        if filtered > self._threshold_low:
            return MotionLevel.LOW
        return MotionLevel.NONE

    def get_filtered_magnitude(self, raw_magnitude: float) -> float:
        return self._kalman.update(raw_magnitude)

    def reset(self):
        self._baseline_window.clear()
        self._kalman.reset()
        self._is_calibrated = False
        self._threshold_low  = IMUConfig.THRESHOLD_LOW_G
        self._threshold_high = IMUConfig.THRESHOLD_HIGH_G

    def get_calibration_status(self) -> dict:
        n = len(self._baseline_window)
        needed = int(IMUConfig.SAMPLE_RATE_HZ * 5)
        mu = (math.fsum(self._baseline_window) / n) if n > 0 else None
        return {
            "is_calibrated":    self._is_calibrated,
            "samples_collected": n,
            "samples_needed":   needed,
            "threshold_low_g":  self._threshold_low,
            "threshold_high_g": self._threshold_high,
            "baseline_mean_g":  round(mu, 5) if mu is not None else None,
        }
