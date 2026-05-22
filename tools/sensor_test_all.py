"""
tools/sensor_test_all.py — Tüm Sensör Entegrasyon Testi
=========================================================
Tüm sensörleri tek bir script'te test eder.
30 saniye boyunca tüm sensörlerden veri okur, tablo halinde gösterir.

Çalıştırma (Pi'da):
  cd ~/veloguard && source venv/bin/activate
  python3 tools/sensor_test_all.py

ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import sys
import time
import os
from pathlib import Path

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

from firmware.drivers.imu_driver import IMUDriver
from firmware.algorithms.kalman import KalmanFilter1D

# ANSI renkleri
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def reset_gpio():
    """Önceki çalışmadan kalan GPIO durumunu temizle (RPi.GPIO + gpiozero çakışması)."""
    try:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
    except Exception:
        pass


def try_init(name: str, driver):
    """Sürücüyü başlatmayı dener, sonucu raporlar."""
    try:
        ok = driver.initialize()
        status = f"{GREEN}✓ HAZIR{RESET}" if ok else f"{RED}✗ BAŞARISIZ{RESET}"
    except Exception as e:
        ok = False
        status = f"{RED}✗ HATA: {e}{RESET}"
    print(f"  {name:<20} {status}")
    return driver if ok else None


def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except Exception:
        return None


def main():
    reset_gpio()

    print(f"\n{BOLD}=== VeloGuard Sensör Entegrasyon Testi ==={RESET}")
    print(f"Kernel: {os.popen('uname -r').read().strip()}")
    print(f"Python: {sys.version.split()[0]}\n")

    # ── Sürücüleri başlat ──────────────────────────────────────────────────
    print(f"{BOLD}[1/3] Sürücü başlatma:{RESET}")
    imu = try_init("IMU (MPU-6050)", IMUDriver())

    try:
        from firmware.drivers.led_driver import LEDDriver
        led = try_init("LED (GPIO23/24/25)", LEDDriver())
    except Exception as e:
        led = None
        print(f"  {'LED':<20} {RED}✗ {e}{RESET}")

    try:
        from firmware.drivers.reed_driver import ReedDriver
        reed = try_init("Reed Switch (GPIO27)", ReedDriver())
    except Exception as e:
        reed = None
        print(f"  {'Reed Switch':<20} {RED}✗ {e}{RESET}")

    try:
        from firmware.drivers.pam8403_driver import PAM8403Driver
        pam = try_init("PAM8403 (GPIO18)", PAM8403Driver())
    except Exception as e:
        pam = None
        print(f"  {'PAM8403':<20} {RED}✗ {e}{RESET}")

    try:
        from firmware.drivers.dht_driver import DHTDriver
        dht = try_init("DHT22 (GPIO4)", DHTDriver())
    except Exception as e:
        dht = None
        print(f"  {'DHT22':<20} {RED}✗ {e}{RESET}")

    try:
        from firmware.drivers.ina219_driver import INA219Driver
        ina = try_init("INA219 (I2C 0x40)", INA219Driver())
    except Exception as e:
        ina = None
        print(f"  {'INA219':<20} {RED}✗ {e}{RESET}")

    # ── Veri okuma döngüsü ─────────────────────────────────────────────────
    print(f"\n{BOLD}[2/3] 30 saniye veri akışı:{RESET}")
    print(f"{'Zaman':>8} | {'ax':>7} {'ay':>7} {'az':>7} | "
          f"{'mag':>7} {'flt':>7} | {'CPU°C':>7} | {'V':>6} {'I(mA)':>7} | "
          f"{'Reed':>6}")
    print("-" * 90)

    kf = KalmanFilter1D()
    start = time.time()

    while time.time() - start < 30:
        elapsed = time.time() - start
        row = f"{elapsed:>8.1f}"

        # IMU
        if imu:
            d = imu.read()
            if d:
                mag = imu.compute_magnitude(d["ax"], d["ay"], d["az"])
                flt = kf.update(mag)
                row += f" | {d['ax']:>+7.3f} {d['ay']:>+7.3f} {d['az']:>+7.3f}"
                row += f" | {mag:>7.4f} {flt:>7.4f}"
            else:
                row += f" | {'---':>7} {'---':>7} {'---':>7} | {'---':>7} {'---':>7}"
        else:
            row += f" | {'N/A':>7} {'N/A':>7} {'N/A':>7} | {'N/A':>7} {'N/A':>7}"

        # CPU sıcaklık
        cpu_t = get_cpu_temp()
        row += f" | {cpu_t:>7.1f}" if cpu_t else f" | {'---':>7}"

        # INA219
        if ina:
            p = ina.read()
            row += (f" | {p['bus_voltage_v']:>6.2f} {p['current_ma']:>7.0f}"
                    if p else f" | {'---':>6} {'---':>7}")
        else:
            row += f" | {'---':>6} {'---':>7}"

        # Reed switch
        if reed:
            rd = reed.read()
            status = f"{RED}AÇIK{RESET}" if rd["is_open"] else f"{GREEN}kapalı{RESET}"
            row += f" | {status:>6}"
        else:
            row += f" | {'---':>6}"

        print(f"\r{row}", end="", flush=True)
        time.sleep(0.1)

    print()

    # ── Aktüatör testi ─────────────────────────────────────────────────────
    print(f"\n{BOLD}[3/3] Aktüatör testi:{RESET}")

    if led:
        from firmware.drivers.led_driver import LEDColor

        # 30 sn sensör döngüsü sonrası pinleri yeniden kur (gpiozero çakışması)
        led.cleanup()
        if not led.initialize():
            print(f"  LED {RED}✗ yeniden başlatılamadı{RESET}")
        else:
            print("  Yeşil LED (ARMED)...")
            led.set(LEDColor.GREEN, True)
            time.sleep(1.0)
            led.set(LEDColor.GREEN, False)

            print("  Sarı LED (PRE_ALARM)...")
            led.set(LEDColor.YELLOW, True)
            time.sleep(1.0)
            led.set(LEDColor.YELLOW, False)

            print("  Kırmızı LED (ALARM)...")
            led.set(LEDColor.RED, True)
            time.sleep(1.0)
            led.set(LEDColor.RED, False)

            print("  FSM blink pattern (3sn)...")
            led.set_fsm_pattern("ARMED")
            time.sleep(1.5)
            led.set_fsm_pattern("PRE_ALARM")
            time.sleep(1.0)
            led.set_fsm_pattern("ALARM")
            time.sleep(0.5)
            led.all_off()
            print(f"  LED {GREEN}✓{RESET}")
            print(f"  {YELLOW}Not: LED yanmadıysa GPIO23/24/25 kablolarını ve 220Ω dirençleri kontrol edin.{RESET}")

    if pam:
        print("  PAM8403 bip testi...")
        pam.beep_pattern(2, on_ms=200)
        print(f"  PAM8403 {GREEN}✓{RESET}")

    # ── Temizlik ───────────────────────────────────────────────────────────
    for drv in [imu, led, reed, pam, dht, ina]:
        if drv:
            try:
                drv.cleanup()
            except Exception:
                pass

    print(f"\n{BOLD}=== Test tamamlandı ==={RESET}")


if __name__ == "__main__":
    main()
