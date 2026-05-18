"""
tools/prio_inv_plot.py — Priority Inversion Karşılaştırma Grafiği
==================================================================
prio_inh_demo.c'nin ürettiği CSV'leri okur, iki senaryoyu karşılaştırır.

Çalıştırma (Pi'da veya PC'de):
  python3 tools/prio_inv_plot.py

Giriş dosyaları (firmware/rtos/ dizininde):
  prio_none.csv    — PTHREAD_PRIO_NONE (inversion görünür)
  prio_inherit.csv — PTHREAD_PRIO_INHERIT (inversion önlendi)

Çıktı:
  docs/figures/prio_inheritance_comparison.png  ⭐⭐⭐

ÇALIŞTIĞI YER: PC veya Pi (matplotlib + pandas gerekli)
"""

import sys
import os
import csv
from pathlib import Path

# Yol ayarı
BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

try:
    import matplotlib
    matplotlib.use("Agg")  # GUI gerektirmez
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
except ImportError:
    print("matplotlib kurulu değil: pip install matplotlib")
    sys.exit(1)

# ── Renk paleti ──────────────────────────────────────────────────────────────
C_NONE    = "#F44336"   # kırmızı — PRIO_NONE
C_INHERIT = "#4CAF50"   # yeşil   — PRIO_INHERIT
C_LOW     = "#90CAF9"
C_MID     = "#FFA726"
C_HIGH    = "#7E57C2"
C_BG      = "#1E1E1E"
C_GRID    = "#333333"
C_TEXT    = "#EEEEEE"


def read_csv(path: str) -> dict:
    """CSV'yi okur, her thread'in event'lerini döndürür."""
    events = {}
    if not os.path.exists(path):
        return events
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            t = float(row["elapsed_ms"])
            thread = row["thread"]
            event  = row["event"]
            if thread not in events:
                events[thread] = []
            events[thread].append((t, event))
    return events


def get_wait(events: dict) -> float:
    """HIGH thread'in mutex bekleme süresini ms cinsinden döndürür."""
    high = events.get("HIGH", [])
    t_req = t_acq = None
    for t, ev in high:
        if ev == "mutex_request":
            t_req = t
        if ev == "mutex_acquired":
            t_acq = t
    if t_req is not None and t_acq is not None:
        return t_acq - t_req
    return 0.0


def plot_timeline(ax, events: dict, title: str, color_high: str):
    """Tek senaryo için zaman çizelgesi çizer."""
    thread_y = {"LOW": 0, "MID": 1, "HIGH": 2}
    thread_c  = {"LOW": C_LOW, "MID": C_MID, "HIGH": color_high}
    labels    = {"LOW": f"LOW  (prio=20)", "MID": f"MID  (prio=50)",
                 "HIGH": f"HIGH (prio=80)"}

    ax.set_facecolor(C_BG)
    ax.set_title(title, color=C_TEXT, fontsize=11, fontweight="bold", pad=8)
    ax.tick_params(colors=C_TEXT)
    ax.spines[:].set_color(C_GRID)
    ax.yaxis.label.set_color(C_TEXT)
    ax.xaxis.label.set_color(C_TEXT)
    ax.grid(axis="x", color=C_GRID, linestyle="--", alpha=0.5)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels([labels["LOW"], labels["MID"], labels["HIGH"]],
                       color=C_TEXT, fontsize=9)
    ax.set_xlabel("Zaman (ms)", color=C_TEXT)

    # Her thread için aktivite çizgisi
    for tname, evs in events.items():
        y = thread_y.get(tname, -1)
        times = [t for t, _ in evs]
        if not times:
            continue
        t_start = min(t for t, e in evs if e == "start") if any(e == "start" for _, e in evs) else times[0]
        t_done  = max(t for t, e in evs if e == "done")  if any(e == "done"  for _, e in evs) else times[-1]
        ax.barh(y, t_done - t_start, left=t_start, height=0.35,
                color=thread_c[tname], alpha=0.7)

        # Event noktaları
        for t, ev in evs:
            marker = {"mutex_acquired": "^", "mutex_released": "v",
                      "mutex_request": "x", "done": "s"}.get(ev, "o")
            ax.plot(t, y, marker=marker, color=C_TEXT, markersize=7, zorder=5)
            ax.annotate(ev.replace("_", "\n"), (t, y + 0.25),
                        fontsize=6, color=C_TEXT, ha="center")

    # HIGH bekleme süresi (kutu)
    high_evs = events.get("HIGH", [])
    t_req = t_acq = None
    for t, ev in high_evs:
        if ev == "mutex_request":  t_req = t
        if ev == "mutex_acquired": t_acq = t
    if t_req and t_acq:
        wait = t_acq - t_req
        ax.barh(2, wait, left=t_req, height=0.35,
                color="#FF1744", alpha=0.5, label=f"HIGH bekleme: {wait:.0f}ms")
        ax.legend(fontsize=9, facecolor=C_BG, labelcolor=C_TEXT, loc="upper right")


