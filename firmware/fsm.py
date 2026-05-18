"""
firmware/fsm.py — VeloGuard Sonlu Durum Makinesi (FSM)
=======================================================
5 ana durum + orthogonal TAMPER durumu.

ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import threading
import logging
from enum import Enum, auto
from typing import Callable, Optional, List
from firmware.config import FSMConfig

logger = logging.getLogger(__name__)


class State(Enum):
    DISARMED  = auto()
    ARMED     = auto()
    PRE_ALARM = auto()
    ALARM     = auto()
    RIDE      = auto()


class Event(Enum):
    ARM               = auto()
    DISARM            = auto()
    RIDE_START        = auto()
    RIDE_END          = auto()
    MOTION_LOW        = auto()
    MOTION_HIGH       = auto()
    TAMPER_OPEN       = auto()
    TAMPER_CLOSE      = auto()
    TIMEOUT_PRE_ALARM = auto()
    BATTERY_LOW       = auto()
    BATTERY_CRITICAL  = auto()
    THERMAL_WARNING   = auto()
    THERMAL_CRITICAL  = auto()


class FSM:
    """VeloGuard'ın merkezi durum makinesi. Thread-safe."""

    def __init__(self):
        self._state = State.DISARMED
        self._is_tamper = False
        self._pre_alarm_timer: Optional[threading.Timer] = None
        self._state_enter_time = time.time()
        self._on_state_change_callbacks: List[Callable] = []
        self._lock = threading.Lock()
        logger.info("FSM başlatıldı — DISARMED")

    def handle_event(self, event: Event) -> bool:
        with self._lock:
            prev = self._state

            # TAMPER her durumda geçerli
            if event == Event.TAMPER_OPEN:
                self._enter_tamper()
                self._notify_state_change()
                return True

            # ARM sonrası bekleme süresi: MOTION eventlerini yoksay
            if event in (Event.MOTION_LOW, Event.MOTION_HIGH):
                suppress_until = getattr(self, "_arm_suppress_until", 0.0)
                if time.time() < suppress_until:
                    remaining = round(suppress_until - time.time(), 2)
                    logger.debug(f"ARM bekleme: {event.name} yoksayıldı ({remaining}s kaldı)")
                    return False

            # Geçiş tablosu
            transition = {
                (State.DISARMED,  Event.ARM):               self._on_enter_armed,
                (State.ARMED,     Event.MOTION_LOW):        self._on_enter_pre_alarm,
                (State.ARMED,     Event.MOTION_HIGH):       self._on_enter_alarm,
                (State.ARMED,     Event.RIDE_START):        self._on_enter_ride,
                (State.ARMED,     Event.DISARM):            self._on_enter_disarmed,
                (State.PRE_ALARM, Event.MOTION_HIGH):       self._on_enter_alarm,
                (State.PRE_ALARM, Event.TIMEOUT_PRE_ALARM): self._on_enter_armed,
                (State.PRE_ALARM, Event.DISARM):            self._on_enter_disarmed,
                (State.ALARM,     Event.DISARM):            self._on_enter_disarmed,
                (State.RIDE,      Event.RIDE_END):          self._on_enter_armed,
                (State.RIDE,      Event.DISARM):            self._on_enter_disarmed,
            }

            action = transition.get((self._state, event))
            if action is None:
                logger.debug(f"Desteklenmeyen geçiş: {self._state.name} + {event.name}")
                return False

            action()
            if self._state != prev:
                self._notify_state_change()
            return True

    # ── Durum giriş metotları ─────────────────────────────────────────────────

    def _on_enter_disarmed(self):
        self._cancel_timer()
        self._state = State.DISARMED
        self._state_enter_time = time.time()
        logger.info("→ DISARMED")

    def _on_enter_armed(self):
        self._cancel_timer()
        self._state = State.ARMED
        self._state_enter_time = time.time()
        self._arm_suppress_until = time.time() + FSMConfig.ARM_DELAY_S
        logger.info(f"→ ARMED (motion {FSMConfig.ARM_DELAY_S}s susturuldu)")

    def _on_enter_pre_alarm(self):
        self._state = State.PRE_ALARM
        self._state_enter_time = time.time()
        self._pre_alarm_timer = threading.Timer(
            FSMConfig.PRE_ALARM_TIMEOUT_S, self._pre_alarm_timeout
        )
        self._pre_alarm_timer.daemon = True
        self._pre_alarm_timer.start()
        logger.info("→ PRE_ALARM (timer başladı)")

    def _on_enter_alarm(self):
        self._cancel_timer()
        self._state = State.ALARM
        self._state_enter_time = time.time()
        logger.warning("→ ALARM!")

    def _on_enter_ride(self):
        self._state = State.RIDE
        self._state_enter_time = time.time()
        logger.info("→ RIDE")

    def _enter_tamper(self):
        self._is_tamper = True
        self._on_enter_alarm()
        logger.warning("→ TAMPER + ALARM!")

    def _pre_alarm_timeout(self):
        with self._lock:
            if self._state == State.PRE_ALARM:
                self._on_enter_armed()
                self._notify_state_change()

    def _cancel_timer(self):
        if self._pre_alarm_timer is not None:
            self._pre_alarm_timer.cancel()
            self._pre_alarm_timer = None

    # ── Callback yönetimi ────────────────────────────────────────────────────

    def register_state_change_callback(self, callback: Callable):
        self._on_state_change_callbacks.append(callback)

    def _notify_state_change(self):
        for cb in self._on_state_change_callbacks:
            try:
                cb(self._state, self._is_tamper)
            except Exception as exc:
                logger.error(f"FSM callback hatası: {exc}")

    # ── Sorgulama metotları ──────────────────────────────────────────────────

    def get_state(self) -> State:
        return self._state

    def is_tamper(self) -> bool:
        return self._is_tamper

    def get_status_dict(self) -> dict:
        return {
            "state":            self._state.name,
            "is_tamper":        self._is_tamper,
            "state_duration_s": round(time.time() - self._state_enter_time, 1),
            "timestamp":        time.time(),
        }

    def clear_tamper(self, password: str) -> bool:
        import hashlib, os
        expected = os.getenv("TAMPER_PASSWORD_HASH", "")
        given = hashlib.sha256(password.encode()).hexdigest()
        if given == expected:
            with self._lock:
                self._is_tamper = False
                self._on_enter_disarmed()
                self._notify_state_change()
            logger.info("Tamper temizlendi.")
            return True
        logger.warning("Tamper temizleme — yanlış parola.")
        return False
