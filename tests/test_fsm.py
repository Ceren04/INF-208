"""
tests/test_fsm.py — FSM Birim Testleri
=======================================
Tüm FSM geçişlerini donanım olmadan test eder.

Çalıştırma: pytest tests/test_fsm.py -v

ÇALIŞTIĞI YER: PC
"""

import pytest
from firmware.fsm import FSM, State, Event


class TestFSMBasicTransitions:
    """Temel durum geçiş testleri."""

    def setup_method(self):
        """Her test öncesi taze FSM oluştur."""
        self.fsm = FSM()

    def test_initial_state_is_disarmed(self):
        """
        Yapması gerekenler:
        - FSM() oluşturulunca başlangıç durumu DISARMED olmalı
        - assert fsm.get_state() == State.DISARMED
        """
        pass

    def test_arm_transitions_to_armed(self):
        """
        Yapması gerekenler:
        - ARM eventi gönder
        - get_state() == State.ARMED olmalı
        """
        pass

    def test_disarm_from_armed(self):
        """
        Yapması gerekenler:
        - ARM → DISARM
        - get_state() == State.DISARMED olmalı
        """
        pass

    def test_motion_low_triggers_pre_alarm(self):
        """
        Yapması gerekenler:
        - ARM → MOTION_LOW
        - get_state() == State.PRE_ALARM olmalı
        """
        pass

    def test_motion_high_from_armed_triggers_alarm(self):
        """
        Yapması gerekenler:
        - ARM → MOTION_HIGH
        - get_state() == State.ALARM olmalı
        """
        pass

    def test_motion_high_from_pre_alarm_triggers_alarm(self):
        """
        Yapması gerekenler:
        - ARM → MOTION_LOW → MOTION_HIGH
        - get_state() == State.ALARM olmalı
        """
        pass

    def test_pre_alarm_timeout_returns_to_armed(self):
        """
        Yapması gerekenler:
        - ARM → MOTION_LOW → (bekle > PRE_ALARM_TIMEOUT_S) → otomatik ARMED
        - NOT: Timer'ın dolmasını beklemek yerine TIMEOUT_PRE_ALARM eventini elle gönder
        """
        pass

    def test_ride_mode(self):
        """
        Yapması gerekenler:
        - ARM → RIDE_START → get_state() == State.RIDE
        - RIDE'da MOTION_HIGH göndermek ALARM tetiklemez
        - RIDE_END → get_state() == State.ARMED
        """
        pass

    def test_tamper_from_any_state_triggers_alarm(self):
        """
        Yapması gerekenler:
        - DISARMED'dan TAMPER_OPEN → ALARM ve is_tamper() True
        - ARMED'dan TAMPER_OPEN → ALARM ve is_tamper() True
        """
        pass

    def test_disarm_does_not_clear_tamper(self):
        """
        Yapması gerekenler:
        - ARM → TAMPER_OPEN → DISARM gönder
        - is_tamper() hâlâ True olmalı (tamper sadece clear_tamper() ile kapanır)
        """
        pass

    def test_invalid_transition_returns_false(self):
        """
        Yapması gerekenler:
        - DISARMED'da MOTION_HIGH gönder (geçersiz geçiş)
        - handle_event() False döndürmeli
        - Durum DISARMED kalmalı
        """
        pass


class TestFSMCallbacks:
    """Durum değişim callback testleri."""

    def test_callback_called_on_state_change(self):
        """
        Yapması gerekenler:
        - callback_results = [] listesi oluştur
        - fsm.register_state_change_callback(lambda s, t: callback_results.append(s))
        - ARM eventi gönder
        - callback_results[0] == State.ARMED olmalı
        """
        pass

    def test_multiple_callbacks_all_called(self):
        """
        Yapması gerekenler:
        - 3 farklı callback kaydet
        - ARM eventi gönder
        - 3 callback da çağrılmış olmalı
        """
        pass

    def test_callback_exception_does_not_crash_fsm(self):
        """
        Yapması gerekenler:
        - Hata fırlatan bir callback kaydet
        - ARM eventi gönder → FSM çökmemeli
        - Durum yine de ARMED olmalı
        """
        pass
