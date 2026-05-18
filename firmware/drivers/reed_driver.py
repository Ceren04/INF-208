"""
firmware/drivers/reed_driver.py — KY-021 Reed Switch Sürücüsü
gpiozero kullanır — RPi.GPIO'nun edge detection sorununu bypass eder.
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import logging
from typing import Callable, Optional
from firmware.drivers.base_sensor import BaseSensor
from firmware.config import Pins

logger = logging.getLogger(__name__)


class ReedDriver(BaseSensor):
    def __init__(self):
        super().__init__("ReedSwitch")
        self._pin = Pins.REED_SWITCH
        self._button = None
        self._on_open_cb:  Optional[Callable] = None
        self._on_close_cb: Optional[Callable] = None
        self._initialized = False

    def initialize(self) -> bool:
        try:
            from gpiozero import Button  # type: ignore
            # pull_up=True → mıknatıs yakında = kapalı (LOW), uzakta = açık (HIGH=tamper)
            self._button = Button(self._pin, pull_up=True, bounce_time=0.05)
            self._button.when_released = self._on_released   # mıknatıs uzaklaştı → TAMPER
            self._button.when_pressed  = self._on_pressed    # mıknatıs yaklaştı  → normal
            self._initialized = True
            state = "AÇIK (TAMPER!)" if self._button.is_active is False else "kapalı"
            logger.info(f"Reed switch başlatıldı — GPIO{self._pin} — durum: {state}")
            return True
        except Exception as exc:
            logger.error(f"Reed switch başlatılamadı: {exc}")
            return False

    def _on_released(self):
        """Mıknatıs uzaklaştı → kutu açıldı → TAMPER."""
        logger.warning("Reed switch AÇILDI — TAMPER!")
        if self._on_open_cb:
            try:
                self._on_open_cb()
            except Exception as exc:
                logger.error(f"Reed open callback hatası: {exc}")

    def _on_pressed(self):
        """Mıknatıs yaklaştı → kutu kapandı."""
        logger.info("Reed switch kapandı.")
        if self._on_close_cb:
            try:
                self._on_close_cb()
            except Exception as exc:
                logger.error(f"Reed close callback hatası: {exc}")

    def read(self) -> dict:
        if self._button is None:
            return {"timestamp": time.time(), "is_open": False, "is_tamper": False}
        # gpiozero Button: is_active=True → basılı (mıknatıs yakında, devre kapalı)
        is_open = not self._button.is_active
        return {"timestamp": time.time(), "is_open": is_open, "is_tamper": is_open}

    def on_open(self, callback: Callable):
        self._on_open_cb = callback

    def on_close(self, callback: Callable):
        self._on_close_cb = callback

    def is_tamper(self) -> bool:
        if self._button is None:
            return False
        return not self._button.is_active

    def cleanup(self):
        if self._button is not None:
            try:
                self._button.close()
            except Exception:
                pass
            self._button = None
        self._initialized = False
        logger.info("Reed switch kapatıldı.")
