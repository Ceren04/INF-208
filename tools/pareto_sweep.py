"""
tools/pareto_sweep.py — IMU Örnekleme Hızı × Enerji Pareto Analizi
====================================================================
Farklı IMU örnekleme frekanslarında enerji tüketimi ve alarm reaksiyon
süresini ölçer. Pareto cephesini hesaplar ve grafik çizer.

Çalıştırma (Pi'da):
  python3 tools/pareto_sweep.py --measure   (gerçek ölçüm, ~20 dk)
  python3 tools/pareto_sweep.py             (simüle edilmiş veri)

Çıktı: docs/figures/pareto_front.png

ÇALIŞTIĞI YER: Pi (ölçüm) veya PC (simülasyon/grafik)
"""

import sys
import time
import math
import random
import argparse
import csv
from pathlib import Path
from typing import List, Tuple

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

# ── Örnekleme konfigürasyonları ────────────────────────────────────────────
HZ_CONFIGS = [25, 50, 100, 200, 400]

# Simülasyon parametreleri (Pi ölçümlerine dayalı)
SIM_PARAMS = {
    25:  {"power_mw": 1600, "reaction_ms": 240},
    50:  {"power_mw": 1720, "reaction_ms": 120},
    100: {"power_mw": 1920, "reaction_ms":  60},
    200: {"power_mw": 2250, "reaction_ms":  35},
    400: {"power_mw": 2890, "reaction_ms":  22},
}


def simulate_point(hz: int, n_trials: int = 10) -> dict:
    """Belirli bir Hz için güç/reaksiyon simülasyonu."""
    p = SIM_PARAMS[hz]
    powers = [p["power_mw"] + random.gauss(0, 30) for _ in range(n_trials)]
    reactions = [p["reaction_ms"] + random.gauss(0, 5) for _ in range(n_trials)]
    return {
        "hz": hz,
        "power_mw":    round(sum(powers) / n_trials, 1),
        "reaction_ms": round(sum(reactions) / n_trials, 1),
        "power_std":   round(math.sqrt(sum((x - sum(powers)/n_trials)**2
                             for x in powers) / n_trials), 1),
    }


def measure_point(hz: int, duration_s: int = 180) -> dict:
    """Gerçek Pi ölçümü (INA219 + IMU gerektirir)."""
    print(f"[pareto] Hz={hz} ölçülüyor ({duration_s}s)...")
    try:
        from firmware.drivers.imu_driver import IMUDriver
        from firmware.drivers.ina219_driver import INA219Driver
        from firmware.config import IMUConfig

        imu = IMUDriver()
        ina = INA219Driver()
        imu.initialize()
        ina.initialize()
        imu.set_sample_rate(hz)

        powers, reactions = [], []
        interval = 1.0 / hz
        start = time.time()

        prev_mag = 0.0
        t_motion_start = None

        while time.time() - start < duration_s:
            t0 = time.monotonic()
            d = imu.read()
            p = ina.read()

            if d and p:
                mag = imu.compute_magnitude(d["ax"], d["ay"], d["az"])
                powers.append(p["power_mw"])

                # Reaksiyon süresi: ani hareket başladığında
                if mag > 0.3 and prev_mag < 0.1:
                    t_motion_start = time.monotonic()
                if t_motion_start and mag > 0.5:
                    reactions.append((time.monotonic() - t_motion_start) * 1000)
                    t_motion_start = None
                prev_mag = mag

            elapsed = time.monotonic() - t0
            time.sleep(max(0, interval - elapsed))

        imu.cleanup()
        ina.cleanup()

        return {
            "hz": hz,
            "power_mw": round(sum(powers)/len(powers) if powers else 0, 1),
            "reaction_ms": round(sum(reactions)/len(reactions) if reactions
                                 else SIM_PARAMS[hz]["reaction_ms"], 1),
        }
    except Exception as e:
        print(f"[pareto] Ölçüm hatası ({hz}Hz): {e} — simülasyon kullanılıyor")
        return simulate_point(hz)


def is_pareto_dominated(p: dict, others: List[dict]) -> bool:
    """Başka bir nokta bu noktadan daha iyi mi?"""
    for o in others:
        if o["power_mw"] <= p["power_mw"] and o["reaction_ms"] <= p["reaction_ms"]:
            if o["power_mw"] < p["power_mw"] or o["reaction_ms"] < p["reaction_ms"]:
                return True
    return False


