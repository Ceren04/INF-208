"""
tests/test_fsm.py — FSM Birim Testleri
========================================
VeloGuard'ın 5-durumlu FSM'ini kapsamlı şekilde test eder.
Tüm geçişler, timeout davranışları ve callback mekanizması test edilir.

Çalıştırma:
  cd ~/veloguard
  pytest tests/test_fsm.py -v

ÇALIŞTIĞI YER: PC ve Pi (donanım gerektirmez)
"""

import time
import threading
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from firmware.fsm import FSM, State, Event


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def fsm():
    """Her test için temiz bir FSM örneği."""
    return FSM()


@pytest.fixture
def armed_fsm(fsm):
    """ARMED durumunda başlayan FSM."""
    fsm.handle_event(Event.ARM)
    time.sleep(0.05)  # ARM_DELAY'i atla
    return fsm


# ── Başlangıç durumu ──────────────────────────────────────────────────────────

class TestInitialState:
    def test_starts_disarmed(self, fsm):
        assert fsm.get_state() == State.DISARMED

    def test_not_tamper_initially(self, fsm):
        assert fsm.is_tamper() is False

    def test_status_dict_has_required_keys(self, fsm):
        d = fsm.get_status_dict()
        assert "state" in d
        assert "is_tamper" in d
        assert "state_duration_s" in d
        assert "timestamp" in d

    def test_status_dict_state_is_string(self, fsm):
        assert fsm.get_status_dict()["state"] == "DISARMED"


# ── Temel geçişler ────────────────────────────────────────────────────────────

