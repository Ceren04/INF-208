"""
firmware/drivers/imu_driver.py — MPU-6050 IMU Sürücüsü
===============================================
GY-521 / MPU-6050 6-eksenli ivmeölçer + jiroskop modülünü
I2C üzerinden yönetir. Ham veriden hareket büyüklüğünü hesaplar
ve Kalman filtresine ham veri akışı sağlar.

Bağlantı:
  VCC → 3.3V | GND → GND
  SDA → GPIO2 (pin 3) | SCL → GPIO3 (pin 5)
  I2C adresi: 0x68 (AD0=GND) veya 0x69 (AD0=3.3V)

ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import math
import logging
from typing import Optional
import smbus2
from firmware.drivers.base_sensor import BaseSensor
from firmware.config import Pins, IMUConfig

logger = logging.getLogger(__name__)

# MPU-6050 Register adresleri
_REG_WHO_AM_I   = 0x75
_REG_PWR_MGMT_1 = 0x6B
_REG_SMPLRT_DIV = 0x19
_REG_ACCEL_XOUT = 0x3B
_REG_GYRO_XOUT  = 0x43
_REG_TEMP_OUT   = 0x41
_ACCEL_SCALE    = 16384.0   # ±2g → 1g = 16384 LSB
_GYRO_SCALE     = 131.0     # ±250°/s → 1°/s = 131 LSB


def _to_signed(val: int) -> int:
    """16-bit unsigned'ı signed'a çevirir."""
    return val - 65536 if val >= 32768 else val


class IMUDriver(BaseSensor):
    """
    MPU-6050 I2C sürücüsü.
    İvmeölçer ve jiroskop verilerini okur, g ve °/s cinsine çevirir.
    """

    def __init__(self):
        super().__init__("IMU")
        self._bus: Optional[smbus2.SMBus] = None
        self._addr = Pins.IMU_I2C_ADDR

    def initialize(self) -> bool:
        try:
            self._bus = smbus2.SMBus(1)
            time.sleep(0.01)

            who = self._bus.read_byte_data(self._addr, _REG_WHO_AM_I)
            # 0x68 = orijinal MPU-6050, 0x72 = yaygın GY-521 klon, 0x70 = MPU-6500
            _KNOWN_WHO_AM_I = {0x68, 0x70, 0x71, 0x72, 0x73, 0x98}
            if who not in _KNOWN_WHO_AM_I:
                self._logger.warning(f"Bilinmeyen WHO_AM_I: {hex(who)} — yine de devam ediliyor")
            else:
                self._logger.info(f"WHO_AM_I: {hex(who)} ✓")

            # Uyku modundan çıkar
            self._bus.write_byte_data(self._addr, _REG_PWR_MGMT_1, 0x00)
            time.sleep(0.05)

            # Örnekleme hızını ayarla
            self.set_sample_rate(IMUConfig.SAMPLE_RATE_HZ)

            self._initialized = True
            self._logger.info(f"MPU-6050 başlatıldı — adres {hex(self._addr)}")
            return True

        except Exception as exc:
            self._logger.error(f"MPU-6050 başlatılamadı: {exc}")
            return False

    def read(self) -> Optional[dict]:
        if not self._initialized or self._bus is None:
            return None
        try:
            raw = self._bus.read_i2c_block_data(self._addr, _REG_ACCEL_XOUT, 14)

            ax = _to_signed((raw[0]  << 8) | raw[1])  / _ACCEL_SCALE
            ay = _to_signed((raw[2]  << 8) | raw[3])  / _ACCEL_SCALE
            az = _to_signed((raw[4]  << 8) | raw[5])  / _ACCEL_SCALE
            tr = _to_signed((raw[6]  << 8) | raw[7])
            gx = _to_signed((raw[8]  << 8) | raw[9])  / _GYRO_SCALE
            gy = _to_signed((raw[10] << 8) | raw[11]) / _GYRO_SCALE
            gz = _to_signed((raw[12] << 8) | raw[13]) / _GYRO_SCALE
            temp_c = (tr / 340.0) + 36.53
            self._error_count = 0  # başarılı okumada sayacı sıfırla

            return {
                "timestamp": time.time(),
                "ax": ax, "ay": ay, "az": az,
                "gx": gx, "gy": gy, "gz": gz,
                "temp_c": temp_c,
            }
        except (IOError, OSError) as exc:
            self._error_count = getattr(self, "_error_count", 0) + 1
            self._logger.warning(f"IMU okuma hatası: {exc} (art arda {self._error_count})")
            # 5 art arda hata → I2C bus'ı yeniden başlat
            if self._error_count >= 5:
                self._logger.warning("IMU bus yeniden başlatılıyor...")
                self._recover_bus()
            return None

    def _recover_bus(self):
        """I2C bus kapanıp yeniden açılarak bağlantı yenilenir."""
        try:
            if self._bus:
                self._bus.close()
        except Exception:
            pass
        try:
            time.sleep(0.1)
            self._bus = smbus2.SMBus(1)
            self._bus.write_byte_data(self._addr, _REG_PWR_MGMT_1, 0x00)
            time.sleep(0.05)
            self._error_count = 0
            self._logger.info("IMU bus yeniden başlatıldı.")
        except Exception as exc:
            self._logger.error(f"IMU bus kurtarma başarısız: {exc}")
            self._initialized = False

    def compute_magnitude(self, ax: float, ay: float, az: float) -> float:
        """Hareketsiz durumda ~0'a yakın olan ivme büyüklüğü."""
        mag = math.sqrt(ax * ax + ay * ay + az * az)
        return abs(mag - 1.0)

    def set_sample_rate(self, hz: int):
        if self._bus is None:
            return
        divider = max(0, min(255, int(8000 / hz) - 1))
        try:
            self._bus.write_byte_data(self._addr, _REG_SMPLRT_DIV, divider)
        except Exception as exc:
            self._logger.warning(f"Sample rate ayarlanamadı: {exc}")

    def cleanup(self):
        if self._bus is not None:
            try:
                self._bus.close()
            except Exception:
                pass
            self._bus = None
        self._initialized = False
        self._logger.info("IMU kapatıldı.")
