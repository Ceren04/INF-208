# 📊 VeloGuard — Sprint 1 Durum Raporu
**Tarih:** 18 Mayıs 2026 (Sprint 2 başlangıcı)  
**Hazırlayan:** Cursor Agent (otomatik)  
**GitHub:** https://github.com/Ceren04/INF-208

---

## ✅ Başarıyla Test Edilen Şeyler

### Donanım Testleri
| Test | Sonuç | Detay |
|------|-------|-------|
| I2C bus tarama | ✅ | `i2cdetect -y 1` → 0x68 görünüyor |
| MPU-6050 WHO_AM_I | ✅ | `0x72` döndü (GY-521 klon, normal) |
| IMU 100Hz veri akışı | ✅ | `az≈+1.01g`, `mag≈0.02g` (hareketsiz baseline) |
| Kalman filtresi | ✅ | Gerçek IMU verisiyle test edildi |
| LED — DISARMED | ✅ | Hepsi kapalı (fiziksel doğrulama) |
| LED — ARMED | ✅ | Yeşil 0.5Hz yavaş yanıp söndü |
| LED — PRE_ALARM | ✅ | Sarı 4Hz hızlı yanıp söndü |
| LED — ALARM | ✅ | Kırmızı 10Hz rapid flash |
| LED — RIDE | ✅ | Yeşil sabit |
| Web UI | ✅ | `http://192.168.102.88:5000` telefondan açıldı |
| ARM butonu | ✅ | FSM DISARMED → ARMED geçişi |
| DISARM butonu | ✅ | FSM → DISARMED |
| RIDE butonu | ✅ | FSM → RIDE |
| Graceful shutdown | ✅ | Ctrl+C → tüm sürücüler temiz kapandı |

### Yazılım Testleri
| Test | Sonuç |
|------|-------|
| `sudo python3 -m firmware.main` çalışıyor | ✅ |
| FSM ARMED → PRE_ALARM → ALARM geçişi | ✅ (logda görüldü) |
| PAM8403 alarm sireni başlatıldı | ✅ (log: "Alarm sireni başlatıldı") |
| TaskManager 6 task başlatıldı | ✅ |
| Watchdog başlatıldı | ✅ |
| Web UI Flask başlatıldı | ✅ |

---

## ⚠️ Bilinen Sorunlar

### 1. IMU [Errno 5] Input/Output Error
```
[WARNING] IMU okuma hatası: [Errno 5] Input/output error
```
**Neden:** Gevşek breadboard kablosu — I2C başarıyla başlıyor ama sürekli okumada hat kaybolabiliyor.  
**Çözüm:** Lehim veya daha sağlam kablo bağlantısı. I2C baudrate 50kHz'e düşürüldü (kısmen yardımcı oluyor).  
**Etki:** IMU okuma kesilince hareket 0'a düşüyor → eşik mantığı PRE_ALARM tetikleyebiliyor.

### 2. Reed Switch "Failed to add edge detection"
```
[ERROR] Reed switch başlatılamadı: Failed to add edge detection
```
**Neden:** GPIO27 önceki oturumdan kirli, kernel GPIO state sıfırlanmamış.  
**Çözüm:** Pi reboot sonrası temiz başlıyor — ama reboot yapılmadan aynı sorun tekrar çıkıyor.  
**Geçici çözüm:** Her oturumda `sudo systemctl restart pigpiod` veya Pi yeniden başlatma.

### 3. Telegram "Unauthorized"
```
[WARNING] Telegram başlatılamadı: Unauthorized
```
**Neden:** `.env` dosyasında placeholder token var (`123456789:ABCdef...`).  
**Çözüm:** Gerçek BotFather token'ı `.env`'e girilmeli.

---

## 📦 Implement Edildi Ama Test Edilmedi

| Modül | Durum | Ne Gerekiyor |
|-------|-------|-------------|
| `firmware/drivers/reed_driver.py` | Kod hazır | Tamper simülasyonu (mıknatıs uzaklaştırma) |
| `firmware/drivers/pam8403_driver.py` | Kod hazır, init OK | Hoparlörü bağla ve alarm sesi fiziksel duyulmalı |
| `firmware/drivers/camera_driver.py` | Kod hazır | Pi Camera CSI bağlantısı + `libcamera-still` test |
| `firmware/drivers/dht_driver.py` | Kod hazır | DHT22 GPIO4'e bağla |
| `firmware/drivers/ina219_driver.py` | Kod hazır | INA219 I2C 0x40'a bağla |
| `firmware/comm/telegram_bot.py` | Kod hazır | Gerçek token `.env`'e gir |
| `firmware/comm/mqtt.py` | Kod hazır | Mosquitto broker başlat |
| `tools/mock_drivers.py` | Kod hazır | `python3 tools/mock_drivers.py` |

---

