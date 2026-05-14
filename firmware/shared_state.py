"""
firmware/shared_state.py — Thread-Safe Paylaşılan Durum Tamponu
================================================================
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import queue
import threading
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class SensorSnapshot:
    timestamp:      float = 0.0
    ax:             float = 0.0
    ay:             float = 0.0
    az:             float = 0.0
    imu_magnitude:  float = 0.0
    imu_filtered:   float = 0.0
    ambient_temp_c: Optional[float] = None
    humidity_pct:   Optional[float] = None
    cpu_temp_c:     Optional[float] = None
    battery_pct:    Optional[float] = None
    power_mw:       Optional[float] = None
    reed_is_open:   bool = False


class SharedState:
    """Sensörler arası thread-safe veri deposu."""

    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot = SensorSnapshot()
        self._event_queue: queue.Queue = queue.Queue(maxsize=100)

    # ── IMU ─────────────────────────────────────────────────────────────────

    def update_imu(self, ax: float, ay: float, az: float,
                   magnitude: float, filtered: float):
        with self._lock:
            self._snapshot.ax           = ax
            self._snapshot.ay           = ay
            self._snapshot.az           = az
            self._snapshot.imu_magnitude = magnitude
            self._snapshot.imu_filtered  = filtered
            self._snapshot.timestamp     = time.time()

    # ── Termal ──────────────────────────────────────────────────────────────

    def update_thermal(self, ambient_temp: Optional[float],
                       humidity: Optional[float], cpu_temp: Optional[float]):
        with self._lock:
            self._snapshot.ambient_temp_c = ambient_temp
            self._snapshot.humidity_pct   = humidity
            self._snapshot.cpu_temp_c     = cpu_temp

    # ── Güç ─────────────────────────────────────────────────────────────────

    def update_power(self, battery_pct: Optional[float], power_mw: Optional[float]):
        with self._lock:
            self._snapshot.battery_pct = battery_pct
            self._snapshot.power_mw    = power_mw

    # ── Reed ─────────────────────────────────────────────────────────────────

    def update_reed(self, is_open: bool):
        with self._lock:
            self._snapshot.reed_is_open = is_open

    # ── Snapshot ────────────────────────────────────────────────────────────

    def get_snapshot(self) -> SensorSnapshot:
        with self._lock:
            s = self._snapshot
            return SensorSnapshot(
                timestamp=s.timestamp, ax=s.ax, ay=s.ay, az=s.az,
                imu_magnitude=s.imu_magnitude, imu_filtered=s.imu_filtered,
                ambient_temp_c=s.ambient_temp_c, humidity_pct=s.humidity_pct,
                cpu_temp_c=s.cpu_temp_c, battery_pct=s.battery_pct,
                power_mw=s.power_mw, reed_is_open=s.reed_is_open,
            )

    # ── Event kuyruğu ───────────────────────────────────────────────────────

    def push_event(self, event):
        try:
            self._event_queue.put_nowait(event)
        except queue.Full:
            logger.warning(f"Event kuyruğu dolu, atlandı: {event}")

    def pop_event(self, timeout: float = 0.1):
        try:
            return self._event_queue.get(timeout=timeout)
        except queue.Empty:
            return None
