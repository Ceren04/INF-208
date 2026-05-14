# VeloGuard 🚴

**Akıllı Bisiklet / Scooter / Motosiklet Hırsızlık Önleme Sistemi**  
*INF 208 Gömülü Sistemler — TAU Proje Ödevi*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Proje Özeti

VeloGuard, park edilmiş araçları korumak için Raspberry Pi 3B üzerinde çalışan gerçek zamanlı bir güvenlik sistemidir. MPU-6050 IMU, Pi Camera, Reed switch ve DHT22 sensörlerini bir arada kullanarak sahte alarm oranını minimize ederken gerçek müdahale girişimlerini anında tespit eder.

**Ana Özellikler:**
- 5-durumlu FSM (Disarmed → Armed → Pre-Alarm → Alarm → Ride)
- Adaptif Kalman filtresi ile gürültü bastırma
- PREEMPT-RT Linux + SCHED_FIFO gerçek-zamanlı zamanlayıcı
- PTHREAD_PRIO_INHERIT ile Priority Inversion önleme (kanıtlı)
- Telegram bot ile anlık bildirim + fotoğraf
- Flask tabanlı mobil uyumlu web arayüzü
- WCET / Enerji / Termal / Pareto metrik analizi

---

## Donanım Listesi (BOM)

| Bileşen | Model | Adet | Bağlantı |
|---------|-------|------|----------|
| Mikro bilgisayar | Raspberry Pi 3B | 1 | — |
| IMU | MPU-6050 (GY-521) | 1 | I2C (0x68) |
| Kamera | Pi Camera v2 | 1 | CSI |
| Sıcaklık | DHT22 | 1 | GPIO4 |
| Akım ölçer | INA219 | 1 | I2C (0x40) |
| Reed switch | KY-021 | 1 | GPIO27 |
| Ses amplifikatörü | PAM8403 | 1 | GPIO18 (PWM) |
| LED Kırmızı | — | 1 | GPIO5 |
| LED Sarı | — | 1 | GPIO6 |
| LED Yeşil | — | 1 | GPIO13 |
| Pil | 18650 Li-ion | 2 | MT3608 boost |

---

## Dizin Yapısı

```
veloguard/
├── firmware/               # Ana yazılım paketi
│   ├── config.py           # Tüm sabitler (GPIO, eşikler, parametreler)
│   ├── main.py             # Giriş noktası
│   ├── fsm.py              # 5-durumlu sonlu durum makinesi
│   ├── shared_state.py     # Thread-safe sensör veri deposu
│   ├── task_manager.py     # RTOS thread yöneticisi
│   ├── watchdog.py         # Yazılım watchdog
│   ├── motion_detector.py  # Adaptif hareket dedektörü
│   ├── drivers/            # Donanım sürücüleri
│   │   ├── base_sensor.py
│   │   ├── imu_driver.py
│   │   ├── camera_driver.py
│   │   ├── reed_driver.py
│   │   ├── dht_driver.py
│   │   ├── ina219_driver.py
│   │   ├── pam8403_driver.py
│   │   └── led_driver.py
│   ├── algorithms/
│   │   ├── kalman.py       # 1D Kalman filtresi
│   │   └── adaptive_threshold.py
│   ├── comm/               # İletişim katmanı
│   │   ├── telegram_bot.py
│   │   ├── web_ui.py
│   │   └── mqtt.py
│   └── rtos/               # C gerçek-zamanlı çekirdek
│       ├── prio_inh_demo.c # Priority Inversion deneyi ⭐
│       ├── imu_task.c
│       └── fsm_task.c
├── tests/                  # Birim testler
├── tools/                  # Geliştirici araçları
│   ├── sensor_test_all.py
│   ├── imu_live_plot.py
│   ├── energy_logger.py
│   ├── wcet_analyzer.py
│   ├── thermal_model.py
│   ├── pareto_sweep.py
│   └── prio_inv_plot.py
├── docs/                   # Dokümantasyon ve görseller
│   └── figures/
├── hardware/               # Devre şeması, BOM, STL
└── presentation/           # Sunum, demo video
```

---

## Kurulum (Raspberry Pi 3B)

### 1. Bağımlılıkları Yükle
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git i2c-tools

# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Arayüzleri Etkinleştir
```bash
sudo raspi-config
# Interface Options → I2C → Enable
# Interface Options → Camera → Enable
# Interface Options → SPI → Enable (opsiyonel)
```

### 3. Ortam Değişkenlerini Ayarla
```bash
cp .env.example .env
nano .env   # TELEGRAM_TOKEN ve TELEGRAM_CHAT_ID girin
```

### 4. Log Dizinini Oluştur
```bash
sudo mkdir -p /var/log/veloguard
sudo chown $USER:$USER /var/log/veloguard
```

### 5. Sistemi Başlat
```bash
# Root gerektirir (SCHED_FIFO için)
sudo python3 -m firmware.main
```

---

## Sensör Testi
```bash
# Tüm sensörleri ayrı ayrı test et
python3 tools/sensor_test_all.py

# Canlı IMU grafiği
python3 tools/imu_live_plot.py

# IMU I2C erişim testi (tek satır)
python3 -c "import smbus2; b=smbus2.SMBus(1); print('OK' if b.read_byte_data(0x68,0x75)==0x68 else 'FAIL')"
```

---

## Priority Inheritance Kanıtı
```bash
# C kodu derle
cd firmware/rtos
gcc -O2 -o prio_inh_demo prio_inh_demo.c -lpthread -lrt
sudo ./prio_inh_demo

# Grafik çiz
python3 tools/prio_inv_plot.py
```

---

## Katkı
Bkz. [CONTRIBUTING.md](CONTRIBUTING.md)

## Lisans
MIT — bkz. [LICENSE](LICENSE)
