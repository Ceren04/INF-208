"""
firmware/watchdog.py — Yazılım Watchdog
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import threading
import logging
import os
import signal
from typing import Dict, Set

logger = logging.getLogger(__name__)

_WATCHDOG_INTERVAL_S = 5.0
_HEARTBEAT_TIMEOUT_S = 15.0


class Watchdog:
    def __init__(self):
        self._heartbeats: Dict[str, float] = {}
        self._required_threads: Set[str] = set()
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()

    def register(self, thread_name: str):
        self._required_threads.add(thread_name)
        self._heartbeats[thread_name] = time.time()

    def heartbeat(self, thread_name: str):
        self._heartbeats[thread_name] = time.time()

    def start(self):
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="Watchdog")
        self._thread.start()
        logger.info("Watchdog başlatıldı.")

    def _run(self):
        while not self._stop_event.wait(timeout=_WATCHDOG_INTERVAL_S):
            now = time.time()
            for name in self._required_threads:
                last = self._heartbeats.get(name, now)
                if (now - last) > _HEARTBEAT_TIMEOUT_S:
                    logger.critical(f"WATCHDOG: '{name}' thread'i {_HEARTBEAT_TIMEOUT_S}s'dir yanıt vermiyor!")
                    self._restart_system(name)

    def _restart_system(self, dead_thread: str):
        logger.critical(f"Sistem yeniden başlatılıyor — ölü thread: {dead_thread}")
        os.kill(os.getpid(), signal.SIGTERM)

    def stop(self):
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Watchdog durduruldu.")
