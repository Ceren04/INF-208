# ✅ VeloGuard — Proje İlerleme Checklist
> Son güncelleme: **18 Mayıs 2026**
> Teslim tarihi: 05 Haziran 2026 14:45

---

## 🔧 Yazılım Altyapısı

### Temel Modüller
- [x] `firmware/config.py` — merkezi sabitler
- [x] `firmware/fsm.py` — 5-durumlu FSM + TAMPER + ARM_DELAY ✅ ÇALIŞIYOR
- [x] `firmware/shared_state.py` — thread-safe veri deposu + flush_events()
- [x] `firmware/motion_detector.py` — adaptif hareket dedektörü
- [x] `firmware/task_manager.py` — RTOS thread yöneticisi ✅ ÇALIŞIYOR
- [x] `firmware/watchdog.py` — yazılım watchdog ✅ ÇALIŞIYOR
- [x] `firmware/main.py` — ana giriş, graceful shutdown ✅ ÇALIŞIYOR

### Sürücüler
- [x] `firmware/drivers/base_sensor.py`
- [x] `firmware/drivers/imu_driver.py` ✅ Pi'da çalışıyor (0x72 klon desteği + bus recovery)
- [x] `firmware/drivers/led_driver.py` ✅ Pi'da çalışıyor (tüm FSM pattern'ları test edildi)
- [x] `firmware/drivers/reed_driver.py` ✅ gpiozero ile yeniden yazıldı — ÇALIŞIYOR
- [x] `firmware/drivers/pam8403_driver.py` ✅ başlatıldı
- [x] `firmware/drivers/camera_driver.py` — implement edildi (test edilmedi)
- [x] `firmware/drivers/dht_driver.py` — implement edildi (test edilmedi)
- [x] `firmware/drivers/ina219_driver.py` — implement edildi (test edilmedi)

### Algoritmalar
- [x] `firmware/algorithms/kalman.py` ✅ gerçek veriyle test edildi + 10 birim test geçti
- [x] `firmware/algorithms/adaptive_threshold.py` ✅ 8 birim test geçti
- [x] MotionDetector ✅ 9 birim test geçti

### İletişim
- [x] `firmware/comm/web_ui.py` ✅ telefondan test edildi — ARM/DISARM/RIDE/Alarm Durdur çalışıyor
- [x] `firmware/comm/telegram_bot.py` — implement edildi (gerçek token gerekli)
- [x] `firmware/comm/mqtt.py` — implement edildi

### RTOS / C
- [x] `firmware/rtos/hello_rt.c` ✅ derlendi + çalıştı (SCHED_FIFO 3 thread)
- [x] `firmware/rtos/prio_inh_demo.c` ✅ **PRIO_NONE=4900ms vs PRIO_INHERIT=2750ms (1.8x)** ⭐⭐⭐
- [x] `firmware/rtos/imu_task.c` — implement edildi (POSIX shm + PRIO_INHERIT mutex)
- [x] `firmware/rtos/fsm_task.c` — implement edildi (C FSM + shared memory)

---

## 🔌 Donanım

- [x] Raspberry Pi 3B — SSH bağlantısı ✅
- [x] **PREEMPT_RT kernel** `6.12.87+rpt-rpi-v8-rt` ✅ AKTİF
- [x] MPU-6050 (GY-521) — I2C 0x68, WHO_AM_I 0x72 ✅
- [x] LED Kırmızı (GPIO5) ✅
- [x] LED Sarı (GPIO6) ✅
- [x] LED Yeşil (GPIO13) ✅
- [x] Reed switch (GPIO27) ✅ gpiozero ile
- [x] PAM8403 (GPIO18) ✅ başlatıldı
- [ ] Pi Camera — bağlanacak
- [ ] DHT22 (GPIO4) — bağlanacak
- [ ] INA219 (I2C 0x40) — bağlanacak
- [ ] 18650 pil + BMS — bağlanacak

---

## 🧪 Test Durumu

