"""
tools/energy_logger.py — INA219 Enerji Loglayıcı
==================================================
Her FSM state'inde 5 dakika boyunca güç tüketimini loglar.
INA219 yoksa simüle edilmiş veri üretir.

Çalıştırma (Pi'da):
  cd ~/veloguard && source venv/bin/activate
  python3 tools/energy_logger.py --state ARMED --duration 300

Çıktı: /var/log/veloguard/energy_<state>_<timestamp>.csv

ÇALIŞTIĞI YER: Raspberry Pi 3B
"""

import sys
import os
import csv
import time
import random
import argparse
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))


# Durum başına beklenen güç değerleri (simülasyon için)
STATE_POWER_MW = {
    "DISARMED":  {"v": 5.05, "i": 95,   "mean": 480,  "std": 20},
    "ARMED":     {"v": 5.04, "i": 380,  "mean": 1920, "std": 80},
    "PRE_ALARM": {"v": 5.04, "i": 520,  "mean": 2620, "std": 100},
    "ALARM":     {"v": 5.03, "i": 920,  "mean": 4620, "std": 200},
    "RIDE":      {"v": 5.04, "i": 280,  "mean": 1410, "std": 60},
    "ECO":       {"v": 5.05, "i": 240,  "mean": 1210, "std": 50},
}


def read_ina219():
    """INA219'dan gerçek veri okumayı dener, yoksa None döner."""
    try:
        import board, busio, adafruit_ina219  # type: ignore
        i2c = busio.I2C(board.SCL, board.SDA)
        ina = adafruit_ina219.INA219(i2c, addr=0x40)
        ina.set_calibration_32V_2A()
        return {
            "voltage_v": ina.bus_voltage,
            "current_ma": ina.current,
            "power_mw": ina.power * 1000,
        }
    except Exception:
        return None


def simulate_reading(state: str) -> dict:
    """INA219 yokken simüle edilmiş güç verisi üretir."""
    p = STATE_POWER_MW.get(state, STATE_POWER_MW["ARMED"])
    power = max(0, random.gauss(p["mean"], p["std"]))
    voltage = p["v"] + random.gauss(0, 0.01)
    current = power / voltage if voltage > 0 else 0
    return {
        "voltage_v": round(voltage, 3),
        "current_ma": round(current, 1),
        "power_mw": round(power, 1),
    }


def log_energy(state: str, duration_s: int, sample_hz: float, out_path: str):
    interval = 1.0 / sample_hz
    samples = []
    start = time.time()
    end = start + duration_s

    print(f"[energy_logger] State={state}, süre={duration_s}s, "
          f"{sample_hz}Hz → {out_path}")

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "state", "voltage_v",
                         "current_ma", "power_mw"])

        while time.time() < end:
            t = time.time()
            data = read_ina219() or simulate_reading(state)
            data["timestamp"] = round(t - start, 3)
            data["state"] = state
            samples.append(data["power_mw"])

            writer.writerow([
                data["timestamp"], state,
                data["voltage_v"], data["current_ma"], data["power_mw"]
            ])
            f.flush()

            elapsed = time.time() - t
            time.sleep(max(0, interval - elapsed))

    if samples:
        avg = sum(samples) / len(samples)
        mx = max(samples)
        mn = min(samples)
        print(f"[energy_logger] Tamamlandı — "
              f"Min={mn:.0f}mW  Avg={avg:.0f}mW  Max={mx:.0f}mW  "
              f"N={len(samples)}")
        return {"state": state, "min_mw": mn, "avg_mw": avg, "max_mw": mx,
                "n": len(samples)}
    return {}


def run_all_states(duration_each: int = 300, out_dir: str = "/var/log/veloguard"):
    """Tüm FSM durumları için enerji ölçümü yapar."""
    os.makedirs(out_dir, exist_ok=True)
    results = []
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    for state in STATE_POWER_MW:
        path = os.path.join(out_dir, f"energy_{state}_{ts}.csv")
        result = log_energy(state, duration_each, 2.0, path)
        if result:
            results.append(result)
        time.sleep(2)

    # Özet tablosu
    print("\n" + "="*65)
    print("ENERJİ TABLOSU — VeloGuard")
    print("="*65)
    print(f"{'State':<12} {'Min(mW)':>9} {'Avg(mW)':>9} {'Max(mW)':>9} "
          f"{'5h Wh':>8}")
    print("-"*65)
    for r in results:
        wh_5h = r["avg_mw"] / 1000 * 5
        print(f"{r['state']:<12} {r['min_mw']:>9.0f} {r['avg_mw']:>9.0f} "
              f"{r['max_mw']:>9.0f} {wh_5h:>8.2f}")
    print("="*65)

    # Pil ömrü tahmini
    if any(r["state"] == "ARMED" for r in results):
        armed = next(r for r in results if r["state"] == "ARMED")
        bat_wh = 3.7 * 3.0  # 18650 3000mAh
        hours = bat_wh / (armed["avg_mw"] / 1000)
        print(f"\nPil ömrü tahmini (ARMED modunda): {hours:.1f} saat")


def main():
    parser = argparse.ArgumentParser(description="VeloGuard Enerji Loglayıcı")
    parser.add_argument("--state",    default="ARMED",
                        choices=list(STATE_POWER_MW.keys()),
                        help="Ölçülecek FSM durumu")
    parser.add_argument("--duration", type=int, default=60,
                        help="Ölçüm süresi (saniye)")
    parser.add_argument("--hz",       type=float, default=2.0,
                        help="Örnekleme frekansı")
    parser.add_argument("--all",      action="store_true",
                        help="Tüm durumları ölç")
    parser.add_argument("--out",      default="/var/log/veloguard",
                        help="Çıktı dizini")
    args = parser.parse_args()

    if args.all:
        run_all_states(args.duration, args.out)
    else:
        os.makedirs(args.out, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(args.out, f"energy_{args.state}_{ts}.csv")
        log_energy(args.state, args.duration, args.hz, path)


if __name__ == "__main__":
    main()
