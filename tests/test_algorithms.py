"""
tests/test_algorithms.py — Algoritma Birim Testleri
====================================================
Kalman filtresi, AdaptiveThreshold ve MotionDetector testleri.

Çalıştırma:
  pytest tests/test_algorithms.py -v

ÇALIŞTIĞI YER: PC ve Pi (donanım gerektirmez)
"""

import math
import time
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from firmware.algorithms.kalman import KalmanFilter1D
from firmware.algorithms.adaptive_threshold import AdaptiveThreshold
from firmware.motion_detector import MotionDetector, MotionLevel


# ── KalmanFilter1D ────────────────────────────────────────────────────────────

class TestKalmanFilter1D:
    def test_initial_state_zero(self):
        kf = KalmanFilter1D()
        assert kf.x == 0.0
        assert kf.p == 1.0

    def test_converges_to_constant(self):
        kf = KalmanFilter1D()
        for _ in range(100):
            kf.update(1.0)
        assert abs(kf.x - 1.0) < 0.01

    def test_smooths_noise(self):
        import random
        kf = KalmanFilter1D()
        noisy = [1.0 + random.gauss(0, 0.5) for _ in range(200)]
        filtered = [kf.update(v) for v in noisy]
        # Filtrelenmiş değerlerin varyansı ham değerlerden küçük olmalı
        var_raw = sum((v - 1.0)**2 for v in noisy) / len(noisy)
        var_filt = sum((v - 1.0)**2 for v in filtered[50:]) / len(filtered[50:])
        assert var_filt < var_raw

    def test_reset_clears_state(self):
        kf = KalmanFilter1D()
        for _ in range(50):
            kf.update(5.0)
        kf.reset()
        assert kf.x == 0.0
        assert kf.p == 1.0

    def test_reset_with_initial_value(self):
        kf = KalmanFilter1D()
        kf.update(10.0)
        kf.reset(initial_value=3.0)
        assert kf.x == 3.0

    def test_set_noise_params(self):
        kf = KalmanFilter1D()
        kf.set_noise_params(q=0.001, r=1.0)
        assert kf.q == 0.001
        assert kf.r == 1.0

    def test_high_r_slow_response(self):
        """Yüksek ölçüm gürültüsü → yavaş güncelleme."""
        kf_slow = KalmanFilter1D(q=0.01, r=10.0)
        kf_fast = KalmanFilter1D(q=0.01, r=0.01)
        for _ in range(10):
            kf_slow.update(1.0)
            kf_fast.update(1.0)
        assert kf_fast.x > kf_slow.x  # hızlı filtre daha çabuk yaklaştı

    def test_update_returns_float(self):
        kf = KalmanFilter1D()
        result = kf.update(0.5)
        assert isinstance(result, float)

    def test_negative_values(self):
        kf = KalmanFilter1D()
        for _ in range(50):
            kf.update(-1.0)
        assert abs(kf.x - (-1.0)) < 0.1

    def test_zero_measurement(self):
        kf = KalmanFilter1D()
        result = kf.update(0.0)
        assert isinstance(result, float)


# ── AdaptiveThreshold ─────────────────────────────────────────────────────────

class TestAdaptiveThreshold:
    def test_initial_thresholds_are_fallback(self):
        at = AdaptiveThreshold(window_size=100,
                                fallback_low=0.3, fallback_high=0.8)
        lo, hi = at.thresholds
        assert lo == 0.3
        assert hi == 0.8

    def test_not_calibrated_initially(self):
        at = AdaptiveThreshold(window_size=100)
        assert at.is_calibrated is False

    def test_calibrates_after_enough_samples(self):
        at = AdaptiveThreshold(window_size=100, fallback_low=0.3, fallback_high=0.8)
        for _ in range(20):  # window_size//6 = ~17
            at.add_sample(0.02)
        assert at.is_calibrated is True

    def test_sample_count_increases(self):
        at = AdaptiveThreshold(window_size=100)
        at.add_sample(0.1)
        at.add_sample(0.2)
        assert at.sample_count == 2

    def test_thresholds_above_fallback(self):
        at = AdaptiveThreshold(window_size=50,
                                fallback_low=0.3, fallback_high=0.8)
        for _ in range(20):
            at.add_sample(0.02)
        lo, hi = at.thresholds
        assert lo >= 0.3
        assert hi >= 0.8

    def test_reset_clears_calibration(self):
        at = AdaptiveThreshold(window_size=50)
        for _ in range(20):
            at.add_sample(0.02)
        at.reset()
        assert at.is_calibrated is False
        assert at.sample_count == 0

    def test_noisy_samples(self):
        import random
        at = AdaptiveThreshold(window_size=200,
                                k_low=1.5, k_high=3.0,
                                fallback_low=0.3, fallback_high=0.8)
        for _ in range(50):
            at.add_sample(abs(random.gauss(0.02, 0.005)))
        assert at.is_calibrated
        lo, hi = at.thresholds
        assert hi > lo

    def test_get_stats_returns_dict(self):
        at = AdaptiveThreshold(window_size=50)
        stats = at.get_stats()
        assert "n" in stats
        assert "is_calibrated" in stats


# ── MotionDetector ────────────────────────────────────────────────────────────

class TestMotionDetector:
    def test_none_when_calm(self):
        md = MotionDetector()
        for _ in range(100):
            level = md.detect(0.01)
        assert level == MotionLevel.NONE

    def test_high_on_large_motion(self):
        md = MotionDetector()
        level = md.detect(2.0)
        assert level == MotionLevel.HIGH

    def test_low_on_medium_motion(self):
        md = MotionDetector()
        # Kalman filtresi kademeli olarak yüksek değere yaklaşır
        # Birkaç iterasyonda 0.5g'ye ulaşmasını sağla
        level = MotionLevel.NONE
        for _ in range(50):
            level = md.detect(0.5)
            if level != MotionLevel.NONE:
                break
        assert level in (MotionLevel.LOW, MotionLevel.HIGH)

    def test_reset_clears_baseline(self):
        md = MotionDetector()
        for _ in range(100):
            md.update_baseline(0.02, "ARMED")
        status_before = md.get_calibration_status()
        md.reset()
        status_after = md.get_calibration_status()
        assert status_after["samples_collected"] == 0
        assert not status_after["is_calibrated"]

    def test_baseline_only_updates_when_armed(self):
        md = MotionDetector()
        for _ in range(100):
            md.update_baseline(0.02, "DISARMED")
        status = md.get_calibration_status()
        assert status["samples_collected"] == 0

    def test_baseline_updates_when_armed(self):
        md = MotionDetector()
        for _ in range(600):  # 5sn x 100Hz = 500 örnek
            md.update_baseline(0.02, "ARMED")
        status = md.get_calibration_status()
        assert status["samples_collected"] > 0

    def test_get_filtered_magnitude_returns_float(self):
        md = MotionDetector()
        result = md.get_filtered_magnitude(0.5)
        assert isinstance(result, float)

    def test_calibration_status_keys(self):
        md = MotionDetector()
        status = md.get_calibration_status()
        assert "is_calibrated" in status
        assert "samples_collected" in status
        assert "threshold_low_g" in status
        assert "threshold_high_g" in status

    def test_no_baseline_update_during_alarm(self):
        md = MotionDetector()
        for _ in range(100):
            md.update_baseline(1.5, "ALARM")  # yüksek değer alarm durumunda
        status = md.get_calibration_status()
        assert status["samples_collected"] == 0  # alarm sırasında eklenmemeli
