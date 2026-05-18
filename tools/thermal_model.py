"""
tools/thermal_model.py — Pi CPU Termal Modelleme
================================================
Pi'nın CPU sıcaklık eğrisini ölçer, RC termal modele fit eder.
R_th (termal direnç), C_th (termal kapasite) ve τ (zaman sabiti) çıkarır.

Kullanım:
  python3 tools/thermal_model.py --measure   (Pi'da çalıştır, 30dk)
  python3 tools/thermal_model.py             (simüle edilmiş veri + fit)

Çıktı: docs/figures/thermal_model.png

ÇALIŞTIĞI YER: Pi (ölçüm) veya PC (simülasyon)
"""

import sys
import math
import time
import csv
import argparse
import random
from pathlib import Path
from typing import List, Tuple

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))


def read_cpu_temp() -> float:
    """Pi CPU sıcaklığını okur."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return int(f.read().strip()) / 1000.0
    except FileNotFoundError:
        return None


def read_ambient_temp() -> float:
    """DHT22'den ortam sıcaklığı okur (yoksa sabit döner)."""
    try:
        import adafruit_dht, board  # type: ignore
        dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
        return dht.temperature
    except Exception:
        return 22.0


def exponential_model(t: float, T_inf: float, T0: float, tau: float) -> float:
    """T(t) = T_inf + (T0 - T_inf) * exp(-t/tau)"""
    return T_inf + (T0 - T_inf) * math.exp(-t / tau)


def fit_rc_model(times: List[float], temps: List[float]) -> Tuple[float, float, float]:
    """Basit yöntemle RC model parametrelerini fit eder."""
    T_amb = min(temps[:5]) if len(temps) >= 5 else 22.0
    T_inf = max(temps)
    T0 = temps[0]

    # τ'yu iteratif ara
    best_tau = 60.0
    best_err = float("inf")

    for tau_guess in range(10, 600, 5):
        err = sum(
            (exponential_model(t, T_inf, T0, tau_guess) - t_meas) ** 2
            for t, t_meas in zip(times, temps)
        )
        if err < best_err:
            best_err = err
            best_tau = float(tau_guess)

    # R_th ve C_th hesapla (kabaca, güç P_cpu ≈ 1.5W varsayımıyla)
    P_cpu = 1.5  # Watt
    R_th = (T_inf - T_amb) / P_cpu  # °C/W
    C_th = best_tau / R_th           # J/°C

    return R_th, C_th, best_tau


def simulate_heating(
    T_amb: float = 22.0,
    T_idle: float = 42.0,
    T_stress: float = 78.0,
    tau_heat: float = 120.0,
    tau_cool: float = 180.0,
    stress_start: float = 60.0,
    stress_end: float = 1800.0,
    total_time: float = 2700.0,
    dt: float = 30.0,
) -> Tuple[List[float], List[float]]:
    """Isınma ve soğuma eğrisi simülasyonu."""
    times, temps = [], []
    T = T_idle
    t = 0.0
    while t <= total_time:
        if t < stress_start:
            T_target = T_idle
            tau = tau_cool
        elif t < stress_end:
            T_target = T_stress
            tau = tau_heat
        else:
            T_target = T_idle
            tau = tau_cool

        dT = (T_target - T) / tau * dt
        T += dT + random.gauss(0, 0.3)
        T = max(T_amb, T)
        times.append(t / 60.0)  # dakika cinsinden
        temps.append(round(T, 1))
        t += dt
    return times, temps


def measure_heating(duration_s: int = 1800, out_path: str = None) -> Tuple[List, List]:
    """Pi'da gerçek ısınma ölçümü."""
    import subprocess
    times, temps = [], []
    start = time.time()

    # stress-ng başlat
    print("[thermal] Stress başlatılıyor...")
    stress = subprocess.Popen(["stress-ng", "--cpu", "4", "--timeout", str(duration_s)])

    try:
        f = open(out_path, "w", newline="") if out_path else None
        writer = csv.writer(f) if f else None
        if writer:
            writer.writerow(["time_min", "cpu_temp_c", "ambient_c"])

        while time.time() - start < duration_s:
            elapsed_min = (time.time() - start) / 60.0
            cpu_t = read_cpu_temp()
            amb_t = read_ambient_temp()

            if cpu_t:
                times.append(round(elapsed_min, 2))
                temps.append(cpu_t)
                print(f"  t={elapsed_min:.1f}min  CPU={cpu_t:.1f}°C  Amb={amb_t:.1f}°C")
                if writer:
                    writer.writerow([round(elapsed_min, 2), cpu_t, amb_t])
                    f.flush()
            time.sleep(30)
    finally:
        stress.terminate()
        if f:
            f.close()

    return times, temps


