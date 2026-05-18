"""
firmware/task_manager.py — RTOS Thread Yöneticisi
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import threading
import time
import os
import logging
from typing import List
from firmware.config import TaskPriority, IMUConfig, ThermalConfig, PowerConfig
from firmware.fsm import Event

logger = logging.getLogger(__name__)


def set_thread_realtime_priority(priority: int):
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, os.sched_param(priority))
        logger.debug(f"SCHED_FIFO önceliği ayarlandı: {priority}")
    except (PermissionError, AttributeError, OSError):
        logger.warning(f"RT öncelik ayarlanamadı (root gerekli) — normal öncelikle devam.")


class IMUTask:
    def __init__(self, imu_driver, motion_detector, shared_state, fsm, watchdog=None):
        self._imu = imu_driver
        self._detector = motion_detector
        self._state = shared_state
        self._fsm = fsm
        self._watchdog = watchdog
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()
        self._interval = IMUConfig.SAMPLE_INTERVAL_S

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="IMUTask")
        self._thread.start()

    def _run(self):
        set_thread_realtime_priority(TaskPriority.IMU_SAMPLING)

        if self._imu is None:
            logger.warning("IMUTask: IMU sürücüsü None — task sonlandırılıyor.")
            return

        # Watchdog'u sadece task gerçekten çalışacaksa kaydet
        if self._watchdog:
            self._watchdog.register("IMUTask")

        from firmware.motion_detector import MotionLevel
        from firmware.fsm import State
        from firmware.config import FSMConfig

        prev_state = None
        arm_suppress_until = 0.0  # ARM sonrası motion eventlerini geçici sustur

        while not self._stop_event.is_set():
            loop_start = time.monotonic()
            try:
                current_state = self._fsm.get_state()

                # ARMED geçişi: detector sıfırla + kısa bekleme süresi
                if current_state == State.ARMED and prev_state != State.ARMED:
                    self._detector.reset()
                    arm_suppress_until = time.time() + FSMConfig.ARM_DELAY_S
                    logger.info("IMUTask: ARMED → detector sıfırlandı, "
                                f"{FSMConfig.ARM_DELAY_S}s bekleme başladı")
                prev_state = current_state

                data = self._imu.read()
                if data:
                    ax, ay, az = data["ax"], data["ay"], data["az"]
                    mag = self._imu.compute_magnitude(ax, ay, az)
                    filtered = self._detector.get_filtered_magnitude(mag)
                    level = self._detector.detect(mag)
                    self._detector.update_baseline(mag, current_state.name)
                    self._state.update_imu(ax, ay, az, mag, filtered)

                    # ARM suppress süresi geçtiyse event gönder
                    if time.time() > arm_suppress_until:
                        if level == MotionLevel.HIGH:
                            self._state.push_event(Event.MOTION_HIGH)
                        elif level == MotionLevel.LOW:
                            self._state.push_event(Event.MOTION_LOW)

                if self._watchdog:
                    self._watchdog.heartbeat("IMUTask")

            except Exception as exc:
                logger.error(f"IMUTask döngü hatası: {exc}")

            elapsed = time.monotonic() - loop_start
            sleep_time = self._interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self._stop_event.set()


class ReedTask:
    def __init__(self, reed_driver, shared_state, fsm):
        self._reed = reed_driver
        self._state = shared_state
        self._fsm = fsm
        self._stop_event = threading.Event()

    def start(self):
        if self._reed is None:
            logger.warning("ReedTask: reed sürücüsü yok, tamper algılama devre dışı.")
            return
        self._reed.on_open(self._on_tamper_open)
        self._reed.on_close(self._on_tamper_close)

    def _on_tamper_open(self):
        self._state.update_reed(is_open=True)
        self._state.push_event(Event.TAMPER_OPEN)

    def _on_tamper_close(self):
        self._state.update_reed(is_open=False)
        self._state.push_event(Event.TAMPER_CLOSE)

    def stop(self):
        self._stop_event.set()


class FSMTask:
    def __init__(self, fsm, shared_state, led_driver, sound_driver,
                 camera_driver, telegram_bot, watchdog=None):
        self._fsm = fsm
        self._state = shared_state
        self._led = led_driver
        self._sound = sound_driver
        self._camera = camera_driver
        self._telegram = telegram_bot
        self._watchdog = watchdog
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()
        self._prev_state = None

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="FSMTask")
        self._thread.start()

    def _run(self):
        set_thread_realtime_priority(TaskPriority.FSM_CORE)
        if self._watchdog:
            self._watchdog.register("FSMTask")

        while not self._stop_event.is_set():
            event = self._state.pop_event(timeout=0.1)
            if event is not None:
                changed = self._fsm.handle_event(event)
                if changed:
                    new_state = self._fsm.get_state()
                    is_tamper = self._fsm.is_tamper()
                    self._trigger_actuators(new_state, is_tamper)
                    self._prev_state = new_state

            if self._watchdog:
                self._watchdog.heartbeat("FSMTask")

    def _trigger_actuators(self, new_state, is_tamper: bool):
        from firmware.fsm import State
        state_name = "TAMPER" if is_tamper else new_state.name
        if self._led:
            try:
                self._led.set_fsm_pattern(state_name)
            except Exception as exc:
                logger.error(f"LED pattern hatası: {exc}")

        if new_state in (State.ALARM,) or is_tamper:
            if self._sound:
                try:
                    self._sound.start_alarm()
                except Exception as exc:
                    logger.error(f"Alarm sesi başlatılamadı: {exc}")
            threading.Thread(
                target=self._capture_and_notify,
                daemon=True,
                name="AlarmCapture"
            ).start()

        elif new_state in (State.DISARMED, State.ARMED, State.RIDE):
            if self._sound:
                try:
                    self._sound.stop_alarm()
                except Exception:
                    pass

        elif new_state == State.PRE_ALARM:
            if self._sound:
                try:
                    threading.Thread(
                        target=self._sound.beep_pattern,
                        args=(1,),
                        daemon=True,
                    ).start()
                except Exception:
                    pass

    def _capture_and_notify(self):
        try:
            snapshot = self._state.get_snapshot()
            status = self._fsm.get_status_dict()
            msg = (f"🚨 ALARM — {status['state']}\n"
                   f"IMU: {snapshot.imu_magnitude:.3f}g\n"
                   f"Zaman: {time.strftime('%H:%M:%S')}")

            if self._camera:
                paths = self._camera.capture_alarm_series()
                for path in paths:
                    if self._telegram:
                        try:
                            with open(path, "rb") as f:
                                self._telegram.send_alarm_photo_sync(f.read(), msg)
                        except Exception as exc:
                            logger.warning(f"Fotoğraf gönderilemedi: {exc}")
            elif self._telegram:
                self._telegram.send_alarm_message_sync(msg)

        except Exception as exc:
            logger.error(f"Alarm yakalama hatası: {exc}")

    def stop(self):
        self._stop_event.set()


class ThermalTask:
    def __init__(self, dht_driver, shared_state, fsm, watchdog=None):
        self._dht = dht_driver
        self._state = shared_state
        self._fsm = fsm
        self._watchdog = watchdog
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="ThermalTask")
        self._thread.start()

    def _run(self):
        set_thread_realtime_priority(TaskPriority.TEMP_MONITOR)
        interval = 1.0 / ThermalConfig.DHT22_SAMPLE_HZ
        while not self._stop_event.is_set():
            try:
                if self._dht:
                    data = self._dht.read()
                    if data:
                        self._state.update_thermal(
                            data.get("temp_c"), data.get("humidity"), data.get("cpu_temp_c")
                        )
                        self._check_thermal_events(data.get("cpu_temp_c"))
                if self._watchdog:
                    self._watchdog.heartbeat("ThermalTask")
            except Exception as exc:
                logger.error(f"ThermalTask hatası: {exc}")
            time.sleep(interval)

    def _check_thermal_events(self, cpu_temp):
        if cpu_temp is None:
            return
        from firmware.config import ThermalConfig
        if cpu_temp >= ThermalConfig.CPU_TEMP_THROTTLE_C:
            self._state.push_event(Event.THERMAL_CRITICAL)
        elif cpu_temp >= ThermalConfig.CPU_TEMP_CAMERA_OFF_C:
            self._state.push_event(Event.THERMAL_WARNING)

    def stop(self):
        self._stop_event.set()


class PowerMonitorTask:
    def __init__(self, ina219_driver, shared_state, fsm, watchdog=None):
        self._ina = ina219_driver
        self._state = shared_state
        self._fsm = fsm
        self._watchdog = watchdog
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="PowerTask")
        self._thread.start()

    def _run(self):
        set_thread_realtime_priority(TaskPriority.POWER_MONITOR)
        from firmware.config import PowerConfig
        interval = 1.0 / PowerConfig.INA219_SAMPLE_HZ
        while not self._stop_event.is_set():
            try:
                if self._ina:
                    data = self._ina.read()
                    if data:
                        pct = data.get("battery_pct")
                        mw = data.get("power_mw")
                        self._state.update_power(pct, mw)
                        if pct is not None:
                            if pct <= PowerConfig.BATTERY_CRITICAL_PCT:
                                self._state.push_event(Event.BATTERY_CRITICAL)
                            elif pct <= PowerConfig.BATTERY_LOW_PCT:
                                self._state.push_event(Event.BATTERY_LOW)
                if self._watchdog:
                    self._watchdog.heartbeat("PowerTask")
            except Exception as exc:
                logger.error(f"PowerTask hatası: {exc}")
            time.sleep(interval)

    def stop(self):
        self._stop_event.set()


class LoggerTask:
    """Sensör verilerini CSV'ye yazan düşük öncelikli thread (Priority Inversion deneyi için LOW)."""

    def __init__(self, shared_state, fsm, watchdog=None):
        self._state = shared_state
        self._fsm = fsm
        self._watchdog = watchdog
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="LoggerTask")
        self._thread.start()

    def _run(self):
        set_thread_realtime_priority(TaskPriority.LOGGER)
        from firmware.config import LogConfig
        import csv
        import pathlib
        csv_path = pathlib.Path(LogConfig.CSV_LOG_FILE)
        csv_path.parent.mkdir(parents=True, exist_ok=True)

        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(["timestamp", "state", "ax", "ay", "az",
                                 "magnitude", "filtered", "temp_c", "battery_pct"])
            while not self._stop_event.is_set():
                try:
                    snap = self._state.get_snapshot()
                    fsm_state = self._fsm.get_state().name
                    writer.writerow([
                        f"{snap.timestamp:.3f}", fsm_state,
                        f"{snap.ax:.4f}", f"{snap.ay:.4f}", f"{snap.az:.4f}",
                        f"{snap.imu_magnitude:.4f}", f"{snap.imu_filtered:.4f}",
                        snap.ambient_temp_c, snap.battery_pct,
                    ])
                    f.flush()
                    if self._watchdog:
                        self._watchdog.heartbeat("LoggerTask")
                except Exception as exc:
                    logger.error(f"LoggerTask hatası: {exc}")
                time.sleep(1.0)

    def stop(self):
        self._stop_event.set()


class TaskManager:
    def __init__(self, drivers: dict, fsm, shared_state, watchdog=None):
        imu   = drivers.get("imu")
        reed  = drivers.get("reed")
        led   = drivers.get("led")
        sound = drivers.get("sound")
        cam   = drivers.get("camera")
        tg    = drivers.get("telegram")
        dht   = drivers.get("dht")
        ina   = drivers.get("ina219")
        md    = drivers.get("motion_detector")

        self._tasks: List = [
            IMUTask(imu, md, shared_state, fsm, watchdog),
            ReedTask(reed, shared_state, fsm),
            FSMTask(fsm, shared_state, led, sound, cam, tg, watchdog),
            ThermalTask(dht, shared_state, fsm, watchdog),
            PowerMonitorTask(ina, shared_state, fsm, watchdog),
            LoggerTask(shared_state, fsm, watchdog),
        ]

    def start_all(self):
        for task in self._tasks:
            task.start()
        logger.info(f"Tüm task'lar başlatıldı ({len(self._tasks)} adet).")

    def stop_all(self):
        for task in self._tasks:
            task.stop()
        logger.info("Tüm task'lar durduruldu.")
