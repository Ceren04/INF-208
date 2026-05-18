"""
tools/imu_live_plot.py — IMU Canlı Grafik
==========================================
MPU-6050'den 100Hz veri okuyup matplotlib ile canlı grafik çizer.
Bisiklet sallama testinde eşik geçişlerini görselleştirir.

Çalıştırma (Pi'da):
  cd ~/veloguard && source venv/bin/activate
  python3 tools/imu_live_plot.py

ÇALIŞTIĞI YER: Raspberry Pi 3B (ekran veya VNC gerektirir)
"""

import sys
import time
import collections
import threading

# matplotlib backend — Pi'da Tkinter yoksa Agg kullan
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sys.path.insert(0, "/home/sena/veloguard")

from firmware.drivers.imu_driver import IMUDriver
from firmware.algorithms.kalman import KalmanFilter1D
from firmware.config import IMUConfig

# ── Ayarlar ──────────────────────────────────────────────────────────────────
WINDOW_S   = 10       # Grafikte kaç saniyelik veri gösterilsin
SAMPLE_HZ  = 50       # Grafik için yeterli, 100Hz yerine
THRESHOLD_LOW  = IMUConfig.THRESHOLD_LOW_G
THRESHOLD_HIGH = IMUConfig.THRESHOLD_HIGH_G
MAX_POINTS = WINDOW_S * SAMPLE_HZ

# ── Paylaşılan veri tamponu ───────────────────────────────────────────────────
times   = collections.deque(maxlen=MAX_POINTS)
raw_mag = collections.deque(maxlen=MAX_POINTS)
flt_mag = collections.deque(maxlen=MAX_POINTS)
ax_data = collections.deque(maxlen=MAX_POINTS)
ay_data = collections.deque(maxlen=MAX_POINTS)
az_data = collections.deque(maxlen=MAX_POINTS)
_lock = threading.Lock()
_running = True

imu = IMUDriver()
kf  = KalmanFilter1D()


def reader_thread():
    """Arka planda IMU okur."""
    global _running
    interval = 1.0 / SAMPLE_HZ
    t0 = time.time()
    while _running:
        t_start = time.monotonic()
        d = imu.read()
        if d:
            mag = imu.compute_magnitude(d["ax"], d["ay"], d["az"])
            filtered = kf.update(mag)
            with _lock:
                now = time.time() - t0
                times.append(now)
                raw_mag.append(mag)
                flt_mag.append(filtered)
                ax_data.append(d["ax"])
                ay_data.append(d["ay"])
                az_data.append(d["az"])
        elapsed = time.monotonic() - t_start
        time.sleep(max(0, interval - elapsed))


def build_figure():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7))
    fig.suptitle("VeloGuard — IMU Canlı Grafik", fontsize=13, fontweight="bold")

    # Üst: hareket büyüklüğü
    line_raw,  = ax1.plot([], [], color="#90CAF9", linewidth=1, label="Ham magnitude")
    line_filt, = ax1.plot([], [], color="#1565C0", linewidth=2, label="Kalman filtrelenmiş")
    line_lo    = ax1.axhline(THRESHOLD_LOW,  color="#FFA000", linestyle="--",
                             linewidth=1.5, label=f"Eşik düşük ({THRESHOLD_LOW}g)")
    line_hi    = ax1.axhline(THRESHOLD_HIGH, color="#D32F2F", linestyle="--",
                             linewidth=1.5, label=f"Eşik yüksek ({THRESHOLD_HIGH}g)")
    ax1.set_ylabel("Hareket büyüklüğü (g)")
    ax1.set_ylim(-0.05, 2.0)
    ax1.legend(loc="upper right", fontsize=8)
    ax1.grid(True, alpha=0.3)
    status_text = ax1.text(0.02, 0.92, "DISARMED", transform=ax1.transAxes,
                           fontsize=11, fontweight="bold", color="gray")

    # Alt: 3 eksen ivme
    line_ax, = ax2.plot([], [], color="#EF5350", linewidth=1, label="ax")
    line_ay, = ax2.plot([], [], color="#66BB6A", linewidth=1, label="ay")
    line_az, = ax2.plot([], [], color="#42A5F5", linewidth=1, label="az")
    ax2.set_ylabel("İvme (g)")
    ax2.set_xlabel("Zaman (s)")
    ax2.set_ylim(-2.5, 2.5)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.grid(True, alpha=0.3)

    def update(_frame):
        with _lock:
            if len(times) < 2:
                return line_raw, line_filt, line_ax, line_ay, line_az, status_text

            t  = list(times)
            rm = list(raw_mag)
            fm = list(flt_mag)
            axd= list(ax_data)
            ayd= list(ay_data)
            azd= list(az_data)

        t0 = t[-1]
        t_rel = [x - t0 + WINDOW_S for x in t]

        line_raw.set_data(t_rel, rm)
        line_filt.set_data(t_rel, fm)
        line_ax.set_data(t_rel, axd)
        line_ay.set_data(t_rel, ayd)
        line_az.set_data(t_rel, azd)

        for ax_obj in (ax1, ax2):
            ax_obj.set_xlim(0, WINDOW_S)

        # Durum etiketi
        cur = fm[-1] if fm else 0
        if cur > THRESHOLD_HIGH:
            status_text.set_text("🚨 ALARM!")
            status_text.set_color("#D32F2F")
        elif cur > THRESHOLD_LOW:
            status_text.set_text("⚠ PRE-ALARM")
            status_text.set_color("#FFA000")
        else:
            status_text.set_text("✓ Normal")
            status_text.set_color("#388E3C")

        return line_raw, line_filt, line_ax, line_ay, line_az, status_text

    ani = animation.FuncAnimation(fig, update, interval=100, blit=True)
    return fig, ani


if __name__ == "__main__":
    print("IMU başlatılıyor...")
    if not imu.initialize():
        print("IMU başlatılamadı!")
        sys.exit(1)

    print(f"Grafik açılıyor — {WINDOW_S}s pencere, {SAMPLE_HZ}Hz")
    print("Pencereyi kapatarak çıkın.")

    t = threading.Thread(target=reader_thread, daemon=True)
    t.start()

    fig, ani = build_figure()
    try:
        plt.tight_layout()
        plt.show()
    finally:
        _running = False
        imu.cleanup()
        print("Kapatıldı.")
