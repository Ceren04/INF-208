"""
tools/mock_drivers.py — Simüle Edilmiş Donanım Sürücüleri
==========================================================
Gerçek donanım olmadan tüm yazılım katmanını test etmek için
gerçekçi sensör verisi üreten mock sürücüler.

IMU: Sakin baseline + periyodik hareket darbesi simülasyonu
LED: Terminal'de renkli ASCII çıktısı
Reed: Manuel toggle ile tamper simülasyonu

Kullanım:
  from tools.mock_drivers import MockIMU, MockLED, MockReed, MockPAM8403
  veya:
  python3 -m tools.mock_drivers   (standalone demo)

ÇALIŞTIĞI YER: Raspberry Pi 3B ve PC
"""

import time
import math
import random
import threading
import logging
from typing import Optional, Callable

logger = logging.getLogger(__name__)

# ANSI renk kodları (terminal çıktısı için)
_RED    = "\033[91m"
_YELLOW = "\033[93m"
_GREEN  = "\033[92m"
_BLUE   = "\033[94m"
_RESET  = "\033[0m"
_BOLD   = "\033[1m"


class MockIMU:
    """
    MPU-6050 simülatörü.
    Sakin baseline gürültüsü + isteğe bağlı hareket darbeleri üretir.
    """

    def __init__(self, noise_std: float = 0.02, gravity: float = 1.0):
        self._noise_std = noise_std
        self._gravity = gravity
        self._initialized = False
        self._motion_until: float = 0.0
        self._motion_level: float = 0.0
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        self._initialized = True
        logger.info("[MOCK] IMU başlatıldı (simülasyon modu)")
        return True

    def read(self) -> Optional[dict]:
        if not self._initialized:
            return None

        now = time.time()
        noise = lambda: random.gauss(0, self._noise_std)

        with self._lock:
            motion = self._motion_level if now < self._motion_until else 0.0

        az = self._gravity + noise() + motion * random.choice([-1, 1])
        ax = noise() + motion * random.gauss(0, 0.5)
        ay = noise() + motion * random.gauss(0, 0.5)

        return {
            "timestamp": now,
            "ax": ax, "ay": ay, "az": az,
            "gx": random.gauss(0, 1.0),
            "gy": random.gauss(0, 1.0),
            "gz": random.gauss(0, 1.0),
            "temp_c": random.gauss(35.0, 0.5),
        }

    def compute_magnitude(self, ax: float, ay: float, az: float) -> float:
        mag = math.sqrt(ax * ax + ay * ay + az * az)
        return abs(mag - 1.0)

    def simulate_motion(self, level: float = 0.5, duration_s: float = 2.0):
        """Hareket simülasyonu başlat (0.0–2.0 arası level)."""
        with self._lock:
            self._motion_level = level
            self._motion_until = time.time() + duration_s
        logger.info(f"[MOCK] Hareket simülasyonu: level={level:.1f}g, süre={duration_s}s")

    def cleanup(self):
        self._initialized = False
        logger.info("[MOCK] IMU kapatıldı")


class MockLED:
    """
    LED simülatörü — terminal'de renkli ASCII çıktısı üretir.
    """

    _COLOR_MAP = {
        5:  (_RED,    "●", "KIRMIZI"),
        6:  (_YELLOW, "●", "SARI"),
        13: (_GREEN,  "●", "YEŞİL"),
    }

    def __init__(self):
        self._states = {5: False, 6: False, 13: False}
        self._blink_threads = {}
        self._stop_events = {5: threading.Event(), 6: threading.Event(), 13: threading.Event()}
        self._initialized = False
        self._current_pattern = "—"

    def initialize(self) -> bool:
        self._initialized = True
        logger.info("[MOCK] LED sürücüsü başlatıldı")
        return True

    def _print_state(self):
        parts = []
        for pin, (color, sym, name) in self._COLOR_MAP.items():
            if self._states[pin]:
                parts.append(f"{color}{sym} {name}{_RESET}")
            else:
                parts.append(f"\033[90m○ {name}{_RESET}")
        print(f"\r[LED] {' | '.join(parts)}  [{self._current_pattern}]", end="", flush=True)

    def set(self, color_val: int, state: bool):
        self._stop_blink(color_val)
        self._states[color_val] = state
        self._print_state()

    def all_off(self):
        for pin in self._states:
            self._stop_blink(pin)
            self._states[pin] = False
        self._print_state()

    def blink(self, color_val: int, hz: float = 1.0, duration_s: Optional[float] = None):
        self._stop_blink(color_val)
        self._stop_events[color_val].clear()
        t = threading.Thread(
            target=self._blink_loop,
            args=(color_val, hz, duration_s),
            daemon=True,
        )
        self._blink_threads[color_val] = t
        t.start()

    def _blink_loop(self, color_val: int, hz: float, duration_s: Optional[float]):
        half = 1.0 / (2.0 * hz)
        start = time.monotonic()
        stop = self._stop_events[color_val]
        while not stop.is_set():
            if duration_s and (time.monotonic() - start) >= duration_s:
                break
            self._states[color_val] = True
            self._print_state()
            if stop.wait(half):
                break
            self._states[color_val] = False
            self._print_state()
            stop.wait(half)
        self._states[color_val] = False
        self._print_state()

    def set_fsm_pattern(self, fsm_state: str):
        self._current_pattern = fsm_state
        self.all_off()
        if fsm_state == "DISARMED":
            pass
        elif fsm_state == "ARMED":
            self.blink(13, hz=0.5)          # yeşil yavaş
        elif fsm_state == "PRE_ALARM":
            self.blink(6, hz=4.0)           # sarı hızlı
        elif fsm_state == "ALARM":
            self.blink(5, hz=10.0)          # kırmızı rapid
        elif fsm_state == "RIDE":
            self.set(13, True)              # yeşil sabit
        elif fsm_state == "TAMPER":
            self.blink(5,  hz=10.0)
            self.blink(6,  hz=10.0)

    def _stop_blink(self, color_val: int):
        self._stop_events[color_val].set()
        t = self._blink_threads.get(color_val)
        if t and t.is_alive():
            t.join(timeout=0.5)
        self._stop_events[color_val].clear()
        self._blink_threads[color_val] = None

    def cleanup(self):
        self.all_off()
        print()
        logger.info("[MOCK] LED kapatıldı")


