# ✅ VeloGuard — Proje İlerleme Checklist
> Son güncelleme: 14 Mayıs 2026  
> Teslim tarihi: 05 Haziran 2026 14:45

---

## 🔧 Yazılım Altyapısı

### Temel Modüller
- [x] `firmware/config.py` — merkezi sabitler
- [x] `firmware/fsm.py` — 5-durumlu FSM + TAMPER
- [x] `firmware/shared_state.py` — thread-safe veri deposu
- [x] `firmware/motion_detector.py` — adaptif hareket dedektörü
- [x] `firmware/task_manager.py` — RTOS thread yöneticisi
- [x] `firmware/watchdog.py` — yazılım watchdog
- [x] `firmware/main.py` — ana giriş, graceful shutdown

### Sürücüler
- [x] `firmware/drivers/base_sensor.py`
- [x] `firmware/drivers/imu_driver.py` ✅ Pi'da çalışıyor
- [x] `firmware/drivers/led_driver.py` ✅ Pi'da çalışıyor
- [x] `firmware/drivers/reed_driver.py` ✅ (reboot sonrası)
- [x] `firmware/drivers/pam8403_driver.py` ✅ başlatıldı
- [ ] `firmware/drivers/camera_driver.py` — implement edilecek
- [ ] `firmware/drivers/dht_driver.py` — implement edilecek
- [ ] `firmware/drivers/ina219_driver.py` — implement edilecek

### Algoritmalar
- [x] `firmware/algorithms/kalman.py` ✅ gerçek veriyle test edildi
- [x] `firmware/algorithms/adaptive_threshold.py`
- [ ] `firmware/algorithms/adaptive_threshold.py` gerçek veriyle test

### İletişim
- [x] `firmware/comm/web_ui.py` ✅ telefondan test edildi
- [x] `firmware/comm/telegram_bot.py` — token girilince çalışır
- [x] `firmware/comm/mqtt.py`

### RTOS / C
- [x] `firmware/rtos/prio_inh_demo.c` — iskelet mevcut
- [ ] `firmware/rtos/prio_inh_demo.c` — implement + ölçüm ⭐⭐⭐
- [ ] `firmware/rtos/imu_task.c` — C'ye port
- [ ] `firmware/rtos/fsm_task.c` — C'ye port

---

## 🔌 Donanım

- [x] Raspberry Pi 3B — SSH bağlantısı
- [x] MPU-6050 (GY-521) — I2C 0x68, WHO_AM_I 0x72 ✅
- [x] LED Kırmızı (GPIO5) ✅
- [x] LED Sarı (GPIO6) ✅
- [x] LED Yeşil (GPIO13) ✅
- [x] Reed switch (GPIO27) ✅
- [x] PAM8403 (GPIO18) ✅
- [ ] Pi Camera — bağlanacak
- [ ] DHT22 (GPIO4) — bağlanacak
- [ ] INA219 (I2C 0x40) — bağlanacak
- [ ] 18650 pil + BMS — bağlanacak

---

## 🧪 Test Durumu

- [x] IMU 100Hz veri akışı — `az≈1.01g`, `mag≈0.02g`
- [x] Kalman filtresi canlı veri
- [x] LED FSM pattern testi (fiziksel)
- [x] Web UI ARM/DISARM/RIDE (telefon)
- [x] `sudo python3 -m firmware.main` — sistem ayakta
- [ ] Reed switch tamper simülasyonu
- [ ] PAM8403 alarm sesi fiziksel test
- [ ] FSM IMU → PRE_ALARM → ALARM geçişi (bisiklet sallama)
- [ ] Telegram bildirim testi (gerçek token)
- [ ] `pytest tests/` — birim testler
- [ ] 30 dakika aralıksız çalışma testi

---

## 🏃 Sprint Hedefleri

### Sprint 0 (04-08 May) — Hazırlık
- [ ] Exposé PDF teslim (08 May)
- [x] Dizin yapısı, README, LICENSE
- [ ] StateChart draw.io
- [ ] Petri ağı draw.io
- [ ] Sistem mimarisi blok diyagramı

### Sprint 1 (09-15 May) — Donanım Kurulumu
- [x] MPU-6050 I2C çalışıyor
- [x] LED'ler çalışıyor
- [x] Reed switch bağlandı
- [x] PAM8403 başlatıldı
- [ ] Pi Camera test (`libcamera-still`)
- [ ] DHT22 sıcaklık okuması
- [ ] INA219 akım ölçümü
- [ ] Tüm sürücüler tek test scriptinde
- [ ] Sprint 1 demo videosu (1-2 dk)

### Sprint 2 (16-22 May) — FSM + Entegrasyon
- [x] FSM 5 durum implement edildi ✅ (erken)
- [x] Kalman filtresi ✅ (erken)
- [x] Adaptif eşik ✅ (erken)
- [x] Web UI ARM/DISARM/RIDE ✅ (erken)
- [ ] IMU → FSM event bağlantısı fiziksel test
- [ ] Kamera + FSM ALARM entegrasyonu
- [ ] Telegram alarm fotoğrafı
- [ ] 🚨 **19 May: Donanım prototipi hocanın milestone'u**

### Sprint 3 (23-29 May) — RTOS + Priority Inheritance
- [ ] PREEMPT-RT kernel kontrolü (`uname -a`)
- [ ] `hello_rt.c` — 3 thread SCHED_FIFO
- [ ] `prio_inv_demo.c` — PRIO_INHERIT deneyi ⭐⭐⭐
- [ ] CSV log → grafik (prio_inv_plot.py)
- [ ] IMU/FSM C'ye port
- [ ] 🚨 **26 May: Priority Inheritance kanıtı**

### Sprint 4 (30 May - 02 Haz) — Metrikler
- [ ] WCET tablosu (10+ task)
- [ ] Enerji tüketimi tablosu (state bazlı)
- [ ] Termal modelleme grafiği
- [ ] Pareto cephesi grafiği
- [ ] 🚨 **02 Haz: Metrikler tamamlandı**

### Final (03-05 Haz) — Teslim
- [ ] Rapor PDF (20-30 sayfa)
- [ ] Demo video (≤5 dk)
- [ ] Sunum (10-12 slayt)
- [ ] Turnitin raporu (#48947170, TAU.INF.208)
- [ ] GitHub public + README + MIT lisans 🎁
- [ ] Basılı + ciltli rapor + 3 imza
- [ ] 🚨 **05 Haz 14:45: C208 elden teslim**

---

## 🎁 Bonus Puanlar

- [ ] GitHub açık kaynak (+5) — repo public yapılacak
- [ ] OpenCV motion detection (+5) — camera_driver.py

---

## 📊 Hocanın Zorunlu Şartları

- [x] ≥2 sensör (IMU ✅, Camera, Reed ✅, DHT22)
- [x] ≥1 aktüatör (LED ✅, PAM8403 ✅)
- [x] Mantıksal karar algoritması (FSM 5-durum ✅)
- [ ] ≥2 modelleme (StateChart, Petri, UPPAAL)
- [x] RTOS (Linux PREEMPT ✅)
- [ ] Priority Inversion çözümü kanıtlı ⭐⭐⭐
- [ ] ≥3 değerlendirme metriği (WCET, Enerji, Termal, Pareto)
