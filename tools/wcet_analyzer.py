"""
tools/wcet_analyzer.py — WCET (Worst Case Execution Time) Analizi
==================================================================
GPIO toggle veya clock_gettime() ile ölçülen task sürelerini analiz eder.
Histogram, istatistik ve rapor tablosu üretir.

Kullanım:
  # Pi'da C task'ına enstrüman ekle, CSV üret:
  # wcet_start(task_id) → GPIO/timestamp
  # wcet_stop(task_id)  → delta hesapla, CSV'ye yaz

  # Sonra bu scriptı PC'de çalıştır:
  python3 tools/wcet_analyzer.py [--csv dosya.csv] [--plot]

Çıktı:
  - Terminal: min/avg/max tablosu
  - docs/figures/wcet_histogram.png

ÇALIŞTIĞI YER: PC ve Pi
"""

import sys
import os
import csv
import math
import argparse
import collections
from pathlib import Path
from typing import Dict, List, Optional

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

# ── Örnek/simüle edilmiş WCET verileri ─────────────────────────────────────
# Pi'dan veri gelene kadar gerçekçi simülasyon kullanılır

import random

TASK_BUDGETS_US = {
    "reed_isr":     50,
    "imu_sampling": 1500,
    "fsm_core":     500,
    "kalman":       100,
    "led_update":   200,
    "telegram_send": 10000,
    "web_ui":       5000,
    "logger_write": 2000,
    "dht_read":     5000,
    "ina219_read":  3000,
}

def simulate_wcet_data(task: str, n: int = 1000) -> List[float]:
    """Gerçekçi WCET verisi simüle eder."""
    params = {
        "reed_isr":     (18,  8,  38),
        "imu_sampling": (900, 150, 1420),
        "fsm_core":     (120, 80, 480),
        "kalman":       (15,  10,  60),
        "led_update":   (50,  30, 150),
        "telegram_send":(2500, 3000, 8000),
        "web_ui":       (800, 500, 3000),
        "logger_write": (200, 150, 800),
        "dht_read":     (1200, 500, 3500),
        "ina219_read":  (800, 400, 2000),
    }.get(task, (100, 50, 500))

    mu, sigma, peak = params
    data = []
    for _ in range(n):
        if random.random() < 0.005:  # nadir yüksek latency
            data.append(random.uniform(peak * 0.8, peak * 1.1))
        else:
            v = abs(random.gauss(mu, sigma))
            data.append(min(v, peak))
    return data


def load_csv(path: str) -> Dict[str, List[float]]:
    """CSV formatı: task_name,duration_us"""
    data = collections.defaultdict(list)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data[row["task"]].append(float(row["duration_us"]))
    return dict(data)


def analyze(data: Dict[str, List[float]]) -> List[dict]:
    results = []
    for task, samples in data.items():
        n = len(samples)
        if n == 0:
            continue
        mu     = sum(samples) / n
        sigma  = math.sqrt(sum((x - mu)**2 for x in samples) / max(n-1, 1))
        mn     = min(samples)
        mx     = max(samples)
        budget = TASK_BUDGETS_US.get(task, mx * 1.5)
        ratio  = mx / budget if budget > 0 else 0
        status = "✅" if ratio <= 1.0 else "❌"
        results.append({
            "task":    task,
            "n":       n,
            "min_us":  round(mn, 1),
            "avg_us":  round(mu, 1),
            "max_us":  round(mx, 1),
            "sigma":   round(sigma, 1),
            "budget":  budget,
            "ratio":   round(ratio, 3),
            "status":  status,
        })
    results.sort(key=lambda r: r["ratio"], reverse=True)
    return results


def print_table(results: List[dict]):
    print("\n" + "="*80)
    print("WCET ANALİZ TABLOSU — VeloGuard")
    print("="*80)
    hdr = f"{'Task':<20} {'N':>6} {'Min(µs)':>9} {'Avg(µs)':>9} {'Max(µs)':>9} {'Bütçe':>7} {'Oran':>6} {'OK'}"
    print(hdr)
    print("-"*80)
    for r in results:
        print(f"{r['task']:<20} {r['n']:>6} {r['min_us']:>9} {r['avg_us']:>9} "
              f"{r['max_us']:>9} {r['budget']:>7} {r['ratio']:>6.3f} {r['status']}")
    print("="*80)
    ok = sum(1 for r in results if r["status"] == "✅")
    print(f"Sonuç: {ok}/{len(results)} task bütçe içinde")


def plot_histograms(data: Dict[str, List[float]], out_path: str):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib bulunamadı, grafik atlanıyor.")
        return

    n_tasks = len(data)
    cols = min(3, n_tasks)
    rows = math.ceil(n_tasks / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 3.5))
    fig.patch.set_facecolor("#1E1E1E")
    fig.suptitle("VeloGuard WCET Histogram Analizi", color="white",
                 fontsize=13, fontweight="bold")

    ax_flat = axes.flat if hasattr(axes, "flat") else [axes]

    for ax, (task, samples) in zip(ax_flat, data.items()):
        budget = TASK_BUDGETS_US.get(task, max(samples) * 1.5)
        color = "#4CAF50" if max(samples) <= budget else "#F44336"

        ax.set_facecolor("#2E2E2E")
        ax.hist(samples, bins=40, color=color, alpha=0.8, edgecolor="none")
        ax.axvline(max(samples), color="#FF1744", linestyle="--",
                   label=f"Max: {max(samples):.0f}µs")
        ax.axvline(budget, color="#FFA726", linestyle=":",
                   label=f"Bütçe: {budget:.0f}µs")
        ax.set_title(task, color="white", fontsize=9)
        ax.tick_params(colors="white")
        ax.legend(fontsize=7, facecolor="#1E1E1E", labelcolor="white")
        for sp in ax.spines.values():
            sp.set_color("#444")

    for ax in list(ax_flat)[n_tasks:]:
        ax.set_visible(False)

    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#1E1E1E")
    plt.close()
    print(f"\nHistogram kaydedildi: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="VeloGuard WCET Analyzer")
    parser.add_argument("--csv",  help="CSV dosyası (task,duration_us)")
    parser.add_argument("--plot", action="store_true", help="Histogram çiz")
    parser.add_argument("--sim",  action="store_true",
                        help="Simüle edilmiş veri kullan (varsayılan)")
    args = parser.parse_args()

    if args.csv and os.path.exists(args.csv):
        print(f"CSV yükleniyor: {args.csv}")
        data = load_csv(args.csv)
    else:
        print("Simüle edilmiş WCET verisi kullanılıyor...")
        data = {task: simulate_wcet_data(task) for task in TASK_BUDGETS_US}

    results = analyze(data)
    print_table(results)

    if args.plot or True:  # her zaman grafik üret
        out = BASE / "docs" / "figures" / "wcet_histogram.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        plot_histograms(data, str(out))

    # Markdown tablosu kaydet
    md_path = BASE / "docs" / "figures" / "wcet_table.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# WCET Analiz Tablosu — VeloGuard\n\n")
        f.write("| Task | Min(µs) | Avg(µs) | Max(µs) | Bütçe(µs) | Oran | Durum |\n")
        f.write("|------|---------|---------|---------|-----------|------|-------|\n")
        for r in results:
            f.write(f"| {r['task']} | {r['min_us']} | {r['avg_us']} | "
                    f"{r['max_us']} | {r['budget']} | {r['ratio']} | {r['status']} |\n")
    print(f"Markdown tablo: {md_path}")


if __name__ == "__main__":
    main()
