"""
firmware/comm/mqtt.py — MQTT İletişim Katmanı
==============================================
Alarm olaylarını ve sistem durumunu MQTT broker'a yayınlar.
Ölçeklenebilirlik puanı için — WiFi+Telegram zaten MVP.

Broker: Yerel mosquitto (Pi'da) veya test.mosquitto.org (bulut test)
Topic şeması:
  veloguard/status      → {"state": "ARMED", "ts": 1234567890}
  veloguard/alarm       → {"level": "HIGH", "magnitude": 1.4, "ts": ...}
  veloguard/sensor/imu  → {"ax": 0.01, "ay": 0.02, "az": 0.98, ...}
  veloguard/sensor/env  → {"temp_c": 22.5, "humidity": 58.0, ...}
  veloguard/power       → {"battery_pct": 85, "power_mw": 1900}

ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import json
import time
import logging
import threading
from typing import Optional

logger = logging.getLogger(__name__)

_BROKER_HOST = "localhost"
_BROKER_PORT = 1883
_TOPIC_BASE  = "veloguard"


class MQTTPublisher:
    """
    MQTT broker'a veri yayınlar.
    paho-mqtt kütüphanesi kurulu değilse sessizce degrade olur.
    """

    def __init__(self, host: str = _BROKER_HOST, port: int = _BROKER_PORT):
        self._host = host
        self._port = port
        self._client = None
        self._connected = False
        self._lock = threading.Lock()

    def connect(self) -> bool:
        """
        Broker'a bağlanır.

        Yapması gerekenler:
        - paho.mqtt.client import et (ImportError → uyarı logla, False dön)
        - mqtt.Client() oluştur
        - client.on_connect callback ayarla
        - client.connect(host, port, keepalive=60)
        - client.loop_start() (arka plan thread)
        - self._connected = True
        - True döndür
        """
        try:
            import paho.mqtt.client as mqtt  # type: ignore
        except ImportError:
            logger.warning("paho-mqtt kurulu değil — MQTT devre dışı. "
                           "Kurmak için: pip install paho-mqtt")
            return False

        try:
            self._client = mqtt.Client(client_id="veloguard")
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.connect(self._host, self._port, keepalive=60)
            self._client.loop_start()
            self._connected = True
            logger.info(f"MQTT bağlantısı kuruldu: {self._host}:{self._port}")
            return True
        except Exception as exc:
            logger.warning(f"MQTT bağlanamadı ({exc}) — devre dışı")
            return False

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT broker'a bağlandı.")
        else:
            logger.warning(f"MQTT bağlantı hatası: rc={rc}")

    def _on_disconnect(self, client, userdata, rc):
        self._connected = False
        logger.warning(f"MQTT bağlantısı kesildi: rc={rc}")

    def publish(self, subtopic: str, payload: dict):
        """
        JSON payload'ı belirtilen alt konuya yayınlar.

        Yapması gerekenler:
        - Bağlı değilse dön (sessizce)
        - topic = f"{_TOPIC_BASE}/{subtopic}"
        - client.publish(topic, json.dumps(payload), qos=0, retain=False)
        """
        if not self._connected or self._client is None:
            return
        topic = f"{_TOPIC_BASE}/{subtopic}"
        try:
            with self._lock:
                self._client.publish(topic, json.dumps(payload), qos=0)
        except Exception as exc:
            logger.debug(f"MQTT publish hatası: {exc}")

    def publish_status(self, state_name: str):
        self.publish("status", {"state": state_name, "ts": time.time()})

    def publish_alarm(self, level: str, magnitude: float):
        self.publish("alarm", {"level": level, "magnitude": round(magnitude, 4),
                               "ts": time.time()})

    def publish_imu(self, ax: float, ay: float, az: float, magnitude: float):
        self.publish("sensor/imu", {"ax": round(ax, 4), "ay": round(ay, 4),
                                    "az": round(az, 4),
                                    "magnitude": round(magnitude, 4),
                                    "ts": time.time()})

    def publish_env(self, temp_c: Optional[float], humidity: Optional[float]):
        self.publish("sensor/env", {"temp_c": temp_c, "humidity": humidity,
                                    "ts": time.time()})

    def publish_power(self, battery_pct: Optional[float], power_mw: Optional[float]):
        self.publish("power", {"battery_pct": battery_pct, "power_mw": power_mw,
                               "ts": time.time()})

    def disconnect(self):
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()
            self._connected = False
