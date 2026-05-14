"""
firmware/drivers/ina219_driver.py — INA219 Akım/Voltaj Sensörü Sürücüsü
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import csv
import os
import threading
import logging
from typing import Optional
from firmware.drivers.base_sensor import BaseSensor
from firmware.config import PowerConfig, LogConfig

logger = logging.getLogger(__name__)


def _voltage_to_pct(v: float) -> float:
    """18650 voltajını 0-100% pil seviyesine çevirir."""
    lo = PowerConfig.VBAT_EMPTY_V
    hi = PowerConfig.VBAT_FULL_V
    return round(max(0.0, min(100.0, (v - lo) / (hi - lo) * 100.0)), 1)


class INA219Driver(BaseSensor):
    def __init__(self):
        super().__init__("INA219")
        self._ina  = None
        self._i2c  = None
        self._logging_active = False
        self._log_thread: Optional[threading.Thread] = None
        self._log_file = None

    def initialize(self) -> bool:
        try:
            import board                    # type: ignore
            import busio                    # type: ignore
            import adafruit_ina219          # type: ignore
            self._i2c = busio.I2C(board.SCL, board.SDA)
            self._ina = adafruit_ina219.INA219(self._i2c, addr=0x40)
            self._ina.set_calibration_32V_2A()
            # Test okuması
            v = self._ina.bus_voltage
            if v <= 0:
                raise ValueError(f"Geçersiz voltaj: {v}")
            self._initialized = True
            self._logger.info(f"INA219 başlatıldı — voltaj: {v:.2f}V")
            return True
        except Exception as exc:
            self._logger.error(f"INA219 başlatılamadı: {exc}")
            return False

    def read(self) -> Optional[dict]:
        if not self._initialized or self._ina is None:
            return None
        try:
            v_bus   = self._ina.bus_voltage
            v_shunt = self._ina.shunt_voltage * 1000  # V → mV
            current = self._ina.current
            power   = self._ina.power * 1000           # W → mW
            pct     = _voltage_to_pct(v_bus)
            return {
                "timestamp":       time.time(),
                "bus_voltage_v":   round(v_bus,   3),
                "shunt_voltage_mv": round(v_shunt, 3),
                "current_ma":      round(current,  1),
                "power_mw":        round(power,    1),
                "battery_pct":     pct,
            }
        except Exception as exc:
            self._logger.warning(f"INA219 okuma hatası: {exc}")
            return None

    def is_battery_low(self) -> bool:
        data = self.read()
        if data is None:
            return False
        return data["battery_pct"] < PowerConfig.BATTERY_LOW_PCT

    def is_battery_critical(self) -> bool:
        data = self.read()
        if data is None:
            return False
        return data["battery_pct"] < PowerConfig.BATTERY_CRITICAL_PCT

    def start_logging(self, sample_hz: float = PowerConfig.INA219_SAMPLE_HZ):
        if self._logging_active:
            return
        csv_path = os.path.join(LogConfig.LOG_DIR, "ina219_energy.csv")
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        write_header = not os.path.exists(csv_path)
        self._log_file = open(csv_path, "a", newline="")
        self._csv_writer = csv.writer(self._log_file)
        if write_header:
            self._csv_writer.writerow(
                ["timestamp", "bus_voltage_v", "current_ma", "power_mw", "battery_pct"]
            )
        self._logging_active = True
        self._log_thread = threading.Thread(
            target=self._log_loop, args=(sample_hz,), daemon=True, name="INA219Logger"
        )
        self._log_thread.start()
        self._logger.info("INA219 enerji loglama başladı.")

    def _log_loop(self, sample_hz: float):
        interval = 1.0 / sample_hz
        while self._logging_active:
            data = self.read()
            if data:
                try:
                    self._csv_writer.writerow([
                        f"{data['timestamp']:.3f}",
                        data["bus_voltage_v"],
                        data["current_ma"],
                        data["power_mw"],
                        data["battery_pct"],
                    ])
                    self._log_file.flush()
                except Exception as exc:
                    self._logger.error(f"INA219 log yazma hatası: {exc}")
            time.sleep(interval)

    def stop_logging(self):
        self._logging_active = False
        if self._log_file:
            try:
                self._log_file.close()
            except Exception:
                pass
            self._log_file = None

    def cleanup(self):
        self.stop_logging()
        if self._i2c is not None:
            try:
                self._i2c.deinit()
            except Exception:
                pass
            self._i2c = None
        self._initialized = False
        self._logger.info("INA219 kapatıldı.")