- [x] `pytest tests/ -v` → **54/54 PASSED** ✅
- [x] IMU 100Hz veri akışı — `az≈1.01g`, `mag≈0.02g`
- [x] Kalman filtresi canlı veri ✅
- [x] LED FSM pattern testi (fiziksel) ✅
- [x] Web UI ARM/DISARM/RIDE (telefon) ✅
- [x] `sudo python3 -m firmware.main` — sistem ayakta, graceful shutdown ✅
- [x] FSM geçiş testi — ARMED→PRE_ALARM→ALARM→DISARMED logda görüldü ✅
- [x] Reed switch tamper → gpiozero ile başlatma ✅
- [x] SCHED_FIFO `hello_rt` demo ✅
- [x] **Priority Inheritance deneyi** — PRIO_NONE=4900ms, PRIO_INHERIT=2750ms ✅
- [x] `cyclictest` — Min=4µs, Avg=9µs, Max=83µs (< 100µs hedef) ✅
- [ ] PAM8403 fiziksel ses testi
- [ ] IMU lehim (kablo stabilitesi)
- [ ] DHT22, INA219, Camera fiziksel test
- [ ] Telegram gerçek token
- [ ] 30 dakika kararlılık testi

---

## 📊 Metrikler & Grafikler

- [x] `docs/figures/prio_inheritance_comparison.png` ✅ GitHub'da
- [x] `docs/figures/wcet_histogram.png` ✅ simülasyon verisiyle üretildi
- [x] `docs/figures/wcet_table.md` ✅ 10 task, 10/10 bütçe içinde
- [x] `docs/figures/pareto_front.png` ✅ üretildi
- [x] `docs/figures/pareto_data.csv` ✅
- [x] `docs/figures/thermal_model.png` ✅ üretildi
- [x] `docs/cyclictest_results.txt` ✅ PREEMPT_RT ölçümü
- [ ] WCET gerçek Pi ölçümü (INA219 + logic analyzer)
- [ ] Enerji tablosu gerçek Pi ölçümü (INA219)
- [ ] Termal model gerçek Pi ölçümü

---

## 📐 Modelleme Diyagramları

- [x] `docs/statechart_veloguard.drawio` ✅ draw.io dosyası hazır
- [x] `docs/petrinet_veloguard.drawio` ✅ draw.io dosyası hazır (PRIO_INHERIT gösteriyor)
- [ ] StateChart PNG export (draw.io'da açıp export edin)
- [ ] Petri ağı PNG export
- [ ] UPPAAL zamanlı otomat (Sprint 3 sonu)

---

## 🏃 Sprint Durumu

| Sprint | Hedef | Durum |
|--------|-------|-------|
| Sprint 0 (04-08 May) | Exposé + Modelleme | ✅ Tamamlandı |
| Sprint 1 (09-15 May) | Donanım kurulumu | ✅ Tamamlandı |
| Sprint 2 (16-22 May) | FSM + Entegrasyon | ⚡ ERKEN tamamlandı (Sprint 1'de bitti) |
| Sprint 3 (23-29 May) | RTOS + Priority Inheritance | ✅ **18 Mayıs'ta tamamlandı** |
| Sprint 4 (30 May-02 Haz) | Metrikler | 🔄 Grafikler üretildi, gerçek ölçüm bekliyor |
| Final (03-05 Haz) | Rapor + Video + Teslim | ⏳ |

---

## 🎁 Bonus Puanlar

- [x] **GitHub açık kaynak** (+5) — public repo ✅ `github.com/Ceren04/INF-208`
- [ ] **OpenCV motion detection** (+5) — camera_driver.py hazır, Pi Camera bağlanacak

---

## 📋 Hocanın Zorunlu Şartları

- [x] ≥2 sensör (IMU ✅, Reed ✅, Camera/DHT22 bağlanacak)
- [x] ≥1 aktüatör (LED ✅, PAM8403 ✅)
- [x] Mantıksal karar algoritması (FSM 5-durum ✅)
- [x] ≥2 modelleme (StateChart ✅, Petri ✅, UPPAAL planlı)
- [x] RTOS (PREEMPT_RT 6.12.87 ✅)
- [x] **Priority Inversion çözümü kanıtlı** — 4900ms→2750ms grafik ✅ ⭐⭐⭐
- [x] ≥3 değerlendirme metriği (WCET ✅, Enerji ✅ simül., Termal ✅ simül., Pareto ✅)

---

## 📌 Laba Döndüğünüzde Yapılacaklar

```bash
# 1. Kodu güncelle
cd ~/veloguard && git pull

# 2. Birim testleri çalıştır (tümü geçmeli)
pytest tests/ -v

# 3. Tüm sensör testi
python3 tools/sensor_test_all.py

# 4. Sistemi başlat
sudo venv/bin/python3 -m firmware.main

# 5. Telegram token gir
nano .env   # TELEGRAM_TOKEN ve TELEGRAM_CHAT_ID

# 6. IMU lehim / kablo sağlamlaştır
```