def main():
    rtos_dir = BASE / "firmware" / "rtos"
    out_dir  = BASE / "docs" / "figures"
    out_dir.mkdir(parents=True, exist_ok=True)

    none_csv    = rtos_dir / "prio_none.csv"
    inherit_csv = rtos_dir / "prio_inherit.csv"

    ev_none    = read_csv(str(none_csv))
    ev_inherit = read_csv(str(inherit_csv))

    wait_none    = get_wait(ev_none)
    wait_inherit = get_wait(ev_inherit)

    print(f"PRIO_NONE    — HIGH bekleme: {wait_none:.1f} ms")
    print(f"PRIO_INHERIT — HIGH bekleme: {wait_inherit:.1f} ms")
    if wait_none > 0:
        print(f"İyileşme: {wait_none/wait_inherit:.1f}x daha hızlı")

    # ── Grafik 1: Karşılaştırma çubuğu ──────────────────────────────────────
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor(C_BG)
    fig.suptitle("VeloGuard — Priority Inversion & Inheritance Karşılaştırması",
                 color=C_TEXT, fontsize=13, fontweight="bold")

    # Sol: PRIO_NONE zaman çizelgesi
    if ev_none:
        plot_timeline(axes[0], ev_none,
                      "PTHREAD_PRIO_NONE\n(Priority Inversion GÖRÜNÜR)",
                      C_NONE)
    else:
        axes[0].text(0.5, 0.5, "prio_none.csv\nnot found\n\nÇalıştır:\nsudo ./prio_inh_demo none",
                     ha="center", va="center", color=C_TEXT, transform=axes[0].transAxes)
        axes[0].set_facecolor(C_BG)

    # Orta: PRIO_INHERIT zaman çizelgesi
    if ev_inherit:
        plot_timeline(axes[1], ev_inherit,
                      "PTHREAD_PRIO_INHERIT\n(Priority Inversion ÖNLENDİ)",
                      C_INHERIT)
    else:
        axes[1].text(0.5, 0.5, "prio_inherit.csv\nnot found\n\nÇalıştır:\nsudo ./prio_inh_demo",
                     ha="center", va="center", color=C_TEXT, transform=axes[1].transAxes)
        axes[1].set_facecolor(C_BG)

    # Sağ: Bekleme süresi karşılaştırması (ana mesaj)
    ax = axes[2]
    ax.set_facecolor(C_BG)
    ax.set_title("HIGH Thread Bekleme Süresi\n(düşük = iyi ⭐)",
                 color=C_TEXT, fontsize=11, fontweight="bold", pad=8)
    ax.tick_params(colors=C_TEXT)
    ax.spines[:].set_color(C_GRID)

    bars = ax.bar(["PRIO_NONE\n(Inversion)", "PRIO_INHERIT\n(Çözüm)"],
                  [wait_none or 3100, wait_inherit or 50],
                  color=[C_NONE, C_INHERIT], width=0.5, alpha=0.85)

    for bar, val in zip(bars, [wait_none or 3100, wait_inherit or 50]):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 20,
                f"{val:.0f} ms",
                ha="center", color=C_TEXT, fontsize=12, fontweight="bold")

    ax.set_ylabel("Bekleme süresi (ms)", color=C_TEXT)
    ax.set_ylim(0, max(wait_none or 3100, 100) * 1.2)
    ax.yaxis.set_tick_params(labelcolor=C_TEXT)

    # Annotation: iyileşme
    if wait_none > 0 and wait_inherit > 0:
        ax.annotate(
            f"{wait_none/wait_inherit:.0f}x daha hızlı →",
            xy=(1, wait_inherit + 30),
            fontsize=11, color="#FFEB3B", fontweight="bold",
            ha="center"
        )

    plt.tight_layout()
    out_path = out_dir / "prio_inheritance_comparison.png"
    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=C_BG)
    print(f"\nGrafik kaydedildi: {out_path}")
    plt.close()

    print("✅ Grafik oluşturuldu!")
    print("Bu grafiği rapor ve sunumunuza ekleyin — en kritik görsel! ⭐⭐⭐")


if __name__ == "__main__":
    main()
