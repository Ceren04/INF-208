"""
firmware/drivers/base_sensor.py — Tüm Sürücülerin Temel Sınıfı
===============================================================
Her sensör/aktüatör sürücüsünün uygulaması gereken arayüzü tanımlar.
initialize(), read(), cleanup() zorunlu metodlar; alt sınıflar override eder.

ÇALIŞTIĞI YER: Raspberry Pi 3B (ve mock modda her ortamda)
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Any


class BaseSensor(ABC):
    """
    Tüm VeloGuard sürücüleri bu sınıfı miras alır.
    Ortak durum yönetimi ve logging altyapısı sağlar.
    """

    def __init__(self, name: str):
        self._name = name
        self._initialized = False
        self._logger = logging.getLogger(f"veloguard.driver.{name.lower()}")

    @abstractmethod
    def initialize(self) -> bool:
        """
        Donanımı başlatır.
        Başarılıysa True, başarısızsa False döndürür.
        """
        ...

    def read(self) -> Optional[Any]:
        """
        Sensörden en güncel veriyi okur.
        Sürücüler gerekirse override eder.
        """
        return None

    @abstractmethod
    def cleanup(self):
        """
        Donanım kaynaklarını serbest bırakır (GPIO, I2C, PWM, vs.).
        Program kapanırken veya hata durumunda çağrılır.
        """
        ...

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_initialized(self) -> bool:
        return self._initialized

    def __repr__(self) -> str:
        status = "initialized" if self._initialized else "not initialized"
        return f"<{self.__class__.__name__} name={self._name!r} {status}>"
