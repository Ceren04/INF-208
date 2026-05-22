"""
firmware/main.py — VeloGuard Ana Giriş Noktası
Çalıştırma: sudo python3 -m firmware.main
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import sys
import signal
import logging
import logging.handlers
import time
import os
from firmware.config import LogConfig


def setup_logging():
    log_dir = LogConfig.LOG_DIR
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, LogConfig.LOG_FILE)

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    fh = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=LogConfig.MAX_BYTES,
        backupCount=LogConfig.BACKUP_COUNT,
    )
    fh.setFormatter(fmt)

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(sh)


class VeloGuardApp:
    def __init__(self):
        self._running = False
        self._drivers = {}
        self._fsm = None
        self._shared_state = None
        self._task_manager = None
        self._watchdog = None
        self._web_ui = None
        self._telegram = None
        self._logger = logging.getLogger("veloguard.app")

    def initialize(self) -> bool:
        self._logger.info("VeloGuard başlatılıyor...")

        # SharedState
        from firmware.shared_state import SharedState
        self._shared_state = SharedState()

        # FSM
        from firmware.fsm import FSM
        self._fsm = FSM()

        # Motion Detector
        from firmware.motion_detector import MotionDetector
        motion_detector = MotionDetector()

        # Sürücüler
        drivers_ok = True

        try:
            from firmware.drivers.imu_driver import IMUDriver
            imu = IMUDriver()
            if imu.initialize():
                self._drivers["imu"] = imu
                self._logger.info("✓ IMU hazır")
            else:
                self._logger.warning("✗ IMU başlatılamadı — mock modda")
                self._drivers["imu"] = None
        except Exception as e:
            self._logger.warning(f"✗ IMU: {e}")
            self._drivers["imu"] = None

        try:
            from firmware.drivers.led_driver import LEDDriver
            led = LEDDriver()
            if led.initialize():
                self._drivers["led"] = led
                self._logger.info("✓ LED hazır")
            else:
                self._drivers["led"] = None
        except Exception as e:
            self._logger.warning(f"✗ LED: {e}")
            self._drivers["led"] = None

        try:
            from firmware.drivers.reed_driver import ReedDriver
            reed = ReedDriver()
            if reed.initialize():
                self._drivers["reed"] = reed
                self._logger.info("✓ Reed switch hazır")
            else:
                self._drivers["reed"] = None
        except Exception as e:
            self._logger.warning(f"✗ Reed: {e}")
            self._drivers["reed"] = None

        try:
            from firmware.drivers.pam8403_driver import PAM8403Driver
            sound = PAM8403Driver()
            if sound.initialize():
                self._drivers["sound"] = sound
                self._logger.info("✓ PAM8403 ses hazır")
            else:
                self._drivers["sound"] = None
        except Exception as e:
            self._logger.warning(f"✗ PAM8403: {e}")
            self._drivers["sound"] = None

        # Opsiyonel sürücüler (yoksa None)
        for name, mod, cls in [
            ("dht",    "firmware.drivers.dht_driver",   "DHTDriver"),
            ("ina219", "firmware.drivers.ina219_driver","INA219Driver"),
            ("camera", "firmware.drivers.camera_driver","CameraDriver"),
        ]:
            try:
                import importlib
                m = importlib.import_module(mod)
                drv = getattr(m, cls)()
                if drv.initialize():
                    self._drivers[name] = drv
                    self._logger.info(f"✓ {cls} hazır")
                else:
                    self._drivers[name] = None
            except Exception as e:
                self._logger.warning(f"✗ {cls}: {e}")
                self._drivers[name] = None

        # Telegram
        try:
            from firmware.comm.telegram_bot import TelegramNotifier
            tg = TelegramNotifier()
            if tg.initialize():
                self._telegram = tg
                self._drivers["telegram"] = tg
                self._logger.info("✓ Telegram hazır")
            else:
                self._drivers["telegram"] = None
        except Exception as e:
            self._logger.warning(f"✗ Telegram: {e}")
            self._drivers["telegram"] = None

        self._drivers["motion_detector"] = motion_detector

        # FSM → LED callback
        # NOTE: LED updates are handled centrally by TaskManager._trigger_actuators
        # to avoid double-calls and race conditions. Do not register per-driver callbacks here.

        # Web UI
        try:
            from firmware.comm.web_ui import WebUI
            self._web_ui = WebUI(self._fsm, self._shared_state)
        except Exception as e:
            self._logger.warning(f"✗ WebUI: {e}")
            self._web_ui = None

        # Watchdog
        from firmware.watchdog import Watchdog
        self._watchdog = Watchdog()

        # TaskManager
        from firmware.task_manager import TaskManager
        self._task_manager = TaskManager(
            self._drivers, self._fsm, self._shared_state, self._watchdog
        )

        self._logger.info("Başlatma tamamlandı.")
        return True

    def run(self):
        signal.signal(signal.SIGINT,  self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        if not self.initialize():
            sys.exit(1)

        self._watchdog.start()
        self._task_manager.start_all()
        if self._web_ui:
            self._web_ui.start()

        self._running = True
        self._logger.info("=" * 50)
        self._logger.info("  VeloGuard çalışıyor — Ctrl+C ile durdur")
        self._logger.info("=" * 50)

        while self._running:
            time.sleep(1)

    def shutdown(self, signum=None, frame=None):
        self._logger.info("Kapanıyor...")
        self._running = False
        if self._task_manager:
            self._task_manager.stop_all()
        if self._watchdog:
            self._watchdog.stop()
        if self._telegram:
            try:
                self._telegram.stop()
            except Exception:
                pass
        if self._web_ui:
            try:
                self._web_ui.stop()
            except Exception:
                pass
        for name, drv in self._drivers.items():
            if drv and hasattr(drv, "cleanup"):
                try:
                    drv.cleanup()
                except Exception as e:
                    self._logger.warning(f"{name} cleanup hatası: {e}")
        self._logger.info("Temiz kapanış tamamlandı.")
        sys.exit(0)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)

    if os.geteuid() != 0:
        logger.warning(
            "Root yetkisi yok. SCHED_FIFO çalışmayacak. "
            "Gerçek-zamanlı performans için: sudo python3 -m firmware.main"
        )

    app = VeloGuardApp()
    app.run()
