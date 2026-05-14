"""
firmware/drivers/camera_driver.py — Pi Camera v2 Sürücüsü
ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import time
import os
import logging
from typing import Optional, List, Tuple
import numpy as np
from firmware.config import CameraConfig
from firmware.drivers.base_sensor import BaseSensor

logger = logging.getLogger(__name__)


class CameraDriver(BaseSensor):
    def __init__(self):
        super().__init__("Camera")
        self._camera = None
        self._is_running = False
        os.makedirs(CameraConfig.PHOTO_SAVE_DIR, exist_ok=True)

    def initialize(self) -> bool:
        try:
            from picamera2 import Picamera2  # type: ignore
            self._camera = Picamera2()
            cfg = self._camera.create_still_configuration(
                main={"size": CameraConfig.RESOLUTION}
            )
            self._camera.configure(cfg)
            self._camera.start()
            time.sleep(2.0)  # warm-up
            self._is_running = True
            self._initialized = True
            self._logger.info(f"Pi Camera başlatıldı — {CameraConfig.RESOLUTION}")
            return True
        except Exception as exc:
            self._logger.error(f"Kamera başlatılamadı: {exc}")
            return False

    def capture_photo(self, filename: Optional[str] = None) -> Optional[str]:
        if not self._initialized or self._camera is None:
            return None
        if filename is None:
            filename = f"alarm_{int(time.time())}.jpg"
        full_path = os.path.join(CameraConfig.PHOTO_SAVE_DIR, filename)
        try:
            self._camera.capture_file(full_path)
            self._logger.debug(f"Fotoğraf kaydedildi: {full_path}")
            return full_path
        except Exception as exc:
            self._logger.error(f"Fotoğraf çekilemedi: {exc}")
            return None

    def capture_alarm_series(self) -> List[str]:
        paths = []
        for i in range(CameraConfig.ALARM_PHOTO_COUNT):
            path = self.capture_photo(f"alarm_{int(time.time())}_{i}.jpg")
            if path:
                paths.append(path)
            if i < CameraConfig.ALARM_PHOTO_COUNT - 1:
                time.sleep(CameraConfig.ALARM_PHOTO_INTERVAL_S)
        self._logger.info(f"Alarm serisi: {len(paths)} fotoğraf çekildi")
        return paths

    def capture_frame_array(self) -> Optional[np.ndarray]:
        if not self._initialized or self._camera is None:
            return None
        try:
            return self._camera.capture_array()
        except Exception as exc:
            self._logger.error(f"Frame alınamadı: {exc}")
            return None

    def detect_motion_region(
        self,
        frame1: np.ndarray,
        frame2: np.ndarray
    ) -> Optional[Tuple[int, int, int, int]]:
        try:
            import cv2  # type: ignore
            g1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
            g2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
            diff = cv2.absdiff(g1, g2)
            _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
            thresh = cv2.dilate(thresh, None, iterations=2)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return None
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) < CameraConfig.MOTION_MIN_AREA_PX:
                return None
            return cv2.boundingRect(largest)
        except Exception as exc:
            self._logger.error(f"Hareket tespiti hatası: {exc}")
            return None

    def draw_motion_box(
        self,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        try:
            import cv2  # type: ignore
            out = frame.copy()
            x, y, w, h = bbox
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(out, "HAREKET ALGILANDI", (x, max(y - 10, 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return out
        except Exception:
            return frame

    def frame_to_jpeg_bytes(
        self,
        frame: np.ndarray,
        quality: int = CameraConfig.JPEG_QUALITY
    ) -> Optional[bytes]:
        try:
            import cv2  # type: ignore
            success, buf = cv2.imencode(
                ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
            if success:
                return buf.tobytes()
            return None
        except Exception as exc:
            self._logger.error(f"JPEG dönüşüm hatası: {exc}")
            return None

    def stop(self):
        if self._camera is not None:
            try:
                self._camera.stop()
            except Exception:
                pass
            self._camera = None
        self._is_running = False
        self._initialized = False

    def cleanup(self):
        self.stop()
        self._logger.info("Kamera kapatıldı.")