class MockReed:
    """
    Reed switch simülatörü.
    simulate_tamper() ile kutu açma/kapama simüle edilir.
    """

    def __init__(self):
        self._is_open = False
        self._on_open_cb:  Optional[Callable] = None
        self._on_close_cb: Optional[Callable] = None
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        logger.info("[MOCK] Reed switch başlatıldı")
        return True

    def read(self) -> dict:
        return {"timestamp": time.time(), "is_open": self._is_open, "is_tamper": self._is_open}

    def on_open(self, callback: Callable):
        self._on_open_cb = callback

    def on_close(self, callback: Callable):
        self._on_close_cb = callback

    def is_tamper(self) -> bool:
        return self._is_open

    def simulate_tamper(self, open_it: bool = True):
        """Kutu açma (True) veya kapama (False) simülasyonu."""
        self._is_open = open_it
        state = "AÇILDI (TAMPER!)" if open_it else "kapandı"
        logger.info(f"[MOCK] Reed switch {state}")
        if open_it and self._on_open_cb:
            self._on_open_cb()
        elif not open_it and self._on_close_cb:
            self._on_close_cb()

    def cleanup(self):
        self._initialized = False
        logger.info("[MOCK] Reed switch kapatıldı")


class MockPAM8403:
    """PAM8403 ses simülatörü — terminal'de log üretir."""

    def __init__(self):
        self._is_active = False
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        logger.info("[MOCK] PAM8403 ses başlatıldı")
        return True

    def beep(self, frequency_hz: int = 1000, duration_ms: int = 200):
        print(f"\r[SES] 🔔 BİP — {frequency_hz}Hz, {duration_ms}ms", flush=True)
        time.sleep(duration_ms / 1000.0)

    def beep_pattern(self, count: int, frequency_hz: int = 1000,
                     on_ms: int = 200, off_ms: int = 150):
        for i in range(count):
            self.beep(frequency_hz, on_ms)
            time.sleep(off_ms / 1000.0)

    def start_alarm(self):
        if self._is_active:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._siren_loop, daemon=True)
        self._thread.start()
        self._is_active = True
        print("\r[SES] 🚨 ALARM SİRENİ BAŞLADI", flush=True)

    def _siren_loop(self):
        chars = ["🔊", "🔉", "🔊", "🔉"]
        i = 0
        while not self._stop_event.is_set():
            print(f"\r[SES] {chars[i % 4]} SİREN çalıyor...", end="", flush=True)
            i += 1
            self._stop_event.wait(0.4)
        print("\r[SES] Siren durdu.          ", flush=True)

    def stop_alarm(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._is_active = False

    def is_alarming(self) -> bool:
        return self._is_active

    def cleanup(self):
        self.stop_alarm()
        logger.info("[MOCK] PAM8403 kapatıldı")


class MockDHT:
    """DHT22 simülatörü."""

    def initialize(self) -> bool:
        logger.info("[MOCK] DHT22 başlatıldı")
        return True

    def read(self) -> dict:
        return {
            "temp_c":    random.gauss(22.5, 0.3),
            "humidity":  random.gauss(55.0, 2.0),
            "cpu_temp_c": random.gauss(45.0, 1.0),
        }

    def cleanup(self):
        pass


class MockINA219:
    """INA219 güç ölçüm simülatörü."""

    def __init__(self):
        self._start = time.time()

    def initialize(self) -> bool:
        logger.info("[MOCK] INA219 başlatıldı")
        return True

    def read(self) -> dict:
        # Pil yavaş boşalıyor
        elapsed = (time.time() - self._start) / 3600
        pct = max(0.0, 100.0 - elapsed * 15)
        return {
            "voltage_v":    5.05 - (100 - pct) * 0.005,
            "current_ma":   380 + random.gauss(0, 10),
            "power_mw":     1920 + random.gauss(0, 50),
            "battery_pct":  pct,
        }

    def cleanup(self):
        pass


# ── Standalone demo ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/sena/veloguard")

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")

    from firmware.fsm import FSM, Event
    from firmware.shared_state import SharedState
    from firmware.motion_detector import MotionDetector
    from firmware.algorithms.kalman import KalmanFilter1D

    print(f"\n{_BOLD}=== VeloGuard Mock Sürücü Demo ==={_RESET}\n")

    fsm   = FSM()
    state = SharedState()
    md    = MotionDetector()
    imu   = MockIMU()
    led   = MockLED()
    reed  = MockReed()
    sound = MockPAM8403()

    imu.initialize()
    led.initialize()
    reed.initialize()
    sound.initialize()

    # FSM callback → LED
    fsm.register_state_change_callback(
        lambda s, t: led.set_fsm_pattern("TAMPER" if t else s.name)
    )

    kf = KalmanFilter1D()

    print("Senaryo: DISARMED → ARM → hareket → PRE_ALARM → şiddetli hareket → ALARM → DISARM\n")
    time.sleep(1)

    # 1. ARM
    print(f"\n{_BLUE}[1] ARM komutu gönderiliyor...{_RESET}")
    fsm.handle_event(Event.ARM)
    time.sleep(2)

    # 2. Hafif hareket → PRE_ALARM
    print(f"\n{_YELLOW}[2] Hafif hareket simülasyonu (0.4g)...{_RESET}")
    imu.simulate_motion(level=0.4, duration_s=3.0)
    for _ in range(30):
        d = imu.read()
        if d:
            mag = imu.compute_magnitude(d["ax"], d["ay"], d["az"])
            filtered = kf.update(mag)
            level = md.detect(mag)
            md.update_baseline(mag, fsm.get_state().name)
            state.update_imu(d["ax"], d["ay"], d["az"], mag, filtered)
            from firmware.motion_detector import MotionLevel
            if level == MotionLevel.HIGH:
                state.push_event(Event.MOTION_HIGH)
            elif level == MotionLevel.LOW:
                state.push_event(Event.MOTION_LOW)
            ev = state.pop_event(timeout=0.01)
            if ev:
                fsm.handle_event(ev)
        time.sleep(0.1)

    # 3. Şiddetli hareket → ALARM
    print(f"\n{_RED}[3] Şiddetli hareket simülasyonu (1.5g)!{_RESET}")
    imu.simulate_motion(level=1.5, duration_s=2.0)
    for _ in range(20):
        d = imu.read()
        if d:
            mag = imu.compute_magnitude(d["ax"], d["ay"], d["az"])
            filtered = kf.update(mag)
            level = md.detect(mag)
            from firmware.motion_detector import MotionLevel
            if level == MotionLevel.HIGH:
                state.push_event(Event.MOTION_HIGH)
            ev = state.pop_event(timeout=0.01)
            if ev:
                fsm.handle_event(ev)
                if fsm.get_state().name == "ALARM":
                    sound.start_alarm()
        time.sleep(0.1)

    time.sleep(2)

    # 4. DISARM
    print(f"\n{_GREEN}[4] DISARM...{_RESET}")
    sound.stop_alarm()
    fsm.handle_event(Event.DISARM)
    time.sleep(1)

    # 5. Tamper
    print(f"\n{_RED}[5] ARM + TAMPER simülasyonu...{_RESET}")
    fsm.handle_event(Event.ARM)
    time.sleep(1)
    reed.simulate_tamper(True)
    state.push_event(Event.TAMPER_OPEN)
    ev = state.pop_event(timeout=0.1)
    if ev:
        fsm.handle_event(ev)
        sound.start_alarm()
    time.sleep(2)
    sound.stop_alarm()
    fsm.handle_event(Event.DISARM)

    print(f"\n\n{_GREEN}{_BOLD}=== Demo tamamlandı ==={_RESET}")
    led.cleanup()
    sound.cleanup()
