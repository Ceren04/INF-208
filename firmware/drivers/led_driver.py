"""
firmware/drivers/led_driver.py — LED Sürücüsü (Kırmızı / Sarı / Yeşil)
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import threading
import logging
from enum import Enum
from typing import Optional, Dict
import RPi.GPIO as GPIO
from firmware.config import Pins

logger = logging.getLogger(__name__)


class LEDColor(Enum):
    RED    = Pins.LED_RED
    YELLOW = Pins.LED_YELLOW
    GREEN  = Pins.LED_GREEN


class LEDDriver:
    def __init__(self):
        self._pins = [Pins.LED_RED, Pins.LED_YELLOW, Pins.LED_GREEN]
        self._blink_threads: Dict[int, Optional[threading.Thread]] = {p: None for p in self._pins}
        self._stop_events:   Dict[int, threading.Event]            = {p: threading.Event() for p in self._pins}
        self._initialized = False

    def initialize(self) -> bool:
        try:
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)
            for pin in self._pins:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)
            self._initialized = True
            logger.info("LED sürücüsü başlatıldı.")
            return True
        except Exception as exc:
            logger.error(f"LED başlatılamadı: {exc}")
            return False

    def set(self, color: LEDColor, state: bool):
        self._stop_blink(color)
        try:
            GPIO.output(color.value, GPIO.HIGH if state else GPIO.LOW)
        except Exception as exc:
            logger.warning(f"LED set hatası: {exc}")

    def all_off(self):
        for color in LEDColor:
            self._stop_blink(color)
        for pin in self._pins:
            try:
                GPIO.output(pin, GPIO.LOW)
            except Exception:
                pass

    def blink(self, color: LEDColor, hz: float = 1.0, duration_s: Optional[float] = None):
        self._stop_blink(color)
        self._stop_events[color.value].clear()
        t = threading.Thread(
            target=self._blink_loop,
            args=(color, hz, duration_s),
            daemon=True,
        )
        self._blink_threads[color.value] = t
        t.start()

    def _blink_loop(self, color: LEDColor, hz: float, duration_s: Optional[float]):
        half = 1.0 / (2.0 * hz)
        start = time.monotonic()
        stop = self._stop_events[color.value]
        pin = color.value
        try:
            while not stop.is_set():
                if duration_s and (time.monotonic() - start) >= duration_s:
                    break
                GPIO.output(pin, GPIO.HIGH)
                if stop.wait(half):
                    break
                GPIO.output(pin, GPIO.LOW)
                stop.wait(half)
        except Exception as exc:
            logger.warning(f"Blink loop hatası ({color.name}): {exc}")
        finally:
            try:
                GPIO.output(pin, GPIO.LOW)
            except Exception:
                pass

    def set_fsm_pattern(self, fsm_state: str):
        self.all_off()
        if fsm_state == "DISARMED":
            pass
        elif fsm_state == "ARMED":
            self.blink(LEDColor.GREEN, hz=0.5)
        elif fsm_state == "PRE_ALARM":
            self.blink(LEDColor.YELLOW, hz=4.0)
        elif fsm_state == "ALARM":
            self.blink(LEDColor.RED, hz=10.0)
        elif fsm_state == "RIDE":
            self.set(LEDColor.GREEN, True)
        elif fsm_state == "TAMPER":
            self.blink(LEDColor.RED,    hz=10.0)
            self.blink(LEDColor.YELLOW, hz=10.0)

    def _stop_blink(self, color: LEDColor):
        self._stop_events[color.value].set()
        t = self._blink_threads.get(color.value)
        if t and t.is_alive():
            t.join(timeout=1.0)
        self._stop_events[color.value].clear()
        self._blink_threads[color.value] = None

    def cleanup(self):
        self.all_off()
        try:
            GPIO.cleanup(self._pins)
        except Exception:
            pass
        logger.info("LED sürücüsü kapatıldı.")
