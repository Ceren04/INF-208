"""
firmware/drivers/reed_driver.py — KY-021 Reed Switch Sürücüsü
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import logging
from typing import Callable, Optional
import RPi.GPIO as GPIO
from firmware.drivers.base_sensor import BaseSensor
from firmware.config import Pins

logger = logging.getLogger(__name__)


class ReedDriver(BaseSensor):
    def __init__(self):
        super().__init__("ReedSwitch")
        self._pin = Pins.REED_SWITCH
        self._on_open_callback:  Optional[Callable] = None
        self._on_close_callback: Optional[Callable] = None
        self._last_state: Optional[bool] = None
        self._debounce_ms = 50

    def initialize(self) -> bool:
        try:
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Önceki oturumdan kalma event detection'ı temizle
            try:
                GPIO.remove_event_detect(self._pin)
            except Exception:
                pass
            GPIO.add_event_detect(
                self._pin,
                GPIO.BOTH,
                callback=self._isr_handler,
                bouncetime=self._debounce_ms,
            )
            self._last_state = bool(GPIO.input(self._pin))
            self._initialized = True
            state_str = "AÇIK (TAMPER!)" if self._last_state else "kapalı"
            logger.info(f"Reed switch başlatıldı — GPIO{self._pin} — durum: {state_str}")
            return True
        except Exception as exc:
            logger.error(f"Reed switch başlatılamadı: {exc}")
            return False

    def read(self) -> dict:
        is_open = bool(GPIO.input(self._pin))
        return {
            "timestamp": time.time(),
            "is_open":   is_open,
            "is_tamper": is_open,
        }

    def _isr_handler(self, channel: int):
        try:
            is_open = bool(GPIO.input(self._pin))
            self._last_state = is_open
            if is_open:
                logger.warning("Reed switch AÇILDI — TAMPER!")
                if self._on_open_callback:
                    self._on_open_callback()
            else:
                logger.info("Reed switch kapandı.")
                if self._on_close_callback:
                    self._on_close_callback()
        except Exception as exc:
            logger.error(f"Reed ISR hatası: {exc}")

    def on_open(self, callback: Callable):
        self._on_open_callback = callback

    def on_close(self, callback: Callable):
        self._on_close_callback = callback

    def is_tamper(self) -> bool:
        return bool(GPIO.input(self._pin))

    def cleanup(self):
        try:
            GPIO.remove_event_detect(self._pin)
            GPIO.cleanup(self._pin)
        except Exception:
            pass
        self._initialized = False
        logger.info("Reed switch kapatıldı.")