## 🗂️ Yazılım Yapısı — Mevcut Durum

```
firmware/
├── config.py           ✅ implement
├── main.py             ✅ implement + ÇALIŞIYOR
├── fsm.py              ✅ implement + ÇALIŞIYOR
├── shared_state.py     ✅ implement
├── task_manager.py     ✅ implement
├── watchdog.py         ✅ implement
├── motion_detector.py  ✅ implement
├── drivers/
│   ├── base_sensor.py  ✅
│   ├── imu_driver.py   ✅ ÇALIŞIYOR (kablo sorunu var)
│   ├── led_driver.py   ✅ ÇALIŞIYOR
│   ├── reed_driver.py  ✅ (GPIO conflict sorunu)
│   ├── pam8403_driver.py ✅ (hoparlör testi yapılmadı)
│   ├── camera_driver.py  ✅ (bağlı değil)
│   ├── dht_driver.py     ✅ (bağlı değil)
│   └── ina219_driver.py  ✅ (bağlı değil)
├── algorithms/
│   ├── kalman.py           ✅ ÇALIŞIYOR
│   └── adaptive_threshold.py ✅
├── comm/
│   ├── web_ui.py       ✅ ÇALIŞIYOR
│   ├── telegram_bot.py ✅ (token gerekli)
│   └── mqtt.py         ✅
└── rtos/
    └── prio_inh_demo.c ⚠️ SADECE İSKELET — implement edilmedi
```

---

## 📋 Sprint 2 Görev Listesi (18-22 Mayıs)

### 🔴 Kritik (19 Mayıs deadline)
- [ ] IMU kablo bağlantısını sağlamlaştır (lehim veya farklı kablo)
- [ ] Reed switch GPIO conflict çözümü (kalıcı fix)
- [ ] IMU → FSM event bağlantısını fiziksel test et (bisiklet salla → ALARM)
- [ ] **19 Mayıs: Donanım prototipi hocanın milestone'u**

### 🟡 Önemli
- [ ] Telegram gerçek token → alarm bildirimi test
- [ ] PAM8403 hoparlör bağlantısı → alarm sesi fiziksel test
- [ ] Pi Camera CSI bağlantısı → `libcamera-still -o test.jpg`
- [ ] DHT22 bağlantısı → sıcaklık okuması
- [ ] `python3 tools/mock_drivers.py` → tam demo senaryosu
- [ ] `pytest tests/` → birim testler

### 🟢 Sprint 2 sonu hedefi
- [ ] FSM + tüm sensörler entegre çalışıyor (30 dk kesintisiz)
- [ ] Kamera + Telegram alarm fotoğrafı
- [ ] Web UI üzerinden tam kontrol

---

## 🔬 Sprint 3-4 için Bekleyen İşler

### RTOS / Priority Inheritance (Sprint 3 — 26 Mayıs deadline ⭐⭐⭐)
- [ ] `firmware/rtos/hello_rt.c` — SCHED_FIFO 3 thread
- [ ] `firmware/rtos/prio_inh_demo.c` — tam implement (şu an boş iskelet)
- [ ] `firmware/rtos/imu_task.c` — IMU okuma C'ye port
- [ ] `firmware/rtos/fsm_task.c` — FSM logic C'ye port
- [ ] PRIO_INHERIT vs PRIO_NONE ölçümü → grafik
- [ ] PREEMPT-RT kernel doğrulama (`uname -a | grep PREEMPT`)

### Metrikler (Sprint 4 — 2 Haziran deadline)
- [ ] WCET tablosu (10+ task için min/avg/max µs)
- [ ] INA219 enerji ölçümü (state bazlı W tüketimi)
- [ ] Termal model (R_th, C_th, τ)
- [ ] Pareto cephesi (enerji vs reaksiyon süresi, IMU Hz parametreli)

### Modelleme (rapor için)
- [ ] StateChart — draw.io (5 durum + TAMPER)
- [ ] Petri ağı — draw.io
- [ ] UPPAAL zamanlı otomat

---

## 📌 Hızlı Başlangıç (Pi'ya bağlanınca)

```bash
# SSH
ssh sena@<PI_IP>

# Sistemi başlat
cd ~/veloguard && sudo venv/bin/python3 -m firmware.main

# IMU tek test
cd ~/veloguard && source venv/bin/activate
python3 -c "
from firmware.drivers.imu_driver import IMUDriver; import time
imu = IMUDriver(); imu.initialize()
for _ in range(10): d = imu.read(); print(f'mag={imu.compute_magnitude(d[\"ax\"],d[\"ay\"],d[\"az\"]):.4f}g') if d else None; time.sleep(0.1)
"

# GPIO sıfırla (reed fix için)
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.cleanup()"

# Mock demo (donanimsiz test)
python3 tools/mock_drivers.py
```
