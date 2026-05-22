"""
firmware/drivers/pam8403_driver.py — PAM8403 + Hoparlör Ses Sürücüsü
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import threading
import logging
from typing import Optional
import RPi.GPIO as GPIO
from firmware.config import Pins, SoundConfig

logger = logging.getLogger(__name__)


class PAM8403Driver:
    def __init__(self):
        self._pin = Pins.PAM8403_PWM
        self._pwm: Optional[GPIO.PWM] = None
        self._is_active = False
        self._alarm_thread: Optional[threading.Thread] = None
        self._stop_alarm_event = threading.Event()
        self._beep_thread: Optional[threading.Thread] = None
        self._stop_beep_event = threading.Event()
        self._initialized = False

    def initialize(self) -> bool:
        try:
            if GPIO.getmode() is None:
                GPIO.setmode(GPIO.BCM)
            GPIO.setup(self._pin, GPIO.OUT)
            self._pwm = GPIO.PWM(self._pin, SoundConfig.PRE_ALARM_FREQ_HZ)
            self._pwm.start(0)
            self._initialized = True
            logger.info("PAM8403 ses sürücüsü başlatıldı.")
            return True
        except Exception as exc:
            logger.error(f"PAM8403 başlatılamadı: {exc}")
            return False

    def beep(self, frequency_hz: int = SoundConfig.PRE_ALARM_FREQ_HZ,
             duration_ms: int = 200):
        if not self._initialized or self._pwm is None:
            return
        try:
            self._pwm.ChangeFrequency(frequency_hz)
            self._pwm.ChangeDutyCycle(SoundConfig.PWM_DUTY_CYCLE)
            time.sleep(duration_ms / 1000.0)
            self._pwm.ChangeDutyCycle(0)
        except Exception as exc:
            logger.warning(f"Beep hatası: {exc}")

    def beep_pattern(self, count: int,
                     frequency_hz: int = SoundConfig.PRE_ALARM_FREQ_HZ,
                     on_ms: int = 200, off_ms: int = 150):
        for _ in range(count):
            if self._stop_beep_event.is_set():
                break
            self.beep(frequency_hz, on_ms)
            if self._stop_beep_event.is_set():
                break
            time.sleep(off_ms / 1000.0)

    def start_beep_pattern_async(self, count: int, frequency_hz: int = SoundConfig.PRE_ALARM_FREQ_HZ,
                                 on_ms: int = 200, off_ms: int = 150):
        """Start a tracked beep pattern for PRE_ALARM. Can be stopped with stop_beep_pattern()."""
        self._stop_beep_event.clear()
        self._beep_thread = threading.Thread(
            target=self.beep_pattern,
            args=(count, frequency_hz, on_ms, off_ms),
            daemon=True,
            name="BeepPattern"
        )
        self._beep_thread.start()

    def stop_beep_pattern(self):
        self._stop_beep_event.set()
        if self._beep_thread and self._beep_thread.is_alive():
            try:
                self._beep_thread.join(timeout=0.5)
            except Exception:
                pass
        self._beep_thread = None
        if self._pwm:
            try:
                self._pwm.ChangeDutyCycle(0)
            except Exception:
                pass

    def start_alarm(self):
        if self._is_active:
            return
        self._stop_alarm_event.clear()
        self._alarm_thread = threading.Thread(target=self._siren_loop, daemon=True)
        self._alarm_thread.start()
        self._is_active = True
        logger.info("Alarm sireni başlatıldı.")

    def _siren_loop(self):
        while not self._stop_alarm_event.is_set():
            self.sweep_tone(SoundConfig.ALARM_FREQ_LOW_HZ,
                            SoundConfig.ALARM_FREQ_HIGH_HZ, 0.4)
            if self._stop_alarm_event.is_set():
                break
            self.sweep_tone(SoundConfig.ALARM_FREQ_HIGH_HZ,
                            SoundConfig.ALARM_FREQ_LOW_HZ, 0.4)
        if self._pwm:
            try:
                self._pwm.ChangeDutyCycle(0)
            except Exception:
                pass

    def sweep_tone(self, freq_start: int = SoundConfig.ALARM_FREQ_LOW_HZ,
                   freq_end: int = SoundConfig.ALARM_FREQ_HIGH_HZ,
                   duration_s: float = 0.5):
        if not self._initialized or self._pwm is None:
            return
        step = SoundConfig.ALARM_SWEEP_STEP_HZ
        steps = max(1, abs(freq_end - freq_start) // step)
        delay = duration_s / steps
        direction = 1 if freq_end > freq_start else -1
        freq = freq_start
        try:
            for _ in range(steps):
                if self._stop_alarm_event.is_set():
                    break
                self._pwm.ChangeFrequency(max(1, freq))
                self._pwm.ChangeDutyCycle(SoundConfig.PWM_DUTY_CYCLE)
                time.sleep(delay)
                freq += direction * step
        except Exception as exc:
            logger.warning(f"Sweep hatası: {exc}")
        finally:
            try:
                if self._pwm:
                    self._pwm.ChangeDutyCycle(0)
            except Exception:
                pass

    def stop_alarm(self):
        # Signal stop for alarm loop and any beep pattern
        self._stop_alarm_event.set()
        self.stop_beep_pattern()
        if self._alarm_thread and self._alarm_thread.is_alive():
            try:
                self._alarm_thread.join(timeout=0.5)
            except Exception:
                pass
        if self._pwm:
            try:
                self._pwm.ChangeDutyCycle(0)
            except Exception:
                pass
        self._is_active = False
        logger.info("Alarm durduruldu.")

    def is_alarming(self) -> bool:
        return self._is_active

    def cleanup(self):
        self.stop_alarm()
        if self._pwm:
            try:
                self._pwm.stop()
            except Exception:
                pass
        try:
            GPIO.cleanup(self._pin)
        except Exception:
            pass
        logger.info("PAM8403 kapatıldı.")