class TestBasicTransitions:
    def test_disarmed_to_armed(self, fsm):
        result = fsm.handle_event(Event.ARM)
        assert result is True
        assert fsm.get_state() == State.ARMED

    def test_armed_to_disarmed(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm.handle_event(Event.DISARM)
        assert fsm.get_state() == State.DISARMED

    def test_armed_to_ride(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm.handle_event(Event.RIDE_START)
        assert fsm.get_state() == State.RIDE

    def test_ride_to_armed(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm.handle_event(Event.RIDE_START)
        fsm.handle_event(Event.RIDE_END)
        assert fsm.get_state() == State.ARMED

    def test_ride_to_disarmed(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm.handle_event(Event.RIDE_START)
        fsm.handle_event(Event.DISARM)
        assert fsm.get_state() == State.DISARMED

    def test_alarm_to_disarmed(self, fsm):
        fsm.handle_event(Event.ARM)
        # ARM_DELAY geçmesini bekle
        time.sleep(0.02)
        fsm._arm_suppress_until = 0  # suppress'i bypass et
        fsm.handle_event(Event.MOTION_HIGH)
        assert fsm.get_state() == State.ALARM
        fsm.handle_event(Event.DISARM)
        assert fsm.get_state() == State.DISARMED


# ── Motion event geçişleri ────────────────────────────────────────────────────

class TestMotionTransitions:
    def test_armed_motion_low_to_pre_alarm(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm._arm_suppress_until = 0
        result = fsm.handle_event(Event.MOTION_LOW)
        assert result is True
        assert fsm.get_state() == State.PRE_ALARM

    def test_armed_motion_high_to_alarm(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm._arm_suppress_until = 0
        fsm.handle_event(Event.MOTION_HIGH)
        assert fsm.get_state() == State.ALARM

    def test_pre_alarm_motion_high_to_alarm(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm._arm_suppress_until = 0
        fsm.handle_event(Event.MOTION_LOW)
        assert fsm.get_state() == State.PRE_ALARM
        fsm.handle_event(Event.MOTION_HIGH)
        assert fsm.get_state() == State.ALARM

    def test_motion_ignored_when_disarmed(self, fsm):
        result = fsm.handle_event(Event.MOTION_HIGH)
        assert result is False
        assert fsm.get_state() == State.DISARMED

    def test_motion_ignored_during_arm_delay(self, fsm):
        fsm.handle_event(Event.ARM)
        # suppress süresi dolmadan
        result = fsm.handle_event(Event.MOTION_HIGH)
        assert result is False
        assert fsm.get_state() == State.ARMED


# ── TAMPER (orthogonal durum) ─────────────────────────────────────────────────

class TestTamper:
    def test_tamper_from_disarmed(self, fsm):
        fsm.handle_event(Event.TAMPER_OPEN)
        assert fsm.get_state() == State.ALARM
        assert fsm.is_tamper() is True

    def test_tamper_from_armed(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm.handle_event(Event.TAMPER_OPEN)
        assert fsm.is_tamper() is True
        assert fsm.get_state() == State.ALARM

    def test_tamper_from_ride(self, fsm):
        fsm.handle_event(Event.ARM)
        fsm.handle_event(Event.RIDE_START)
        fsm.handle_event(Event.TAMPER_OPEN)
        assert fsm.is_tamper() is True


# ── PRE_ALARM timeout ─────────────────────────────────────────────────────────

class TestPreAlarmTimeout:
    def test_pre_alarm_returns_to_armed_after_timeout(self, fsm):
        from firmware.config import FSMConfig
        # Çok kısa timeout için config'i geçici değiştir
        original = FSMConfig.PRE_ALARM_TIMEOUT_S
        FSMConfig.PRE_ALARM_TIMEOUT_S = 0.1
        try:
            fsm2 = FSM()
            fsm2.handle_event(Event.ARM)
            fsm2._arm_suppress_until = 0
            fsm2.handle_event(Event.MOTION_LOW)
            assert fsm2.get_state() == State.PRE_ALARM
            time.sleep(0.3)  # timeout'u bekle
            assert fsm2.get_state() == State.ARMED
        finally:
            FSMConfig.PRE_ALARM_TIMEOUT_S = original


# ── Callback mekanizması ──────────────────────────────────────────────────────

class TestCallbacks:
    def test_callback_called_on_state_change(self, fsm):
        calls = []
        fsm.register_state_change_callback(lambda s, t: calls.append(s))
        fsm.handle_event(Event.ARM)
        assert len(calls) == 1
        assert calls[0] == State.ARMED

    def test_multiple_callbacks(self, fsm):
        a, b = [], []
        fsm.register_state_change_callback(lambda s, t: a.append(s))
        fsm.register_state_change_callback(lambda s, t: b.append(s))
        fsm.handle_event(Event.ARM)
        assert len(a) == 1
        assert len(b) == 1

    def test_callback_exception_doesnt_break_fsm(self, fsm):
        def bad_cb(s, t):
            raise RuntimeError("callback hatası")
        fsm.register_state_change_callback(bad_cb)
        # Hata olsa bile FSM çalışmaya devam etmeli
        fsm.handle_event(Event.ARM)
        assert fsm.get_state() == State.ARMED

    def test_tamper_flag_passed_to_callback(self, fsm):
        tampers = []
        fsm.register_state_change_callback(lambda s, t: tampers.append(t))
        fsm.handle_event(Event.TAMPER_OPEN)
        assert tampers[-1] is True


# ── Thread güvenliği ──────────────────────────────────────────────────────────

class TestThreadSafety:
    def test_concurrent_events(self, fsm):
        """50 thread eşzamanlı event gönderir, crash olmamalı."""
        errors = []

        def worker():
            try:
                for _ in range(10):
                    fsm.handle_event(Event.ARM)
                    fsm.handle_event(Event.DISARM)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(50)]
        for t in threads: t.start()
        for t in threads: t.join()

        assert len(errors) == 0

    def test_get_state_while_transitioning(self, fsm):
        """get_state() geçiş sırasında güvenli çağrılabilmeli."""
        results = []

        def transitioner():
            for _ in range(100):
                fsm.handle_event(Event.ARM)
                fsm.handle_event(Event.DISARM)

        def reader():
            for _ in range(100):
                results.append(fsm.get_state())

        t1 = threading.Thread(target=transitioner)
        t2 = threading.Thread(target=reader)
        t1.start(); t2.start()
        t1.join(); t2.join()

        # Sadece geçerli state değerleri olmalı
        valid = set(State)
        assert all(r in valid for r in results)


# ── get_status_dict ───────────────────────────────────────────────────────────

class TestStatusDict:
    def test_duration_increases_over_time(self, fsm):
        fsm.handle_event(Event.ARM)
        d1 = fsm.get_status_dict()["state_duration_s"]
        time.sleep(0.1)
        d2 = fsm.get_status_dict()["state_duration_s"]
        assert d2 > d1

    def test_state_resets_on_transition(self, fsm):
        fsm.handle_event(Event.ARM)
        time.sleep(0.2)
        fsm.handle_event(Event.DISARM)
        d = fsm.get_status_dict()["state_duration_s"]
        assert d < 0.1  # yeni durumda az süre geçti
