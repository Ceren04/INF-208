"""
firmware/drivers/dht_driver.py — DHT22 Sıcaklık & Nem Sürücüsü
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import logging
from typing import Optional
from firmware.drivers.base_sensor import BaseSensor
from firmware.config import ThermalConfig

logger = logging.getLogger(__name__)

_MAX_RETRY    = 3
_RETRY_DELAY  = 0.5


class DHTDriver(BaseSensor):
    def __init__(self):
        super().__init__("DHT22")
        self._dht = None
        self._pin_number = 4
        self._last_temp:     Optional[float] = None
        self._last_humidity: Optional[float] = None

    def initialize(self) -> bool:
        try:
            import adafruit_dht  # type: ignore
            import board         # type: ignore
            self._dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
            # Test okuması
            _ = self._dht.temperature
            self._initialized = True
            self._logger.info("DHT22 başlatıldı — GPIO4")
            return True
        except Exception as exc:
            self._logger.error(f"DHT22 başlatılamadı: {exc}")
            return False

    def read(self) -> Optional[dict]:
        if not self._initialized or self._dht is None:
            return None

        for attempt in range(_MAX_RETRY):
            try:
                temp = self._dht.temperature
                hum  = self._dht.humidity
                if temp is not None and hum is not None:
                    self._last_temp     = temp
                    self._last_humidity = hum
                    return {
                        "timestamp":       time.time(),
                        "temp_c":          round(temp, 1),
                        "humidity":        round(hum, 1),
                        "cpu_temp_c":      self.get_cpu_temperature(),
                    }
            except RuntimeError as exc:
                self._logger.debug(f"DHT22 okuma hatası (deneme {attempt+1}): {exc}")
                time.sleep(_RETRY_DELAY)
            except Exception as exc:
                self._logger.warning(f"DHT22 beklenmeyen hata: {exc}")
                time.sleep(_RETRY_DELAY)

        # Tüm denemeler başarısız — stale veri
        if self._last_temp is not None:
            self._logger.warning("DHT22 stale veri döndürülüyor")
            return {
                "timestamp": time.time(),
                "temp_c":    self._last_temp,
                "humidity":  self._last_humidity,
                "cpu_temp_c": self.get_cpu_temperature(),
                "stale":     True,
            }
        return None

    def get_cpu_temperature(self) -> Optional[float]:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                return round(int(f.read().strip()) / 1000.0, 1)
        except Exception:
            return None

    def get_combined_thermal_data(self) -> dict:
        data = self.read() or {}
        cpu  = self.get_cpu_temperature()
        return {
            "timestamp":           time.time(),
            "ambient_temp_c":      data.get("temp_c"),
            "ambient_humidity_pct": data.get("humidity"),
            "cpu_temp_c":          cpu,
        }

    def cleanup(self):
        if self._dht is not None:
            try:
                self._dht.exit()
            except Exception:
                pass
            self._dht = None
        self._initialized = False
        self._logger.info("DHT22 kapatıldı.")
