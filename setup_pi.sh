#!/bin/bash
# =============================================================================
# setup_pi.sh — VeloGuard Raspberry Pi 3B Kurulum Scripti
# =============================================================================
# Kullanım: bash setup_pi.sh
# Root gerektirmez; sudo gereken adımlar kendi içlerinde sudo kullanır.

set -e   # herhangi bir hata → dur

VELOGUARD_DIR="$HOME/veloguard"
LOG_DIR="/var/log/veloguard"
VENV_DIR="$VELOGUARD_DIR/venv"

echo "╔══════════════════════════════════════════════╗"
echo "║   VeloGuard — Pi Kurulum Scripti             ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

# ── 1. Sistem paketleri ──────────────────────────────────────────────────────
echo "[1/8] Sistem paketleri yükleniyor..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3-pip python3-venv python3-dev \
    git i2c-tools build-essential \
    libatlas-base-dev libopenblas-dev \
    libcamera-dev python3-libcamera \
    mosquitto mosquitto-clients \
    stress-ng rt-tests \
    > /dev/null
echo "      Tamamlandı."

# ── 2. Raspberry Pi arayüzleri ───────────────────────────────────────────────
echo "[2/8] I2C ve diğer arayüzler etkinleştiriliyor..."
sudo raspi-config nonint do_i2c 0       # I2C AÇ
sudo raspi-config nonint do_camera 0    # Camera AÇ
sudo raspi-config nonint do_spi 0       # SPI AÇ (opsiyonel)
# GPIO (DHT22) için dtoverlay
if ! grep -q "dtoverlay=w1-gpio" /boot/config.txt 2>/dev/null; then
    echo "dtoverlay=w1-gpio" | sudo tee -a /boot/config.txt > /dev/null
fi
echo "      Tamamlandı."

# ── 3. Log dizini ────────────────────────────────────────────────────────────
echo "[3/8] Log dizini oluşturuluyor: $LOG_DIR"
sudo mkdir -p "$LOG_DIR"
sudo chown "$USER:$USER" "$LOG_DIR"
echo "      Tamamlandı."

# ── 4. Proje dizini ──────────────────────────────────────────────────────────
echo "[4/8] Proje dizini: $VELOGUARD_DIR"
mkdir -p "$VELOGUARD_DIR"
# Kamera fotoğraf geçici dizini
mkdir -p /tmp/veloguard_photos
echo "      Tamamlandı."

# ── 5. Python sanal ortamı ───────────────────────────────────────────────────
echo "[5/8] Python sanal ortamı oluşturuluyor..."
python3 -m venv "$VENV_DIR" --system-site-packages
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
echo "      Tamamlandı."

# ── 6. Python bağımlılıkları ─────────────────────────────────────────────────
echo "[6/8] Python bağımlılıkları yükleniyor (requirements.txt)..."
if [ -f "$VELOGUARD_DIR/requirements.txt" ]; then
    pip install -r "$VELOGUARD_DIR/requirements.txt" --quiet
    echo "      Tamamlandı."
else
    echo "      UYARI: requirements.txt bulunamadı — bağımlılıklar yüklenmedi."
fi

# ── 7. PREEMPT-RT kernel kontrolü ────────────────────────────────────────────
echo "[7/8] PREEMPT-RT kernel kontrolü..."
KERNEL_VER=$(uname -r)
if uname -a | grep -q "PREEMPT_RT"; then
    echo "      ✅ PREEMPT-RT aktif: $KERNEL_VER"
else
    echo "      ⚠️  PREEMPT-RT YOK — standart kernel: $KERNEL_VER"
    echo "      PREEMPT-RT kurmak için:"
    echo "      https://github.com/kdoren/linux/releases adresinden"
    echo "      Pi 3B için hazır .deb paketi indirin ve kurun."
fi

# ── 8. .env dosyası ──────────────────────────────────────────────────────────
echo "[8/8] .env dosyası kontrolü..."
if [ ! -f "$VELOGUARD_DIR/.env" ]; then
    if [ -f "$VELOGUARD_DIR/.env.example" ]; then
        cp "$VELOGUARD_DIR/.env.example" "$VELOGUARD_DIR/.env"
        echo "      .env.example → .env kopyalandı."
        echo "      ⚠️  LÜTFEN .env dosyasını düzenleyin: nano $VELOGUARD_DIR/.env"
    fi
else
    echo "      .env zaten mevcut."
fi

# ── Özet ─────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   KURULUM TAMAMLANDI                                  ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "Sonraki adımlar:"
echo "  1. Dosyaları Pi'ya kopyalayın:"
echo "     scp -r . pi@<PI_IP>:~/veloguard/"
echo ""
echo "  2. Telegram token'ı ayarlayın:"
echo "     nano $VELOGUARD_DIR/.env"
echo ""
echo "  3. Sensör testi:"
echo "     cd $VELOGUARD_DIR"
echo "     source venv/bin/activate"
echo "     python3 tools/sensor_test_all.py"
echo ""
echo "  4. Sistemi başlatın (root gerektirir):"
echo "     sudo $VENV_DIR/bin/python3 -m firmware.main"
echo ""
echo "  5. PREEMPT-RT kurulumu (gerekirse — yukarıdaki linke bakın)"
echo ""