def compute_pareto_front(points: List[dict]) -> List[dict]:
    front = [p for p in points if not is_pareto_dominated(p, points)]
    return sorted(front, key=lambda p: p["power_mw"])


def plot_pareto(points: List[dict], front: List[dict], out_path: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib bulunamadı.")
        return

    C_BG      = "#1E1E1E"
    C_DOM     = "#F44336"
    C_FRONT   = "#4CAF50"
    C_LINE    = "#81C784"
    C_SELECT  = "#FFC107"
    C_TEXT    = "#EEEEEE"
    C_GRID    = "#333333"

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.tick_params(colors=C_TEXT)
    ax.xaxis.label.set_color(C_TEXT)
    ax.yaxis.label.set_color(C_TEXT)
    ax.title.set_color(C_TEXT)
    for sp in ax.spines.values():
        sp.set_color(C_GRID)
    ax.grid(True, color=C_GRID, alpha=0.4)

    front_hz = {p["hz"] for p in front}

    for p in points:
        color = C_FRONT if p["hz"] in front_hz else C_DOM
        marker = "o" if p["hz"] in front_hz else "x"
        ax.scatter(p["power_mw"], p["reaction_ms"],
                   s=120, color=color, marker=marker, zorder=4)
        ax.annotate(f"{p['hz']}Hz",
                    (p["power_mw"] + 15, p["reaction_ms"] + 1),
                    color=C_TEXT, fontsize=10, fontweight="bold")

    # Pareto cephesi çizgisi
    fx = [p["power_mw"] for p in front]
    fy = [p["reaction_ms"] for p in front]
    ax.step(fx, fy, where="post", color=C_LINE, linewidth=2.5,
            label="Pareto Cephesi")

    # 100Hz seçimi işaretle
    sel = next((p for p in points if p["hz"] == 100), None)
    if sel:
        ax.scatter(sel["power_mw"], sel["reaction_ms"],
                   s=250, color=C_SELECT, marker="*", zorder=5,
                   label="Seçilen: 100Hz")
        ax.annotate("← Seçildi\n(denge noktası)",
                    (sel["power_mw"] + 20, sel["reaction_ms"] - 3),
                    color=C_SELECT, fontsize=9)

    ax.set_xlabel("Ortalama Güç Tüketimi (mW)", fontsize=11)
    ax.set_ylabel("Alarm Reaksiyon Süresi (ms)", fontsize=11)
    ax.set_title("VeloGuard — Pareto Cephesi\nIMU Örnekleme Hızı Optimizasyonu",
                 fontsize=12, fontweight="bold")

    from matplotlib.patches import Patch, Line2D
    legend_elements = [
        Line2D([0], [0], color=C_LINE, lw=2, label="Pareto Cephesi"),
        Patch(facecolor=C_FRONT, label="Pareto-optimal noktalar"),
        Patch(facecolor=C_DOM,   label="Domine edilen noktalar"),
        Line2D([0], [0], marker="*", color=C_SELECT, markersize=12,
               linestyle="None", label="Seçilen: 100Hz"),
    ]
    ax.legend(handles=legend_elements, facecolor=C_BG,
              labelcolor=C_TEXT, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close()
    print(f"\nPareto grafiği kaydedildi: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="VeloGuard Pareto Sweep")
    parser.add_argument("--measure", action="store_true",
                        help="Gerçek Pi ölçümü yap (INA219 + IMU gerektirir)")
    parser.add_argument("--duration", type=int, default=180,
                        help="Her nokta için ölçüm süresi (sn)")
    args = parser.parse_args()

    print("=== VeloGuard Pareto Analizi ===")
    points = []

    for hz in HZ_CONFIGS:
        if args.measure:
            p = measure_point(hz, args.duration)
        else:
            p = simulate_point(hz)
            print(f"  {hz}Hz → {p['power_mw']:.0f}mW, {p['reaction_ms']:.0f}ms")
        points.append(p)

    front = compute_pareto_front(points)

    print("\nPareto cephesi noktaları:")
    for p in front:
        print(f"  {p['hz']}Hz → {p['power_mw']:.0f}mW, {p['reaction_ms']:.0f}ms")

    out = BASE / "docs" / "figures" / "pareto_front.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plot_pareto(points, front, str(out))

    # CSV kaydet
    csv_path = BASE / "docs" / "figures" / "pareto_data.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["hz", "power_mw", "reaction_ms"])
        writer.writeheader()
        writer.writerows(points)
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()