def plot_thermal(times: List[float], temps: List[float],
                 model_temps: List[float],
                 R_th: float, C_th: float, tau: float,
                 stress_start_min: float, stress_end_min: float,
                 out_path: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib bulunamadı.")
        return

    C_BG   = "#1E1E1E"
    C_MEAS = "#42A5F5"
    C_MODEL= "#FFA726"
    C_TEXT = "#EEEEEE"
    C_GRID = "#333333"

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.tick_params(colors=C_TEXT)
    for sp in ax.spines.values():
        sp.set_color(C_GRID)
    ax.grid(True, color=C_GRID, alpha=0.4)

    ax.plot(times, temps, color=C_MEAS, linewidth=2, label="Ölçüm", zorder=3)
    ax.plot(times, model_temps, color=C_MODEL, linewidth=2,
            linestyle="--", label="RC Model (fit)")

    ax.axvspan(stress_start_min, stress_end_min, alpha=0.15,
               color="#F44336", label="Stress dönemi")

    ax.annotate(f"R_th = {R_th:.2f} °C/W\nC_th = {C_th:.1f} J/°C\nτ = {tau:.0f} s",
                xy=(stress_end_min + 1, min(temps) + 5),
                fontsize=10, color=C_TEXT,
                bbox=dict(boxstyle="round", facecolor="#333", alpha=0.8))

    ax.set_xlabel("Zaman (dakika)", color=C_TEXT)
    ax.set_ylabel("Sıcaklık (°C)", color=C_TEXT)
    ax.set_title("VeloGuard — CPU Termal Model", color=C_TEXT,
                 fontsize=12, fontweight="bold")
    ax.legend(facecolor=C_BG, labelcolor=C_TEXT)
    ax.xaxis.label.set_color(C_TEXT)
    ax.yaxis.label.set_color(C_TEXT)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    plt.close()
    print(f"Termal grafik kaydedildi: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="VeloGuard Termal Model")
    parser.add_argument("--measure", action="store_true",
                        help="Pi'da gerçek ölçüm (stress-ng gerektirir)")
    parser.add_argument("--duration", type=int, default=1800)
    args = parser.parse_args()

    print("=== VeloGuard Termal Modelleme ===")

    if args.measure:
        out_csv = str(BASE / "docs" / "thermal_data.csv")
        times, temps = measure_heating(args.duration, out_csv)
        stress_start_min = 1.0
        stress_end_min = args.duration / 60.0
    else:
        print("Simüle edilmiş termal veri kullanılıyor...")
        times, temps = simulate_heating()
        stress_start_min = 1.0
        stress_end_min = 30.0

    R_th, C_th, tau = fit_rc_model(times, temps)
    T_inf = max(temps)
    T0    = temps[0]
    model = [exponential_model(t * 60, T_inf, T0, tau) for t in times]

    print(f"\nRC Model Parametreleri:")
    print(f"  T_idle  = {T0:.1f} °C")
    print(f"  T_max   = {T_inf:.1f} °C")
    print(f"  R_th    = {R_th:.2f} °C/W")
    print(f"  C_th    = {C_th:.1f} J/°C")
    print(f"  τ       = {tau:.0f} s ({tau/60:.1f} dk)")
    print(f"  T_max < 80°C: {'✅' if T_inf < 80 else '❌'}")

    out = BASE / "docs" / "figures" / "thermal_model.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    plot_thermal(times, temps, model, R_th, C_th, tau,
                 stress_start_min, stress_end_min, str(out))


if __name__ == "__main__":
    main()
