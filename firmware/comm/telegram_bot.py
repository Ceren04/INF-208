"""
firmware/comm/telegram_bot.py — Telegram Alarm Bildirimi
ÇALIŞTIĞI YER: Raspberry Pi 3B (internet bağlantısı gerekir)
"""

import queue
import logging
import threading
from datetime import datetime
from typing import Optional
from firmware.config import TelegramConfig

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, fsm=None):
        self._token   = TelegramConfig.TOKEN
        self._chat_id = TelegramConfig.CHAT_ID
        self._bot     = None
        self._fsm     = fsm
        self._send_queue: queue.Queue = queue.Queue(maxsize=50)
        self._sender_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._initialized = False

    def initialize(self) -> bool:
        if not self._token or not self._chat_id:
            logger.warning("Telegram TOKEN veya CHAT_ID eksik — bildirimler devre dışı.")
            return False
        try:
            import telegram  # type: ignore
            self._bot = telegram.Bot(token=self._token)
            # Bağlantı testi (sync)
            import asyncio
            loop = asyncio.new_event_loop()
            me = loop.run_until_complete(self._bot.get_me())
            loop.close()
            logger.info(f"Telegram bağlandı: @{me.username}")
            self._stop_event.clear()
            self._sender_thread = threading.Thread(
                target=self._sender_loop, daemon=True, name="TelegramSender"
            )
            self._sender_thread.start()
            self._initialized = True
            return True
        except ImportError:
            logger.warning("python-telegram-bot kurulu değil — bildirimler devre dışı.")
            return False
        except Exception as exc:
            logger.warning(f"Telegram başlatılamadı: {exc}")
            return False

    def send_alarm_message(self, state: str, is_tamper: bool = False):
        if not self._initialized:
            return
        text = (
            f"🚨 VeloGuard ALARM\n"
            f"Durum: {state}\n"
            f"Tamper: {'EVET' if is_tamper else 'Hayır'}\n"
            f"Zaman: {datetime.now().strftime('%H:%M:%S')}"
        )
        self._enqueue({"type": "message", "text": text})

    # Sync wrapper — TaskManager'dan çağrılır
    def send_alarm_message_sync(self, text: str):
        self._enqueue({"type": "message", "text": text})

    def send_alarm_photo(self, photo_bytes: bytes, caption: str = ""):
        if not self._initialized:
            return
        self._enqueue({"type": "photo", "data": photo_bytes, "caption": caption})

    def send_alarm_photo_sync(self, photo_bytes: bytes, caption: str = ""):
        self._enqueue({"type": "photo", "data": photo_bytes, "caption": caption})

    def send_status(self, status_dict: dict):
        if not self._initialized:
            return
        text = (
            f"📊 VeloGuard Durumu\n"
            f"Mod: {status_dict.get('state', '?')}\n"
            f"Pil: %{status_dict.get('battery_pct', '?')}\n"
            f"CPU: {status_dict.get('cpu_temp_c', '?')}°C\n"
            f"Nem: %{status_dict.get('humidity_pct', '?')}"
        )
        self._enqueue({"type": "message", "text": text})

    def _enqueue(self, item: dict):
        try:
            self._send_queue.put_nowait(item)
        except queue.Full:
            logger.warning("Telegram kuyruğu dolu, mesaj atlandı.")

    def _sender_loop(self):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while not self._stop_event.is_set():
            try:
                item = self._send_queue.get(timeout=1.0)
            except queue.Empty:
                continue
            for attempt in range(3):
                try:
                    if item["type"] == "message":
                        loop.run_until_complete(
                            self._bot.send_message(
                                chat_id=self._chat_id,
                                text=item["text"]
                            )
                        )
                    elif item["type"] == "photo":
                        import io
                        loop.run_until_complete(
                            self._bot.send_photo(
                                chat_id=self._chat_id,
                                photo=io.BytesIO(item["data"]),
                                caption=item.get("caption", ""),
                            )
                        )
                    break
                except Exception as exc:
                    logger.warning(f"Telegram gönderim hatası (deneme {attempt+1}): {exc}")
                    if attempt < 2:
                        import time; time.sleep(3)
        loop.close()

    def stop(self):
        self._stop_event.set()
        if self._sender_thread and self._sender_thread.is_alive():
            self._sender_thread.join(timeout=3.0)
        logger.info("TelegramNotifier durduruldu.")
