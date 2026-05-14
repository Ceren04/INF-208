"""
tools/plot_style.py — Grafik Stil Ayarları
==========================================
Tüm grafiklerin tutarlı görünmesi için ortak matplotlib ayarları.
Her grafik dosyası başında: from tools.plot_style import apply_style

ÇALIŞTIĞI YER: PC (geliştirici makinesi)
"""

import matplotlib.pyplot as plt
import matplotlib as mpl


COLORS = {
    "primary":   "#2196F3",   # mavi
    "danger":    "#F44336",   # kırmızı (alarm)
    "warning":   "#FF9800",   # turuncu (pre-alarm)
    "success":   "#4CAF50",   # yeşil (armed/OK)
    "neutral":   "#9E9E9E",   # gri
    "highlight": "#9C27B0",   # mor (pareto cephesi)
    "prio_none":    "#F44336",
    "prio_inherit": "#4CAF50",
}


def apply_style():
    """Tüm grafiklere uygulanacak global matplotlib ayarları."""
    mpl.rcParams.update({
        "figure.dpi":         150,
        "figure.figsize":     (10, 5),
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.grid":          True,
        "grid.alpha":         0.3,
        "font.family":        "DejaVu Sans",
        "font.size":          11,
        "axes.titlesize":     13,
        "axes.labelsize":     11,
        "legend.fontsize":    10,
        "lines.linewidth":    2.0,
        "lines.markersize":   6,
    })


def save_fig(fig: plt.Figure, path: str, tight: bool = True):
    """Grafiği yüksek çözünürlükte kaydeder."""
    if tight:
        fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"[plot_style] Grafik kaydedildi: {path}")
