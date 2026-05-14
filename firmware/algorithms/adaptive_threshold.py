"""
firmware/algorithms/adaptive_threshold.py — Adaptif Eşik Hesaplayıcı
======================================================================
motion_detector.py'de kullanılan baseline istatistiklerini hesaplar.
Bağımsız modül olarak da test edilebilir.

Algoritma:
  - Son N saniyenin magnitude değerlerini ring buffer'da tutar
  - mean ± k*sigma yöntemiyle dinamik eşik üretir
  - Eşikler sabit fallback değerlerinin asla altına inmez (güvenlik)

ÇALIŞTIĞI YER: Raspberry Pi 3B (ve PC testlerde)
"""

import math
import collections
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AdaptiveThreshold:
    """
    Kayan pencere istatistikleriyle dinamik hareket eşiği hesaplar.
    """

    def __init__(
        self,
        window_size: int,
        k_low: float = 1.5,
        k_high: float = 3.0,
        fallback_low: float = 0.30,
        fallback_high: float = 0.80,
    ):
        """
        Args:
            window_size:   Ring buffer kapasitesi (örnek sayısı).
            k_low:         Düşük eşik çarpanı (mean + k_low * sigma).
            k_high:        Yüksek eşik çarpanı (mean + k_high * sigma).
            fallback_low:  Sabit düşük eşik (kalibre olmadan önce kullanılır).
            fallback_high: Sabit yüksek eşik.
        """
        self._buffer: collections.deque = collections.deque(maxlen=window_size)
        self._k_low = k_low
        self._k_high = k_high
        self._fallback_low = fallback_low
        self._fallback_high = fallback_high
        self._threshold_low = fallback_low
        self._threshold_high = fallback_high
        self._is_calibrated = False

    def add_sample(self, value: float):
        """
        Yeni bir ölçüm değerini ekler ve eşikleri günceller.
        Sadece anormal olmayan değerler eklenmeli (filtrele → sonra ekle).
        """
        self._buffer.append(value)
        if len(self._buffer) >= max(10, self._buffer.maxlen // 6):
            self._recalculate()

    def _recalculate(self):
        n = len(self._buffer)
        if n < 2:
            return
        mu = math.fsum(self._buffer) / n
        variance = math.fsum((x - mu) ** 2 for x in self._buffer) / (n - 1)
        sigma = math.sqrt(variance)

        candidate_low  = mu + self._k_low  * sigma
        candidate_high = mu + self._k_high * sigma

        self._threshold_low  = max(candidate_low,  self._fallback_low)
        self._threshold_high = max(candidate_high, self._fallback_high)
        self._is_calibrated  = True

        logger.debug(
            f"Adaptif eşik güncellendi — "
            f"mu={mu:.4f}g  sigma={sigma:.4f}g  "
            f"low={self._threshold_low:.4f}g  high={self._threshold_high:.4f}g"
        )

    @property
    def thresholds(self) -> Tuple[float, float]:
        """(threshold_low, threshold_high) döndürür."""
        return self._threshold_low, self._threshold_high

    @property
    def is_calibrated(self) -> bool:
        return self._is_calibrated

    @property
    def sample_count(self) -> int:
        return len(self._buffer)

    def reset(self):
        self._buffer.clear()
        self._threshold_low  = self._fallback_low
        self._threshold_high = self._fallback_high
        self._is_calibrated  = False

    def get_stats(self) -> dict:
        n = len(self._buffer)
        if n == 0:
            return {"n": 0, "mean": None, "sigma": None,
                    "threshold_low": self._threshold_low,
                    "threshold_high": self._threshold_high,
                    "is_calibrated": False}
        mu = math.fsum(self._buffer) / n
        variance = math.fsum((x - mu) ** 2 for x in self._buffer) / max(n - 1, 1)
        return {
            "n": n,
            "mean": round(mu, 5),
            "sigma": round(math.sqrt(variance), 5),
            "threshold_low": round(self._threshold_low, 5),
            "threshold_high": round(self._threshold_high, 5),
            "is_calibrated": self._is_calibrated,
        }
