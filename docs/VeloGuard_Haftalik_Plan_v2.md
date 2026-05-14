# 📋 VeloGuard — Detaylı Haftalık & Günlük Çalışma Planı
## INF 208 Gömülü Sistemler Projesi · Check-list Sistemi

> **Başlangıç:** 04 Mayıs 2026 (Pazartesi)  
> **Final Teslim:** 05 Haziran 2026 (Cuma 14:45)  
> **Toplam Süre:** 33 gün (5 sprint)  
> **Ekip:** 3 kişi · Üye-1 (Donanımcı) · Üye-2 (Beyin/Yazılım) · Üye-3 (Göz/Ses/Comm)

---

## ✅ GÜNCEL İLERLEME DURUMU (Son güncelleme: 14 Mayıs 2026)

### 🏁 Sprint 1 — 14 Mayıs Perşembe sonu itibarıyla tamamlananlar

#### Yazılım Altyapısı (Tamamlandı ✅)
- [x] Proje dizin yapısı kuruldu (`firmware/`, `drivers/`, `comm/`, `rtos/`, `tools/`, `tests/`, `docs/`, `hardware/`, `presentation/`)
- [x] Tüm Python `__init__.py` paket dosyaları oluşturuldu
- [x] `firmware/config.py` — merkezi sabitler (GPIO, eşikler, parametreler)
- [x] `firmware/drivers/base_sensor.py` — soyut temel sürücü sınıfı
- [x] `firmware/drivers/imu_driver.py` — MPU-6050 I2C sürücüsü (GY-521 klon 0x72 desteği dahil) ✅ **DONANUMDA TEST EDİLDİ**
- [x] `firmware/drivers/led_driver.py` — 3 renkli LED, thread-safe blink ✅ **DONANUMDA TEST EDİLDİ**
- [x] `firmware/drivers/reed_driver.py` — GPIO interrupt tabanlı tamper algılama
- [x] `firmware/drivers/pam8403_driver.py` — PWM ses sürücüsü, siren, bip ✅ **BAŞLATILDI**
- [x] `firmware/algorithms/kalman.py` — 1D Kalman filtresi ✅ **GERÇEK VERİYLE TEST EDİLDİ**
- [x] `firmware/algorithms/adaptive_threshold.py` — adaptif eşik hesaplayıcı
- [x] `firmware/motion_detector.py` — adaptif hareket dedektörü + Kalman
- [x] `firmware/fsm.py` — 5 durumlu FSM + orthogonal TAMPER + callback sistemi
- [x] `firmware/shared_state.py` — thread-safe sensör veri deposu
- [x] `firmware/watchdog.py` — yazılım watchdog
- [x] `firmware/task_manager.py` — RTOS thread yöneticisi (IMU/Reed/FSM/Thermal/Power/Logger)
- [x] `firmware/comm/web_ui.py` — Flask tabanlı mobil uyumlu web arayüzü ✅ **TELEFONDAN TEST EDİLDİ**
- [x] `firmware/comm/telegram_bot.py` — Telegram bildirim sürücüsü (token gerekli)
- [x] `firmware/comm/mqtt.py` — MQTT yayın katmanı
- [x] `firmware/main.py` — ana giriş noktası, graceful shutdown ✅ **Pi'DA ÇALIŞIYOR**
- [x] `tools/mock_drivers.py` — simüle edilmiş sürücüler (donanımsız test)
- [x] `tools/plot_style.py` — grafik stil ayarları
- [x] `setup_pi.sh` — Pi otomatik kurulum scripti
- [x] `README.md`, `LICENSE (MIT)`, `CONTRIBUTING.md`, `.env.example`, `.gitignore`

#### Donanım & Pi Kurulumu (Tamamlandı ✅)
- [x] Raspberry Pi 3B — SSH bağlantısı kuruldu
- [x] Raspberry Pi OS Bookworm — PREEMPT Debian 6.12.75+rpt-rpi-v8
- [x] Python sanal ortamı (`venv`) kuruldu
- [x] Tüm Python bağımlılıkları yüklendi (numpy, scipy, flask, RPi.GPIO, smbus2, vs.)
- [x] I2C arayüzü etkinleştirildi
- [x] MPU-6050 (GY-521) bağlandı — I2C adres 0x68, WHO_AM_I 0x72 ✅
- [x] 3 renkli LED bağlandı (GPIO5/6/13) ✅
- [x] PAM8403 bağlandı (GPIO18 PWM) ✅
- [x] Reed switch bağlandı (GPIO27) — reboot sonrası çalışıyor
- [x] I2C baudrate 50000 Hz'e düşürüldü (kablo bağlantısı stabilizasyonu)

#### Canlı Test Sonuçları ✅
- [x] `i2cdetect -y 1` → 0x68 görünüyor
- [x] IMU 100Hz veri akışı: `az≈+1.01g`, `mag≈0.02g` (hareketsiz baseline)
- [x] Kalman filtresi gerçek veriyle çalışıyor
- [x] LED FSM pattern'ları fiziksel olarak doğrulandı (DISARMED/ARMED/PRE_ALARM/ALARM/RIDE)
- [x] `sudo venv/bin/python3 -m firmware.main` — tüm sistem ayakta
- [x] Web UI `http://192.168.102.88:5000` — telefondan erişildi, ARM/DISARM/RIDE çalışıyor

### ⏳ Sprint 1 — Kalan Görevler (15 Mayıs'a kadar)
- [ ] Reed switch reboot sonrası tam test (tamper simülasyonu)
- [ ] PAM8403 alarm sesi fiziksel test (hoparlör bağlantısı)
- [ ] IMU'yu bisiklet üzerine tak → `mag` değeri sallanınca ne oluyor ölç
- [ ] Telegram bot gerçek token ile test (`TELEGRAM_TOKEN` + `TELEGRAM_CHAT_ID` .env'e gir)
- [ ] Sprint 1 demo videosu çek (1-2 dk ham malzeme)

### ⏩ Sprint 2 için hazır durumdakiler (Erken tamamlandı)
- [x] FSM çekirdeği (Sprint 2 hedefi — erken tamamlandı)
- [x] Adaptif eşik algoritması (Sprint 2 hedefi — erken tamamlandı)  
- [x] Kalman filtresi (Sprint 2 hedefi — erken tamamlandı)
- [x] Web UI ARM/DISARM/RIDE komutları (Sprint 2 hedefi — erken tamamlandı)

---

---

## 🗺️ Yüksek Seviye Yol Haritası

| Sprint | Tarih | Süre | Ana Hedef | Hocanın Milestone'u |
|---|---|---|---|---|
| **Sprint 0** | 04 - 08 May | 5 gün | Exposé + Modelleme + Donanım siparişi | 🚨 **08 May: EXPOSÉ TESLİM** |
| **Sprint 1** | 09 - 15 May | 7 gün | Donanım eline geçir, kurulum, ilk sürücüler | — |
| **Sprint 2** | 16 - 22 May | 7 gün | Sensör + aktüatör entegrasyon, FSM çekirdeği | 🚨 **19 May: DONANIM ÇALIŞIR** |
| **Sprint 3** | 23 - 29 May | 7 gün | RTOS + Priority Inheritance + İletişim | 🚨 **26 May: PRIO_INH KANITLI** |
| **Sprint 4** | 30 May - 02 Haz | 4 gün | WCET + Enerji + Termal + Pareto ölçümleri | 🚨 **02 Haz: METRİKLER TAMAM** |
| **Final** | 03 - 05 Haz | 3 gün | Rapor + Video + Sunum + TESLİM | 🚨 **05 Haz 14:45: SON TESLİM** |

---

## 🔁 Standart Günlük Rutin (Her Gün Geçerli)

### Sabah Açılış (15 dk · 09:00)
- [ ] WhatsApp/Discord grubunda iyi sabahlar + bugün ne yapacağını yaz
- [ ] Önceki günün tamamlanmamış maddelerini kontrol et
- [ ] Bugünün checkbox listesini aç

### Öğle Mini-Sync (5 dk · 13:00)
- [ ] Sabahki blok varsa diğerlerine söyle
- [ ] Öğleden sonraki plan kısaca yaz

### Akşam Sync (20-30 dk · 21:00 — sesli arama)
3 kişi sırayla cevaplar:
1. **Ne bitirdim?** (somut, "şunu yaptım" şeklinde)
2. **Yarın ne yapacağım?** (somut, ölçülebilir)
3. **Bloker var mı?** (donanım gelmedi, hata aldım, vs.)
4. **Yardım gerekiyor mu?** (kimden, ne konuda)

### Pazar Akşamı Haftalık Retrospektif (45 dk)
- Bu hafta tamamlanan / tamamlanmayan maddeler
- Önümüzdeki haftaya taşınanlar
- Süreçte düzeltilmesi gereken şeyler

---

## ⚙️ Görev Sahibi Kısaltmaları

| Kısaltma | Anlamı |
|---|---|
| **Ü1** | Üye 1 — Donanımcı |
| **Ü2** | Üye 2 — Beyin/Yazılım Çekirdeği |
| **Ü3** | Üye 3 — Göz/Ses/Comm/Değerlendirme |
| **🤝** | Üçü birlikte |
| **⭐** | Hocanın puantajı için kritik madde |
| **⚠️** | Atlanırsa risk doğurur |
| **🎁** | Bonus puan getirici |


---
---

# 🚀 SPRINT 0 — Hazırlık & Exposé (4-8 Mayıs)

## 🎯 Sprintin Ana Hedefi
Hocaya **8 Mayıs Cuma günü** Exposé teslim etmek + donanımı sipariş etmek + ekip altyapısını kurmak.

## 🏁 Sprint Sonunda Elde Olması Gerekenler
- [ ] ⭐ Exposé PDF (3 sayfa) hocaya teslim edildi (Classroom)
- [ ] Donanım siparişi verildi (Robotistan/Direnc)
- [ ] GitHub repo'su açıldı, README başlangıç hali var
- [ ] Telegram grubu + bot token hazır
- [ ] StateChart taslağı hazır (draw.io)
- [ ] Petri ağı taslağı hazır
- [ ] Sistem mimarisi blok diyagramı hazır
- [ ] Pi'a OS yükleme planı netleşti

---

## 📆 04 Mayıs — Pazartesi (Bugün! Sıfır Günü)

**Günün Hedefi:** Plan ekibe sunulur, kararlar alınır, altyapı kurulur.

### 🤝 Sabah (10:00 - 12:00) — Birlikte Toplanma
- [ ] **Kick-off toplantısı** (yüz yüze ya da görüntülü)
  - [ ] Bu plan dokümanı birlikte okunur
  - [ ] Roller netleşir (kim Ü1, kim Ü2, kim Ü3)
  - [ ] Kabul edilmeyen kısımlar işaretlenir, alternatifler tartışılır
- [ ] **İletişim kanalı**: WhatsApp veya Discord grubu kurulur
- [ ] **Bulut depolama**: Google Drive klasörü açılır (raporlar, görseller için)
- [ ] **Ortak takvim**: Google Calendar paylaşılan etkinlik (haftalık sync)

### 👤 Ü1 — Donanımcı (Öğleden sonra)
- [ ] Mevcut Pi modelini belirle (Pi 4 mü, Pi 5 mi? RAM kaç GB?)
- [ ] Fotoğraftaki anti-statik poşeti aç, içinde ne var görsel olarak ekibe paylaş
- [ ] Bilinen güç adaptörlerinin Volt/Amper değerlerini etiketten oku, listele
- [ ] Robotistan + Direnc.net + Hepsiburada'da fiyat karşılaştırma:
  - [ ] MPU6050 GY-521
  - [ ] Pi Camera v2 (veya Pi'ya uygun versiyon)
  - [ ] DHT22 (waterproof tip)
  - [ ] INA219
  - [ ] Reed switch + mıknatıs
  - [ ] Aktif buzzer 5V
  - [ ] LED kit + dirençler
  - [ ] 18650 pil (2 adet) + holder + BMS
  - [ ] MT3608 boost converter
  - [ ] IP65 plastik kutu (~150x100x50)
  - [ ] Breadboard + jumper kablo seti
  - [ ] **Sepet ekran görüntüsü ekibe paylaş** (akşam sync'e hazır)

### 👤 Ü2 — Beyin/Yazılım Çekirdeği
- [ ] GitHub'da yeni organization (örn. `tau-veloguard`) oluştur
- [ ] `veloguard` repo'sunu **public** olarak aç 🎁
- [ ] MIT License ekle 🎁
- [ ] Boş README.md ile commit at, ekibi collaborator olarak ekle
- [ ] `.gitignore` (Python, C, OS) ekle
- [ ] `docs/`, `firmware/`, `hardware/`, `presentation/` klasörlerini hazırla
- [ ] Kişisel makinede: draw.io desktop kurulumu (modelleme için)
- [ ] StateChart **çok kaba taslağı** çiz (Disarmed → Armed → Pre-Alarm → Alarm)

### 👤 Ü3 — Göz/Ses/Comm
- [ ] Telegram'da `@BotFather` üzerinden yeni bot oluştur
  - [ ] Bot adı: `VeloGuardAlertBot` (kullanılabilirse)
  - [ ] Bot token'ını **gizli** olarak Drive'a not düş (sonra `.env` dosyası olacak)
- [ ] Ekipte ortak Telegram grubu aç, botu gruba ekle
- [ ] Test: telefondan `python-telegram-bot` kütüphanesi ile ilk "Merhaba" mesajı atılıyor mu? (kendi laptop'undan)
- [ ] Demo planı taslağı: **5 senaryo** (park, hafif dokunma, hırsızlık, sürüş, tamper) — düz metin halinde yaz

### 🌙 Akşam Sync (21:00)
**Soru listesi:**
- Pi modeli ne? RAM ne? Disk ne?
- Sipariş listesi gönderilebilir durumda mı?
- GitHub repo açıldı mı, herkesin erişimi var mı?
- Telegram bot çalışıyor mu?
- Yarın siparişi kim verecek (kart, adres)? **Karar al!**

### ⚠️ Bugünün Riski
Eğer **biri kick-off'a katılamazsa**, sentezi kaçıracak. Mutlaka kayıt al ya da yazılı özet paylaş.

---

## 📆 05 Mayıs — Salı

**Günün Hedefi:** Envanter tamamlanır + modelleme başlar + kernel araştırması.

### 👤 Ü1 — Donanımcı
- [ ] **Sabah 10:00'a kadar**: Sipariş listesi finalize (akşam sync'inde alınan kararlara göre)
- [ ] **Envanter kontrolü** ✅ — tüm malzemeler elimizde!
  - [ ] Her bileşeni masaya koy, gözle kontrol et
  - [ ] Pil şarjını ölç, BMS çalışıyor mu kontrol et
  - [ ] Kutu + bisiklet braketi siparişi: fiyat karşılaştır (acil değil)
- [ ] Mevcut Pi'a **Raspberry Pi OS Lite (64-bit Bookworm)** yükle:
  - [ ] Raspberry Pi Imager indir
  - [ ] MicroSD'ye yaz
  - [ ] SSH'i aktif et (ssh dosyası boot'a)
  - [ ] WiFi credentials (varsa) yapılandır
  - [ ] İlk boot: `sudo apt update && sudo apt upgrade -y`
- [ ] Pi'da temel paketler: `git`, `python3-pip`, `i2c-tools`, `vim`/`nano`
- [ ] `raspi-config` ile I2C, SPI, Camera, GPIO (DHT22) interface'lerini AÇ

### 👤 Ü2 — Beyin/Yazılım
- [ ] **PREEMPT-RT araştırması** (1.5 saat):
  - [ ] Pi 3B için hazır PREEMPT-RT kernel var mı? Önce şuraya bak:
    - https://github.com/kdoren/linux/releases (hazır .deb)
    - https://github.com/raspberrypi/linux (kaynak kod)
  - [ ] Eğer hazır .deb varsa → 1 saatte kurulum mümkün ✓
  - [ ] Yoksa → kernel derlemek 4-6 saat alır, ona göre planla
  - [ ] Bulgularını grup chat'e yaz
- [ ] **StateChart detaylandırma** (draw.io):
  - [ ] 5 ana state (Disarmed, Armed, Pre-Alarm, Alarm, Ride)
  - [ ] Tamper süper-state'i (orthogonal)
  - [ ] Eco/Low-battery süper-state'i
  - [ ] Geçişlerin tetikleyicilerini yaz (motion_low, motion_high, ARM_BTN, vs.)
  - [ ] PNG export → `docs/statechart_v1.png`
- [ ] Repo'ya commit + push

### 👤 Ü3 — Göz/Ses/Comm
- [ ] **Petri ağı taslağı** (PIPE2 veya draw.io):
  - [ ] 3 yer (place): IMU veri hazır, mutex boş, buffer dolu
  - [ ] 4 geçiş (transition): yaz, kilit-al, oku, kilit-bırak
  - [ ] Token akışını çiz, basit producer-consumer
  - [ ] PNG export → `docs/petrinet_v1.png`
- [ ] **Sistem mimarisi blok diyagramı** (draw.io):
  - [ ] Sensörler (sol blok)
  - [ ] Pi (orta) — task'lar listesi
  - [ ] Çıktılar (sağ blok) — Buzzer/LED/Camera/BLE
  - [ ] PNG export → `docs/architecture_v1.png`
- [ ] Telegram bot'a basit test scripti yaz, GitHub'a `tools/telegram_test.py` olarak ekle (token .env'den okusun)

### 🌙 Akşam Sync (21:00)
- Sipariş verildi mi? Kargo no ne, ne zaman gelmesi bekleniyor?
- StateChart, Petri ağı, mimari diyagram hangi seviyede?
- PREEMPT-RT için karar: hazır .deb mi, derleme mi?
- Yarın için sabah önceliği ne?

### ⚠️ Bugünün Riski
- Kutu/braket için sipariş acil değil — neredeyse tüm donanım elimizde.
- (Sipariş artık acil değil, tüm donanım elimizde!)

---

## 📆 06 Mayıs — Çarşamba

**Günün Hedefi:** Modelleme bitsin (taslak seviyesi), Exposé yazımı başlasın, Pi hazırlığı tamamlansın.

### 👤 Ü1 — Donanımcı
- [ ] Pi üzerinde son hazırlıklar:
  - [ ] `vcgencmd measure_temp` çalışıyor mu?
  - [ ] `i2cdetect -y 1` (boş bus görünmeli)
  - [ ] `ls /sys/bus/w1/devices/` (GPIO (DHT22) için, boş olabilir)
- [ ] **Pi Camera test stand-by**: eğer eski bir Pi Camera varsa şimdiden takıp `libcamera-still -o test.jpg` ile test et
- [ ] **Donanım kutusu için ölçü çıkarma** (kağıt üzerinde):
  - [ ] Pi 3B boyutu: 85 x 56 x 17 mm (Pi 4 ile aynı)
  - [ ] Pil 18650 (×2) boyutu: ~140 x 40 x 20 mm
  - [ ] Mantıklı kutu iç boyutu: ~150 x 100 x 50 mm
  - [ ] Kabaca Fusion 360 / FreeCAD'de basit kutu çiz (sonra detay)
- [ ] **Bisiklet bağlantısı**: ekipten kim bisiklet sağlayacak? Sele borusu çapını ölç (genelde 27.2 / 30.9 / 31.6 mm)

### 👤 Ü2 — Beyin/Yazılım
- [ ] PREEMPT-RT KURULUMU (kararı dün verildiyse şimdi uygula):
  - [ ] Kernel paketi yükle / derle
  - [ ] Reboot
  - [ ] `uname -a` ile `PREEMPT_RT` ibaresini gör
  - [ ] `sudo apt install rt-tests` → `cyclictest -p 80 -t 1 -n` ile temel ölçüm al
  - [ ] Sonuçları **screenshot** al, repo'ya `docs/preempt_rt_baseline.png` olarak ekle ⭐
- [ ] StateChart v2 (geçiş etiketleri net, hocaya gösterilebilir kalitede)
- [ ] Petri ağına bakıp Ü3 ile birlikte **tutarlılık kontrolü** (model 1 ile model 2 aynı sistemi anlatıyor mu?)

### 👤 Ü3 — Göz/Ses/Comm
- [ ] **Exposé yazımına başla** (Google Docs ortak dosya):
  - [ ] Sayfa 1: Proje adı, ekip, motivasyon, problem tanımı (1 paragraf)
  - [ ] Sayfa 2: Sistem mimarisi diyagramı + StateChart + kısa açıklama
  - [ ] Sayfa 3: Petri ağı + zaman planı (Gantt taslağı) + literatür referansları
- [ ] Bonus: Üniversite kütüphanesinden 3-5 akademik referans bul (bisiklet hırsızlığı, IoT güvenlik, IMU-tabanlı algılama)
  - [ ] BibTeX olarak `docs/references.bib` dosyasına ekle

### 🌙 Akşam Sync (21:00)
- Pi PREEMPT-RT'da mı? `cyclictest` skoru ne?
- Modelleme görselleri sunuma uygun seviyede mi?
- Exposé birinci sayfası bitti mi?
- Kargo durumu?

### ⚠️ Bugünün Riski
PREEMPT-RT kurulumu beklenenden uzun sürerse → Ü2 yarına kaydırır, ama dokümantasyon görevini öne alır.

---

## 📆 07 Mayıs — Perşembe (Exposé Hazırlık Maratonu)

**Günün Hedefi:** Exposé MUTLAKA bitirilir, gece son okuma yapılır.

### 🤝 Sabah Bloku (10:00 - 13:00) — Birlikte Yazma
- [ ] Google Docs'ta **paralel yazım**: 3 kişi farklı bölümlere odaklanır
  - Ü1 → Donanım kapsamı, BOM özeti, mekanik planlama (sayfa 2)
  - Ü2 → Modelleme açıklaması, RTOS planı, Priority Inheritance hedefi (sayfa 2-3)
  - Ü3 → Motivasyon, hedefler, zaman planı, referanslar (sayfa 1 ve 3)
- [ ] Görselleri yerleştir (StateChart, Petri, mimari, Gantt)

### 🤝 Öğleden Sonra (14:00 - 18:00) — Konsolidasyon
- [ ] Ü3 baş editör → tüm metni okuyup tutarlı dile çek
- [ ] Ü2 teknik kontrol → ifadelerin doğru olduğundan emin ol
- [ ] Ü1 görsel kontrol → diyagramların okunabilir olduğunu test et (PDF'e çevirip görüntüle)
- [ ] **Hocanın istediği şartların kontrolü** (Exposé için):
  - [ ] ≥ 2 sensör listelendi mi? ✓ (IMU, Kamera, Reed, DHT22)
  - [ ] ≥ 1 aktüatör listelendi mi? ✓ (PAM8403+Hoparlör, LED)
  - [ ] ≥ 2 modelleme yöntemi anlatıldı mı? ✓ (StateChart, Petri)
  - [ ] RTOS planı belirtildi mi? ✓ (PREEMPT-RT)
  - [ ] Priority Inversion çözümü hedefleniyor mu? ✓
  - [ ] WCET / Enerji / Termal değerlendirmeleri planda var mı? ✓

### 👤 Bireysel Görevler (Akşam)
- [ ] Ü1: Sipariş kargo durumunu kontrol et, gecikme varsa alternatif tedarikçi araştır
- [ ] Ü2: PREEMPT-RT'da 3 farklı senaryoda `cyclictest` çalıştır (idle, CPU stress, I/O stress) → exposé için somut veri
- [ ] Ü3: Exposé'yi PDF olarak çıkar, isim formatı: `VeloGuard_Expose_TAU_INF208_v1.pdf`

### 🌙 Akşam Sync (22:00 — uzatılmış)
- Exposé bitti mi? Yoksa sabaha hangi maddeler kaldı?
- Yarın 09:00'a kadar son rötuş için kim ayırdı zamanı?
- Classroom'a kim yükleyecek?

### ⚠️ Bugünün Riski
Exposé bugün **bitmezse** yarın panik olur. Geç saate kadar çalışmaya hazır ol.

---

## 📆 08 Mayıs — Cuma 🚨 EXPOSÉ TESLİM GÜNÜ

**Günün Hedefi:** Hocaya teslim, sonra hafta sonuna geçiş için planlama.

### 👤 Ü3 — Sabah Erken (08:00 - 10:00)
- [ ] Son okuma — yazım hatası taraması
- [ ] PDF metadata'sı (yazar adları, başlık) düzgün mü?
- [ ] Classroom'a yükle ⚠️ **GERÇEK TESLİM**
- [ ] Yedek olarak hocaya e-posta da at (varsa)
- [ ] Grup chat'e "TESLİM EDİLDİ ✅" mesajı

### 🤝 Öğle (13:00 - 14:30) — Kutlama + Geriye Bakış
- [ ] Birlikte yemek 🍕 (hak ettiniz)
- [ ] Sprint 0 retrospektifi:
  - [ ] Ne iyi gitti?
  - [ ] Ne kötü gitti?
  - [ ] Önümüzdeki hafta neyi farklı yapacağız?

### 👤 Ü1 — Donanımcı (Öğleden sonra)
- [ ] Kargo durumu: hangi paket ne zaman gelir? (cuma → cumartesi/pazartesi tahmin)
- [ ] Kutu/3D baskı için TAU içinde 3D printer var mı? Sorum sor (laboratuvar/asistan)
- [ ] Eğer Pi Camera bugün geldiyse: `libcamera-still -o pi_camera_test.jpg` test
- [ ] Gelmediyse: Pi'da `picamera2` paketini önceden yükle, dokümanları oku

### 👤 Ü2 — Beyin
- [ ] **Sürücü iskelet kodu** yazmaya başla (donanım gelmeden):
  - [ ] `firmware/src/drivers/imu_driver.py` — `MPU6050` class taslağı (read_accel, read_gyro)
  - [ ] `firmware/src/drivers/pam8403_driver.py` — `Buzzer` class
  - [ ] `firmware/src/drivers/led_driver.py` — `LED` class
  - [ ] Her birinde **mock mode** olsun → donanım yokken simülasyonla geliştirilebilsin ⭐
- [ ] Repo'ya `firmware/src/main.py` boş skelet
- [ ] FSM kodu için sözde-kod yaz (`firmware/src/fsm.py` taslak)

### 👤 Ü3 — Göz/Ses
- [ ] OpenCV kurulumu: `pip install opencv-python-headless numpy` (Pi'da değil, kendi laptop'unda da)
- [ ] **Motion detection prototipi**: laptop kamerası ile basit `cv2.absdiff` örneği yaz
  - [ ] `tools/motion_test_laptop.py`
  - [ ] Hareket eden bölgenin etrafına dikdörtgen çiz
  - [ ] Çalışıyor mu? GitHub'a push
- [ ] Telegram bot — temel komutlar:
  - [ ] `/start`, `/status`, `/arm`, `/disarm`
  - [ ] `tools/telegram_bot_v0.py` olarak commit

### 🌙 Akşam Sync (21:00)
- Exposé teslim edildi mi? Hocadan onay/cevap geldi mi?
- Hangi donanım hangi gün gelir? Plan netleşti mi?
- Hafta sonu kim ne yapacak (yorgun olabilirsiniz, hafif tutun)?

### ⚠️ Bugünün Riski
**ÖNEMLİ:** Ders saatinde dijital kontrolü unutmayın. Hoca `Exposé & Modellierung – Abgabe` diyor; basılı bekliyorsa bunu da öğren.

---

## 📆 09-10 Mayıs — Cumartesi & Pazar (Hafif Hafta Sonu)

**Hedef:** Dinlen ama tamamen unutma. 2-3 saatlik hafif görevler.

### Cumartesi (09 Mayıs)
- [ ] 🤝 Tüm sensörler elimizde — envanter sayımı + ilk bağlantı testlerine hazırlık
- [ ] Ü2: PREEMPT-RT cyclictest verilerini grafik haline getir (matplotlib), `docs/cyclictest_baseline.png`
- [ ] Ü3: OpenCV motion detection'da hassasiyet eşikleri test et (gürültüden kaçınma)
- [ ] Ü1: 3D baskı için kutu çiziminin ilk versiyonu (Fusion360 / FreeCAD / Tinkercad)

### Pazar (10 Mayıs)
- [ ] 🤝 **Sprint 1 hazırlık toplantısı** (akşam 19:00, 1 saat)
- [ ] Hafta planı netleşir
- [ ] Tüm sensörler elimizde — Sprint 1 bağlantı sıralamasını netleştir.
- [ ] Pazartesi sabah için iş tablosu hazır

### ⚠️ Hafta sonu için
**6 saatten fazla çalışmayın.** Sprint 1 yorucu olacak, şimdiden tükenmeyin.


---
---

# 🔧 SPRINT 1 — Donanım Kurulumu (11-15 Mayıs)

## 🎯 Sprintin Ana Hedefi
Tüm donanımı eline alıp her sensörü tek tek Pi'a bağlamak ve **bağımsız test etmek**. Sprint sonunda "her parça ayrı ayrı çalışıyor" durumda olmalı.

## 🏁 Sprint Sonunda Elde Olması Gerekenler
- [ ] ⭐ MPU6050 → I2C üzerinden ivme + jiroskop verisi okunuyor
- [ ] Pi Camera → `libcamera-still` ile fotoğraf çekiliyor
- [ ] Reed switch → GPIO interrupt çalışıyor
- [ ] DHT22 → GPIO (DHT22) üzerinden sıcaklık okunuyor
- [ ] PAM8403 + Hoparlör → PWM ile ses çıkarıyor
- [ ] LED'ler → GPIO ile kontrol ediliyor
- [ ] INA219 → I2C üzerinden akım/voltaj okunuyor
- [ ] Pil + BMS → 5V çıkış sağlıyor, Pi besliyor
- [ ] Tüm bileşenler için sürücü class'ları yazıldı + test edildi
- [ ] Devre şeması taslağı hazır (Fritzing veya KiCad)

---

## 📆 11 Mayıs — Pazartesi (Sprint 1 Başlangıç)

**Günün Hedefi:** Donanımı sayım, breadboard'a yerleşim planı, ilk bağlantılar.

### 🤝 Sabah (10:00 - 11:00) — Donanım Envanteri
- [ ] Tüm parçalar masaya konur
- [ ] Excel/Google Sheet'te liste:
  - [ ] Beklenenler vs gelenler
  - [ ] Eksikler varsa hemen sipariş
  - [ ] Hasar/kusur kontrolü (özellikle pil ve kart)
- [ ] **Fotoğraf çek** → rapora "elimizdeki donanım" bölümünde kullanılacak

### 👤 Ü1 — Donanımcı (Asıl yoğun gün)
- [ ] Breadboard'a yerleşim planı çiz (kağıt üzerinde):
  - [ ] Pi 3B GPIO pinout tablosu yanında olsun (https://pinout.xyz)
  - [ ] I2C bus: SDA=GPIO2 (pin 3), SCL=GPIO3 (pin 5)
  - [ ] GPIO (DHT22): GPIO4 (pin 7) varsayılan
  - [ ] Reed switch: GPIO17 (pin 11) gibi boş bir pin
  - [ ] Buzzer: GPIO18 (pin 12) — donanımsal PWM
  - [ ] LED'ler: GPIO22, 23, 24 gibi boş pinler
- [ ] **MPU6050'yi breadboard'a yerleştir** + Pi'ya bağla:
  - [ ] VCC → 3.3V (DİKKAT: 5V verme, modül 3.3V toleranslı)
  - [ ] GND → GND
  - [ ] SDA → GPIO2
  - [ ] SCL → GPIO3
- [ ] `i2cdetect -y 1` → 0x68 (veya AD0 yüksekse 0x69) görmeli ✅
- [ ] **Smoke test**: `python3 -c "import smbus2; bus=smbus2.SMBus(1); print(hex(bus.read_byte_data(0x68, 0x75)))"` → 0x68 dönmeli (WHO_AM_I register)

### 👤 Ü2 — Beyin
- [ ] `firmware/src/drivers/imu_driver.py` gerçek implementasyon:
  - [ ] `read_accel()` → 3 eksen ham veri + g cinsine çevirme
  - [ ] `read_gyro()` → 3 eksen ham veri + °/s cinsine çevirme
  - [ ] `read_temp()` → MPU6050'nin kendi sıcaklık sensörü
  - [ ] `magnitude()` → `sqrt(ax² + ay² + az²)` − 1g
- [ ] Test scripti: `tools/imu_live_plot.py` — matplotlib ile canlı 3 eksen ivme grafiği (10 sn için)
- [ ] Bisikleti hafifçe sars → grafikte görüntüye kavuş 🎯

### 👤 Ü3 — Göz/Ses
- [ ] **Pi Camera fiziki bağlantısı** (Ü1 ile birlikte):
  - [ ] Pi'yı kapat
  - [ ] CSI flat kabloyu Pi'ya tak (kontaklar HDMI portuna bakacak)
  - [ ] `raspi-config` → Camera Enabled
  - [ ] `libcamera-still -o test.jpg` → fotoğraf çekiyor mu?
- [ ] `firmware/src/drivers/camera_driver.py`:
  - [ ] `picamera2` kullan
  - [ ] `capture_photo(path)` fonksiyonu
  - [ ] `start_preview()` / `stop_preview()` (debug için)
  - [ ] `capture_motion_frames(n=3, interval=0.3)` → alarm anı için seri fotoğraf

### 🌙 Akşam Sync
- IMU okuyor mu? Magnitude değeri durağanken kaç (~1g civarı olmalı)?
- Pi Camera test fotoğrafı geldi mi?
- Yarın için kim hangi sensöre odaklanacak?

### ⚠️ Bugünün Riski
**MPU6050'ye 5V verirseniz yanabilir.** Bağlantıdan önce VCC pinini iki kez kontrol et. Modülde regülatör olabilir ama riske girme.

---

## 📆 12 Mayıs — Salı

**Günün Hedefi:** Aktüatörler + sıcaklık sensörü + reed switch tek tek çalıştırılır.

### 👤 Ü1 — Donanımcı
- [ ] **PAM8403 + Hoparlör bağlantısı** (Buzzer yerine):
  - [ ] PAM8403 VCC → 5V, GND → GND
  - [ ] PAM8403 IN_L pini → GPIO18 (donanımsal PWM)
  - [ ] 4Ω/3W hoparlör → PAM8403 OUT_L çıkışına
  - [ ] Python test: `import RPi.GPIO as GPIO; p=GPIO.PWM(18,2000); p.start(50)` → 2kHz ton duyulmalı
  - [ ] ⚠️ Pi 3B'de GPIO18 donanımsal PWM — `pigpio` daemon ile daha temiz ses kalitesi
- [ ] **LED'ler**:
  - [ ] Kırmızı (alarm): GPIO22 → 220Ω → LED → GND
  - [ ] Mavi (status): GPIO23 → 220Ω → LED → GND
  - [ ] Sarı (pre-alarm): GPIO24 → 220Ω → LED → GND
- [ ] **Reed switch** (manyetik):
  - [ ] Bir uç → GPIO17, diğer uç → GND
  - [ ] Pull-up yazılımsal: `GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)`
  - [ ] Mıknatıs yaklaştırınca kapanır → 0 okumalı
  - [ ] Test scripti: `gpiozero.Button` ile event-driven dinleme

### 👤 Ü2 — Beyin
- [ ] `firmware/src/drivers/pam8403_driver.py`:
  - [ ] `beep(duration_ms)` — kısa bip
  - [ ] `alarm_pattern(repeat=10)` — uzun alarm sirenı
  - [ ] PWM ile farklı frekanslar (ön-alarm 1kHz, alarm 2-4kHz çift-frekans)
- [ ] `firmware/src/drivers/led_driver.py`:
  - [ ] `set_state(led_id, state)` — basit aç/kapat
  - [ ] `blink(led_id, hz, duration)` — yanıp sönme
  - [ ] `pulse(led_id)` — alarm pattern'i
- [ ] `firmware/src/drivers/reed_driver.py`:
  - [ ] Interrupt callback altyapısı
  - [ ] `on_open(callback)`, `on_close(callback)`
  - [ ] Debouncing (10 ms yazılımsal)

### 👤 Ü3 — Göz/Ses
- [ ] **DHT22 GPIO (DHT22) kurulumu** (Ü1 ile):
  - [ ] DATA → GPIO4 (pin 7)
  - [ ] 4.7kΩ pull-up direnç DATA ↔ VCC
  - [ ] VCC → 3.3V, GND → GND
  - [ ] `/boot/config.txt` içine `dtoverlay=w1-gpio` ekle, reboot
  - [ ] `ls /sys/bus/w1/devices/` → `28-xxxxx` görmeli
- [ ] `firmware/src/drivers/temp_driver.py`:
  - [ ] `adafruit-circuitpython-dht` paketi kullan
  - [ ] `read_celsius()` fonksiyonu
  - [ ] CPU sıcaklık karşılaştırması: `vcgencmd measure_temp` ile DHT22 değeri yan yana
- [ ] **OpenCV motion detection Pi'ya port**:
  - [ ] Laptop'taki `motion_test_laptop.py` → Pi'ya kopyala
  - [ ] `picamera2` ile entegre et
  - [ ] Hareket olduğunda console'a "MOTION DETECTED" yaz
  - [ ] Performans: kaç FPS işliyor? (Pi 3B'de 320x240'da 10-15 FPS beklenir, yeterli)

### 🌙 Akşam Sync
- Buzzer + 3 LED + Reed switch hepsi çalışıyor mu?
- DHT22 değer dönüyor mu? (oda sıcaklığı 22-25°C civarı normal)
- Pi Camera + OpenCV motion detection FPS kaç?
- Yarın INA219 ve pil entegrasyonu için kimde ne yok?

### ⚠️ Bugünün Riski
LED bağlarken polariteye dikkat — ters takarsanız yanmaz ama kısa devre yapabilir. Anot (uzun bacak) GPIO tarafına.

---

## 📆 13 Mayıs — Çarşamba

**Günün Hedefi:** INA219 enerji ölçümü + pil sistemi + tüm sensörler bir arada.

### 👤 Ü1 — Donanımcı
- [ ] **INA219 bağlantısı**:
  - [ ] VCC → 3.3V, GND → GND
  - [ ] SDA, SCL → I2C bus (zaten MPU6050 ile paylaşıyor, farklı adres 0x40)
  - [ ] V+ ve V− pinleri → ölçeceği güç hattı (Pi besleme hattını seri olarak kes)
- [ ] `i2cdetect -y 1` → 0x40 görmeli (MPU6050 0x68 yanında)
- [ ] **Pil sistemi**:
  - [ ] 18650 ×2 seri (7.4V) → BMS → MT3608 boost? Hayır, 7.4V → buck converter ile 5V daha doğru
  - [ ] **Önerilen**: 18650 ×1 (3.7V) → MT3608 → 5V (5A) → Pi
  - [ ] Veya 18650 ×2 paralel (3.7V, 6000mAh) → MT3608 → 5V
  - [ ] Test: pil dolu → Pi MT3608 üzerinden besleniyor mu? `vcgencmd get_throttled` (0x0 olmalı, undervoltage yok)

### 👤 Ü2 — Beyin
- [ ] `firmware/src/drivers/ina219_driver.py`:
  - [ ] `adafruit-circuitpython-ina219` paketi kullan
  - [ ] `read_voltage()`, `read_current()`, `read_power()` metodları
  - [ ] Sürekli loglama modu: `start_logging(file, hz=2)` → CSV
- [ ] **Tüm sürücüleri tek bir test scripti'nde topla**: `tools/full_sensor_test.py`
  - [ ] 30 saniye boyunca tüm sensörlerden veri oku
  - [ ] Tablo halinde print: zaman, ax, ay, az, gx, gy, gz, temp_pi, temp_ext, V, I, P
  - [ ] Reed switch açılırsa "REED OPEN" satırı bas
- [ ] **Watchdog araştırma**: Pi'da systemd watchdog nasıl kurulur, kısa not yaz (notu Drive'a)

### 👤 Ü3 — Göz/Ses
- [ ] **Telegram bot güçlendirme**:
  - [ ] Bot fotoğraf gönderebiliyor mu? `bot.send_photo(chat_id, photo=open('test.jpg', 'rb'))`
  - [ ] Pi Camera ile çekilen fotoğrafı Telegram'a gönderme akışı: 5 saniyede tamamlanabiliyor mu?
  - [ ] **End-to-end test**: Pi'da `python3 alarm_demo.py` → fotoğraf çek → Telegram'a gönder
- [ ] **Web kontrol arayüzü taslağı** (Flask):
  - [ ] `firmware/src/comm/web_ui.py`
  - [ ] Tek sayfa: ARM / DISARM / RIDE butonları + son durum metni
  - [ ] Pi'nın IP'sinde port 5000'da çalışsın
  - [ ] CSS minimum (Bootstrap CDN tek satır)

### 🌙 Akşam Sync
- INA219 doğru ölçüyor mu? (5V hattı için ~5V görmeli, akım Pi'nın yüküne bağlı 300-500mA)
- Pil sistemi çalışıyor mu? Pi'yı 30 dk besledi mi?
- Telegram'a fotoğraf gitti mi? Süresi ne?
- Yarın entegrasyon başlıyor — bu gece her sürücünün çalıştığından emin ol.

### ⚠️ Bugünün Riski
- Pil bağlantılarında polarite **çok kritik**. Yanlış kutup → BMS yanar, hatta pil patlayabilir.
- Ölçü için **multimetre kullan**, görsel tahmine güvenme.

---

## 📆 14 Mayıs — Perşembe

**Günün Hedefi:** Tüm bileşenleri TEK bir program altında çalıştırmak (henüz FSM yok, sadece read & display).

### 🤝 Sabah (10:00 - 12:00) — Birleştirme Günü
- [ ] Ü1 + Ü2 birlikte: tüm sürücüleri tek bir Python scripti'nde import et
- [ ] Ü3 paralel: web UI'ı Pi'ya yükle, Pi'nın IP'sinden test et

### 👤 Ü1 — Donanımcı (Öğleden sonra)
- [ ] Devre şeması çizimi (Fritzing veya KiCad):
  - [ ] Pi GPIO header
  - [ ] Tüm sensörler ve bağlantılar
  - [ ] Pil + BMS + MT3608 güç bloğu
  - [ ] PNG export → `hardware/schematic_v1.png`
- [ ] Devre şemasının repo'ya commit'i
- [ ] **Termal görsel test**: Pi'yı 10 dk yükle (`stress-ng --cpu 4`), DHT22 ve `vcgencmd measure_temp` değerlerini paralel logla → grafik

### 👤 Ü2 — Beyin
- [ ] **Multi-thread sensör okuma demo**:
  - [ ] Python `threading` ile 3 thread:
    - Thread 1: IMU 100 Hz oku, son değeri shared dict'e yaz
    - Thread 2: Temp 1 Hz oku
    - Thread 3: Reed switch event listener
  - [ ] Mutex (threading.Lock) ile shared dict koru
  - [ ] Bu, gelecekteki POSIX threads + PRIO_INHERIT için **ön deney** ⭐
- [ ] FSM çekirdeği için ilk Python implementasyon (`firmware/src/fsm.py`):
  - [ ] State enum (DISARMED, ARMED, PRE_ALARM, ALARM, RIDE)
  - [ ] `transition(event)` metodu
  - [ ] Henüz aktüatör tetiklemiyor, sadece state print

### 👤 Ü3 — Göz/Ses
- [ ] **Adım 1: Motion → Telegram entegrasyonu**:
  - [ ] OpenCV motion detector'a callback ekle
  - [ ] Hareket algılandığında: 1) fotoğraf çek 2) Telegram'a gönder
  - [ ] Test: bisikleti pi'nın önünden geçir, Telegram'a fotoğraf gelsin
- [ ] **Web UI'ı Pi'da çalıştır**:
  - [ ] `firmware/src/comm/web_ui.py` Pi'da
  - [ ] Phone'dan Pi'nın IP'sinde aç
  - [ ] ARM butonuna basınca terminal'de "ARM_BTN" yazsın (henüz FSM bağlı değil)

### 🌙 Akşam Sync
- 5 sensör + 3 aktüatör hepsi tek script'te çalışıyor mu?
- Devre şeması okunabilir mi?
- Telegram alarm fotoğrafı E2E işliyor mu?

### ⚠️ Bugünün Riski
**Pi 3B RAM (1GB) dikkat:** OpenCV aktifken `free -h` ile RAM izle, gerekirse 512MB swap ekle (`sudo dphys-swapfile` ile). **Multi-thread sensör okumada** I2C bus paylaşımı sorun çıkarabilir. Eğer `Errno 121` görürsen → I2C lock'ı tek thread'e ver, diğerleri ondan oku.

---

## 📆 15 Mayıs — Cuma

**Günün Hedefi:** Sprint 1'i kapatma + Sprint 2'ye geçiş + ilk demo videosu.

### 🤝 Sabah (10:00 - 13:00) — Demo Hazırlığı
- [ ] **Mini-demo videosu çek (1-2 dakika)**: bu, ileride final video için **ham malzeme** olur
  - [ ] Sahne 1: Pi'ya bağlı sensörler
  - [ ] Sahne 2: Bir terminalde 5 sensörden veri akışı
  - [ ] Sahne 3: PAM8403+Hoparlör çalıyor + LED yanıyor
  - [ ] Sahne 4: Pi Camera fotoğraf çekip Telegram'a yolluyor
- [ ] Bu video repo'ya `presentation/raw/sprint1_demo.mp4`

### 👤 Ü1 — Donanımcı (Öğleden sonra)
- [ ] **3D baskı**: kutu modeli STL → TAU labında / dışarıdan baskıya gönder
  - [ ] Eğer sürer ise 4-5 gün → 19 Mayıs'a yetişir mi? Acele
- [ ] Bisiklet ölçü çıkar → sele borusu çapına göre kelepçe siparişi (gerekirse hazır kelepçe satın al)
- [ ] BOM tablosunu güncelle (gerçek alınanlar, fiyatlar) → `hardware/BOM_v2.csv`

### 👤 Ü2 — Beyin
- [ ] FSM Python prototipinde **tüm geçişleri test et** (unit test):
  - [ ] `tests/test_fsm.py` dosyasında 10+ test case
  - [ ] `pytest` çalıştır, hepsi yeşil olsun
- [ ] PREEMPT-RT ile çalışan ilk C kodu yaz: `firmware/src/rtos/hello_rt.c`
  - [ ] `pthread_create` + `sched_setscheduler(SCHED_FIFO)`
  - [ ] 3 thread, 3 farklı öncelik
  - [ ] Sadece "Thread X running" print'i, ama RT ile

### 👤 Ü3 — Göz/Ses
- [ ] **Sprint 1 retrospektif raporu** (kısa, internal):
  - [ ] Bitti olanlar
  - [ ] Bitmemiş olanlar (taşınacaklar)
  - [ ] Karşılaşılan sorunlar
- [ ] Web UI'a daha fazla detay ekle:
  - [ ] Son 10 IMU değerini göster (canlı)
  - [ ] Sıcaklık göstergesi
  - [ ] Pil seviyesi göstergesi (INA219'dan hesapla)

### 🌙 Akşam Sync — Sprint 1 KAPANIŞI
- Sprint 1 tüm hedefleri tamamlandı mı? (`Hafta Sonunda Elde Olması Gerekenler` listesi)
- Bitmeyen var mı? Sprint 2'ye taşıyalım mı, yoksa hafta sonu telafi mi?
- Sprint 2 öncelikleri ne?

---

## 📆 16-17 Mayıs — Cumartesi & Pazar (Hafif/Telafi)

### Cumartesi (16 May)
- [ ] Sprint 1'den taşınanları telafi et (en fazla 4 saat)
- [ ] Üye 2: PREEMPT-RT C örneği geliştir, sched_param parametrelerini öğren
- [ ] Üye 3: Demo video ham malzemelerini düzenle, daha iyi açılarla yeniden çek

### Pazar (17 May)
- [ ] 🤝 **Sprint 2 hazırlık toplantısı** (akşam 19:00)
- [ ] Önümüzdeki hafta için iş tablosu netleşir
- [ ] **19 Mayıs deadline'ı** sadece 2 gün uzakta — neyle yetişeceğiz?


---
---

# 🧠 SPRINT 2 — FSM + Donanım Prototip Deadline (18-22 Mayıs)

## 🎯 Sprintin Ana Hedefi
**19 Mayıs Salı**: hocanın istediği "donanım prototipi (1 sensör + 1 aktüatör çalışır)" deadline'ı. Bu hafta içinde sistemin **kendi başına çalışan ilk versiyonunu** ortaya çıkarmak: IMU verisi → karar → buzzer/LED.

## 🏁 Sprint Sonunda Elde Olması Gerekenler
- [ ] ⭐ **19 May**: Donanım prototipi hocanın takvimine göre çalışıyor (tek script ile demo)
- [ ] FSM çekirdeği tüm 5 durumla çalışıyor
- [ ] Adaptif eşik (baseline öğrenme) implement edildi
- [ ] Kalman filtresi IMU verisine uygulanıyor
- [ ] Tamper algılama (reed switch) entegre
- [ ] Web UI üzerinden ARM/DISARM/RIDE çalışıyor
- [ ] Çalışan sistem 30 dakika boyunca aralıksız çalışabiliyor

---

## 📆 18 Mayıs — Pazartesi (Sprint 2 Başlangıç)

**Günün Hedefi:** FSM çekirdeğini sensörlere bağlamak — sistemin "ruhunu" oluşturmak.

### 👤 Ü1 — Donanımcı
- [ ] Devre üzerine plastik kutu deneme yerleşimi: tüm bileşenler kutuya sığıyor mu?
- [ ] Kabloları **düzgün boyutlamaya başla**: uzunlukları kes, JST konnektörler için crimp
- [ ] **Bisikletin yanına git**: gerçek montaj noktasını test et, ölçüm al
- [ ] PAM8403+Hoparlör için kutu delik planı (hoparlör ağızı dışarıya bakacak)

### 👤 Ü2 — Beyin (Çok yoğun gün)
- [ ] **FSM çekirdeği + sensör entegrasyonu**: `firmware/src/main_v1.py`
  - [ ] FSM instance oluştur
  - [ ] IMU thread → magnitude hesapla → eşik kontrol → FSM'e event gönder
  - [ ] Reed thread → açılırsa FSM'e TAMPER event gönder
  - [ ] Web UI'dan gelen ARM/DISARM/RIDE komutları FSM'e event gönder
  - [ ] FSM state'ine göre: PAM8403/LED kontrol et
- [ ] Test senaryoları (manuel):
  - [ ] ARM → ARMED (mavi LED yavaş yanıp söner)
  - [ ] Hafif sallama → PRE-ALARM (sarı LED, 1 bip)
  - [ ] Şiddetli sallama → ALARM (kırmızı LED, PAM8403 sürekli alarm)
  - [ ] Web UI DISARM → DISARMED (LED kapalı)
- [ ] Çalışan görüntünün videosunu çek

### 👤 Ü3 — Göz/Ses
- [ ] **Kamera + FSM entegrasyonu**:
  - [ ] FSM ALARM state'ine geçtiğinde Camera task tetiklensin
  - [ ] Telegram bot'a fotoğraf + alarm mesajı gitsin
  - [ ] Mesaj formatı: "🚨 ALARM @ 18:42:15 — IMU magnitude: 1.6g — Photo attached"
- [ ] **Web UI'a görsel feedback**:
  - [ ] State değiştiğinde renk değişsin (yeşil=disarmed, mavi=armed, sarı=pre-alarm, kırmızı=alarm)
  - [ ] Son alarm fotoğrafı UI'da gösterilsin (alarm durumu için debug)

### 🌙 Akşam Sync (KRİTİK GÜN)
- main_v1.py çalışıyor mu? Kaç dakika boyunca crash etmeden çalıştı?
- Yarın hocanın 19 May deadline'ı için demo hazır mı?
- Gece veya yarın sabah son rötuş için ne kaldı?

### ⚠️ Bugünün Riski
**Eğer main_v1.py bugün çalışmazsa**, yarın hocanın deadline'ına yetiştirme stresi yüksek olur. Bu yüzden en azından **basit bir demo** çalışsın (IMU → Buzzer minimum).

---

## 📆 19 Mayıs — Salı 🚨 DONANIM PROTOTİPİ DEADLINE 

**Günün Hedefi:** Hocanın takvimindeki "Hardwareprototyp funktionsfähig" milestone'u. Demo videosu çek, GitHub'a yükle.

> **Not:** 19 Mayıs Türkiye'de resmi tatil (Atatürk'ü Anma, Gençlik ve Spor Bayramı). Ama proje deadline'ı bu tarih. Çalışmaya hazır olun.

### 🤝 Sabah (09:00 - 12:00) — Final Test
- [ ] Sistemi sabahtan başla, **tam 30 dakika** boyunca aralıksız çalışsın
- [ ] Bu süre içinde:
  - [ ] 5 farklı arm/disarm denemesi
  - [ ] 3 farklı pre-alarm tetikleme (hafif dokunmalar)
  - [ ] 2 farklı alarm tetikleme (sallama)
  - [ ] 1 tamper test (reed switch açma)
- [ ] Hata sayısını say. Hedef: **0 crash**.

### 🤝 Öğle (13:00 - 15:00) — Demo Videosu (Sprint 2)
- [ ] Profesyonel demo videosu çek (3-5 dakika):
  - [ ] Sistem tanıtım (15 sn)
  - [ ] Donanım yakın çekim (30 sn)
  - [ ] Senaryolar (3 dk):
    - Park ediyorum → ARM
    - Hafif rüzgar → no alarm (yanlış alarm engelleme!)
    - Hafif dokunma → PRE-ALARM
    - Hırsızlık → ALARM + Telegram bildirim
    - DISARM
  - [ ] Sonuç (30 sn): "Sprint 2 hedefimiz tamamlandı"
- [ ] `presentation/raw/sprint2_milestone.mp4` olarak kaydet

### 👤 Ü2 — Beyin (Öğleden sonra)
- [ ] **Adaptif eşik algoritması** ekle:
  - [ ] Son 30 saniyenin magnitude değerlerini bir ring buffer'da tut
  - [ ] mean ± 3·std → adaptif eşik
  - [ ] State ARMED iken sürekli güncelle, ALARM/PRE-ALARM'da güncelleme yapma
- [ ] **Kalman filtresi**: scipy ile basit 1D Kalman uygula (ham magnitude → smoothed magnitude)
  - [ ] `firmware/src/algorithms/kalman.py`
  - [ ] Önce/sonra grafik göster (yine matplotlib)

### 👤 Ü1 — Donanımcı
- [ ] Donanım fotoğrafları profesyonel çek: rapor için
  - [ ] Pi + sensörler breadboard üstünde (üstten ve yandan)
  - [ ] Kutuya yerleştirilmiş hali
  - [ ] Bisikletin sele altına monte edilmiş hali (eğer kutu hazırsa)
- [ ] Devre şemasını v2 olarak güncelle (aslında çalışan halini yansıt)

### 👤 Ü3 — Göz/Ses
- [ ] Demo videosunu kurgula (DaVinci Resolve / iMovie / CapCut):
  - [ ] Açılış/kapanış logosu
  - [ ] Yazılı altyazılar (senaryolar için)
  - [ ] Müzik (telifsiz)
- [ ] GitHub'da Sprint 2 release'i oluştur:
  - [ ] Tag: `v0.2-sprint2`
  - [ ] Release notes: tamamlananlar listesi
  - [ ] Demo video link

### 🌙 Akşam Sync — Sprint 2 Milestone Kutlaması 🎉
- Hocanın deadline'ı tamamlandı mı? Tüm bileşenler hazır mı?
- Demo videosu hazır mı?
- GitHub release açıldı mı?

### ⚠️ Bugünün Riski
Tatil olduğu için aksaklık olabilir (kargo, market, insanlar uygun olmayabilir). Önceden hazırlık yap.

---

## 📆 20 Mayıs — Çarşamba

**Günün Hedefi:** Sprint 2'nin geri kalan hedefleri (Kalman, adaptif eşik test, montaj iyileştirme).

### 👤 Ü1 — Donanımcı
- [ ] **3D baskı kutuyu test et** (eğer geldi ise):
  - [ ] Bileşenler içine sığıyor mu?
  - [ ] Kapağı açma/kapama mıknatıs reed switch'i tetikliyor mu?
  - [ ] Sensörler/kameralar için açıklık doğru yerde mi?
- [ ] **Bisikletin yanında uzun süreli test**:
  - [ ] Bisikleti yere yatay yerleştir, kutuyu monte et
  - [ ] 1 saat boyunca cihaz çalışsın, yanlış alarm var mı?
  - [ ] Sıcaklık logla, INA219 ile pil tüketimi takibi
- [ ] Pil ömrü ilk tahmin: bu hızda kaç saat dayanır?

### 👤 Ü2 — Beyin
- [ ] **Adaptif eşik gerçek dünya testi**:
  - [ ] Sessiz oda: eşik değer kaç (~0.05g civarı bekle)
  - [ ] Açık pencere yanı (rüzgar): eşik değer kaç (~0.15g)
  - [ ] Pi'nın yanında titreşimli laptop: eşik kaç
  - [ ] Bu verileri matplotlib ile grafikle, rapora ekle
- [ ] **Modüler kod düzeni** (kod kalitesi puanı için ⭐):
  - [ ] `main.py` parçala → her sürücü ayrı dosyada (zaten yapıldı)
  - [ ] `config.py` → eşik değerleri, GPIO numaraları, vs.
  - [ ] `logger.py` → ortak log fonksiyonu (rotating file handler)
  - [ ] Her dosyaya docstring ekle

### 👤 Ü3 — Göz/Ses
- [ ] **Görüntü işleme algoritmasını güçlendir** 🎁 (kamera bonus için kritik):
  - [ ] Sadece motion detection değil, **insan algılama** ekle
  - [ ] Hafif yöntem: HOG descriptor (`cv2.HOGDescriptor_getDefaultPeopleDetector()`)
  - [ ] Veya MobileNet-SSD (Pi'da `cv2.dnn` modülü)
  - [ ] "İnsan tespit edildi" event'i FSM'e gönder → daha agresif alarm
- [ ] Test: bisikletin önünden geçen biri varsa "PERSON" log'u atılıyor mu?

### 🌙 Akşam Sync
- Adaptif eşik yanlış alarmları azalttı mı?
- Görüntü işleme insan algılıyor mu?
- 1 saatlik testte cihaz crash etti mi?

### ⚠️ Bugünün Riski
**Pi'da OpenCV insan algılama yavaş çalışabilir.** Eğer FPS 5'in altına düşerse → bunu daha düşük frekansta (1 fps) çağır, ya da MobileNet quantize edilmiş versiyon kullan.

---

## 📆 21 Mayıs — Perşembe

**Günün Hedefi:** İletişim katmanını güçlendir + ride mode + rapor başlangıcı.

### 👤 Ü1 — Donanımcı
- [ ] **Mekanik dokümantasyon**:
  - [ ] Kutu STL dosyası repo'da
  - [ ] Bisiklet montaj kılavuzu (fotolu, 1 sayfa Markdown)
  - [ ] `hardware/mounting_guide.md`
- [ ] EMI/gürültü test: bisiklet yakınından motor geçince sistem etkileniyor mu? (bayağı paranoyak ama hocaya iyi gözükür)

### 👤 Ü2 — Beyin
- [ ] **RIDE mode logic**:
  - [ ] Web UI'dan RIDE seçilirse → IMU sürekli oku ama alarm karar mantığını bypass et
  - [ ] Sadece tamper aktif kalsın
  - [ ] RIDE'da telemetri logla (ileride GPS eklenirse hız/mesafe için altyapı)
- [ ] **Tamper logic özelleştirme**:
  - [ ] Tamper alarmı normal DISARM_BTN ile sönmesin
  - [ ] Sadece web UI'da "tamper_disarm" + parola ile sönsün
  - [ ] Bu, raporda "katmanlı güvenlik" olarak anlatılacak

### 👤 Ü3 — Göz/Ses
- [ ] **Rapor yazımına başlangıç** (erken başlamak iyi olur, son güne bırakma):
  - [ ] Şablon: LaTeX (Overleaf) veya Word — ekiple karar ver
  - [ ] Kapak + içindekiler + giriş bölümü
  - [ ] **Bölüm 3: Donanım Tasarımı** ilk taslağı yaz (Ü1 ile birlikte)
- [ ] Telegram bot'a komutlar:
  - [ ] `/photo` → Pi Camera'dan anlık fotoğraf çekip gönder
  - [ ] `/temp` → CPU + ortam sıcaklığı
  - [ ] `/battery` → INA219'dan tüketim ve tahmini kalan süre
  - [ ] `/log_last_24h` → son 24 saatteki olaylar

### 🌙 Akşam Sync
- RIDE mode çalışıyor mu? Bisiklette sürerken alarm vermez mi?
- Tamper logic iyi mi?
- Rapor şablonu hazır mı? Ekipten kim yazıyor?

---

## 📆 22 Mayıs — Cuma

**Günün Hedefi:** Sprint 2'yi temiz kapatmak, RTOS'a (Sprint 3) zihinsel hazırlık.

### 🤝 Sabah (10:00 - 13:00) — Sprint 2 Final Test
- [ ] **Tam senaryo testi (1 saat aralıksız)**:
  - [ ] Sistem sabah 10:00'da başlar
  - [ ] 5 dakikada bir farklı durum tetiklenir
  - [ ] 11:00'da hala çalışıyor mu? Kaç hata oldu?
- [ ] Sonuçları `docs/sprint2_endurance_test.md` olarak yaz

### 👤 Ü1 — Donanımcı (Öğleden sonra)
- [ ] Bisiklet montaj denemesi: 30 dk gerçek bisiklet üstünde
- [ ] Bisikletle hareket halindeyken (RIDE mode) IMU verisi nasıl? Yanlış alarm tetikliyor mu?

### 👤 Ü2 — Beyin
- [ ] **PREEMPT-RT'ye taşıma planı** (Pazar gece toplantısı için hazırlık):
  - [ ] Hangi task'lar C'ye taşınacak (kritik olanlar): IMU, FSM, Reed
  - [ ] Hangi task'lar Python'da kalacak: Camera, Telegram, Web UI, Logger
  - [ ] Veri köprüsü: Python ↔ C arasında shared memory veya POSIX MQ
  - [ ] **C kodunu mümkün olduğunca minimal yap** — riski düşürür
- [ ] Plan dokümanı `docs/sprint3_rtos_plan.md`

### 👤 Ü3 — Göz/Ses
- [ ] Rapor giriş bölümü tamamla (1.5 sayfa):
  - [ ] Motivasyon (bisiklet hırsızlığı istatistikleri, web search ile bul)
  - [ ] Problem tanımı
  - [ ] Hedefler
  - [ ] Katkılar (özgün ne yapıyoruz?)
- [ ] Sprint 2 demo videosunu son haline getir, GitHub release'e bağla

### 🌙 Akşam Sync — Sprint 2 KAPANIŞI
- Hocanın 19 May deadline'ı geçildi mi? ✅
- Sprint 2'nin tüm hedefleri tamamlandı mı?
- Sprint 3'e zihinsel hazırlık: Priority Inheritance konusunda kim ne biliyor?

---

## 📆 23-24 Mayıs — Cumartesi & Pazar

### Cumartesi (23 May) — Telafi günü
- [ ] Sprint 2'den sarkanlar (varsa) tamamla
- [ ] Ü2: PREEMPT-RT için **2 saatlik öğrenme bloğu**:
  - [ ] `pthread` + `sched_setscheduler` örnekleri oku
  - [ ] `pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT)` örneği
  - [ ] `cyclictest`'in çıktısını yorumlamayı öğren
- [ ] Ü1: Donanım bakım — kabloları düzenle, gevşek lehimleri sıkıştır

### Pazar (24 May) — Sprint 3 Hazırlık 🚨
- [ ] 🤝 **Önemli toplantı (akşam 19:00, 1.5 saat)**:
  - [ ] Sprint 3 planını okuyun
  - [ ] **Priority Inheritance deneyini birlikte tasarlayın**:
    - Düşük öncelikli task X mutex'i tutuyor
    - Yüksek öncelikli task Y bekliyor
    - Orta öncelikli task Z (CPU yiyici) çalışıyor
    - PRIO_INHERIT'siz: Y çok bekler
    - PRIO_INHERIT'le: X'in önceliği geçici Y'ye yükselir, hızlı tamamlanır
  - [ ] Bu deneyin **önce/sonra grafiklerini** hazırlayacağımız konusunda anlaş
- [ ] Pazartesi sabah için iş tablosu hazır


---
---

# ⏱️ SPRINT 3 — RTOS + Priority Inheritance + İletişim (25-29 Mayıs)

## 🎯 Sprintin Ana Hedefi
**26 Mayıs Salı**: hocanın "RTOS-Integration, Nachweis Priority Inheritance" milestone'u. Bu hocanın **en kritik puanı (50 pts ZORUNLU)**. Bu hafta priority inheritance hem implement edilir, hem de **ölçümle kanıtlanır**.

> **NOT:** Bu hafta Türkiye'de Kurban Bayramı tatili olabilir (yaklaşık 27 May). Ekibe göre ayarla, eğer çakışırsa hafta öncesi/sonrası sıkışır.

## 🏁 Sprint Sonunda Elde Olması Gerekenler
- [ ] ⭐⭐⭐ **Priority Inheritance protokolü implement edildi** (C kodu, PTHREAD_PRIO_INHERIT)
- [ ] ⭐⭐⭐ **Priority Inversion deneyi yapıldı**: PRIO_INHERIT olan/olmayan ölçüm karşılaştırması
- [ ] Kritik task'lar C'ye taşındı (IMU, FSM)
- [ ] Python ↔ C iletişimi kuruldu (POSIX MQ veya shared memory)
- [ ] BLE veya MQTT iletişim çalışıyor
- [ ] Tamper, RIDE, ALARM senaryolarının hepsi RT context'te çalışıyor

---

## 📆 25 Mayıs — Pazartesi (Sprint 3 Başlangıç)

**Günün Hedefi:** PREEMPT-RT'da minimal C uygulamasını çalıştır. Priority Inheritance kavramını koda dök.

### 👤 Ü2 — Beyin (Bu hafta yıldız oyuncu) ⭐
- [ ] **Sabah Bloku — Hello-RT in C** (`firmware/src/rtos/hello_rt.c`):
  - [ ] 3 thread: high (prio 80), mid (prio 50), low (prio 20)
  - [ ] Hepsi `SCHED_FIFO`
  - [ ] Her thread 1 saniye bir mesaj print etsin
  - [ ] Compile: `gcc -o hello_rt hello_rt.c -lpthread`
  - [ ] Çalıştır: `sudo ./hello_rt`
  - [ ] Beklenen: high önce, low sonra
- [ ] **Öğleden sonra — Priority Inversion Demo (BAŞYAPIT!)** ⭐⭐⭐
  - [ ] `firmware/src/rtos/prio_inv_demo.c`:
    - Thread Low (prio 20): mutex al, 5 saniye CPU işi yap, mutex bırak
    - Thread Mid (prio 50): sürekli CPU yakar (mutex'e dokunmaz)
    - Thread High (prio 80): mutex al, kısa iş, bırak
  - [ ] **Ölçüm**: High thread'in mutex'i bekleme süresi
  - [ ] İki versiyon:
    1. `PTHREAD_PRIO_NONE` (varsayılan) → High çok bekler
    2. `PTHREAD_PRIO_INHERIT` → Low'un önceliği yükselir, hızlı çözülür
  - [ ] CSV log: `timestamp, thread_id, event` (event: lock_request, lock_acquired, lock_released)

### 👤 Ü1 — Donanımcı
- [ ] Cihazı bisiklette **gerçek arazi testi**:
  - [ ] Bisiklete bin, 1 km tur at (RIDE mode)
  - [ ] Sonra park et, ARM
  - [ ] 1 saat bekle, yanlış alarm var mı?
- [ ] Pil ömrü ölçümü: pili %100 doldur, sistemi armed mode'da çalıştır, ne zaman kapanıyor?
  - [ ] Sonuç: "X saat dayanıyor"
- [ ] Termal stress testi: Pi'yı `stress-ng --cpu 4` ile 30 dk yükle, sıcaklık eğrisini logla

### 👤 Ü3 — Göz/Ses
- [ ] **MQTT broker kurulumu** (opsiyonel ama ölçeklenebilirlik puanı için):
  - [ ] Pi'da `mosquitto` kur
  - [ ] Veya bulut broker (HiveMQ test): test.mosquitto.org
  - [ ] `firmware/src/comm/mqtt.py`: alarm publish, status publish
  - [ ] Her olay JSON formatında topic'e gitsin
- [ ] **Rapor — Bölüm 4: Modelleme** taslağı (3 sayfa):
  - [ ] StateChart açıklaması
  - [ ] Petri ağı açıklaması  
  - [ ] UPPAAL zamanlı otomat (henüz hazırlanmamışsa Ü2 yardım eder, ama açıklama Ü3)

### 🌙 Akşam Sync
- Hello-RT çalışıyor mu? `cyclictest` skoru kaç?
- Priority Inversion demo'su ne durumda?
- Pil ömrü ne çıktı?

### ⚠️ Bugünün Riski
**PRIO_INHERIT deneyini doğru kurmak teknik olarak zor**. Eğer Ü2 takılırsa, gece yatmadan önce mutlaka ekibe söylesin — diğerleri yardım edebilir. Bu deney KRİTİK puan.

---

## 📆 26 Mayıs — Salı 🚨 PRIO_INHERIT DEADLINE

**Günün Hedefi:** Priority Inheritance ölçümlerini tamamla, grafikleri çıkar, raporun en güçlü bölümünü yaz.

### 🤝 Sabah (09:00 - 13:00) — Final Ölçüm Bloğu
- [ ] Ü2 + Ü1 birlikte:
  - [ ] `prio_inv_demo.c` her iki versiyonu çalıştır (10 koşum, 30 saniyelik)
  - [ ] CSV verilerini topla
  - [ ] Pi'da `stress-ng` ile arka plan yükü oluşturarak da test et (worst case)
- [ ] **Beklenen sonuç**:
  - PRIO_NONE: High thread max bekleme **>10 saniye**
  - PRIO_INHERIT: High thread max bekleme **<200 ms**
  - Bu fark grafikte **göze batar şekilde** görünmeli

### 👤 Ü3 — Grafikleme
- [ ] `tools/prio_inv_plot.py`:
  - [ ] CSV'leri oku
  - [ ] X ekseni: zaman
  - [ ] Y ekseni: bekleme süresi (logaritmik olabilir)
  - [ ] İki çizgi: PRIO_NONE (kırmızı) vs PRIO_INHERIT (yeşil)
  - [ ] Kaydet: `docs/figures/prio_inheritance_comparison.png` ⭐⭐⭐
- [ ] Bu grafiği **rapora ve sunuma** koy — bu sizin "para kazanan" görseliniz!

### 👤 Ü1 — Donanımcı
- [ ] **WCET ölçümü için fiziksel kurulum**:
  - [ ] Eğer logic analyzer varsa: GPIO pin (örn. 25) sniff modunda
  - [ ] Yoksa: osiloskop probu GPIO 25'e + GND
  - [ ] Yine yoksa: Pi'nın kendi `clock_gettime` ile (5 µs çözünürlük yeterli)
- [ ] Bisiklette uzun süreli test (3 saat) — çalışmaya devam mı, ne zaman duruyor?

### 👤 Ü2 — Beyin
- [ ] **Kritik task'ları C'ye port etme**:
  - [ ] `firmware/src/rtos/imu_task.c` — IMU okuma 100Hz, SCHED_FIFO prio 80
  - [ ] `firmware/src/rtos/fsm_task.c` — FSM logic, prio 70
  - [ ] Shared state: POSIX shm + PRIO_INHERIT mutex
  - [ ] Python tarafı `mmap` ile bu shared memory'i okuyabilir (Camera, Logger, Web UI için)
- [ ] **Hocanın istediği "Nachweis":**
  - [ ] Rapor için "PRIO_INHERIT Kanıtlama Bölümü" yaz (1.5 sayfa)
  - [ ] Önce kavramsal açıklama, sonra deney, sonra grafik, sonra yorum

### 🌙 Akşam Sync — KRİTİK MILESTONE 🎯
- Priority Inheritance grafiği hazır mı?
- C kodları repo'ya commit edildi mi?
- Hocanın 26 May milestone'u tamamlandı mı?

---

## 📆 27 Mayıs — Çarşamba

**Günün Hedefi:** WCET ölçümlerini başlat + iletişim katmanını sağlamlaştır.

### 👤 Ü2 — Beyin
- [ ] **WCET ölçüm framework'ü**:
  - [ ] `firmware/src/rtos/wcet_helper.c`:
    - `wcet_start(task_id)` → GPIO HIGH ya da timestamp kaydet
    - `wcet_stop(task_id)` → GPIO LOW ya da delta hesapla, log'a yaz
  - [ ] Tüm RT task'lara enstrüman ekle
  - [ ] 1000 iterasyon → her task için min/avg/max latency tablosu
- [ ] CPU stress yokken / varken karşılaştırma → rapor için tablo

### 👤 Ü1 — Donanımcı
- [ ] **INA219 enerji ölçüm framework'ü**:
  - [ ] `tools/energy_logger.py` — sürekli kayıt eden script
  - [ ] Her sistem state'inde 5 dakika logla:
    - DISARMED, ARMED (idle), PRE_ALARM, ALARM, RIDE, ECO
  - [ ] Sonuç: state-bazlı ortalama güç tüketimi (W)
- [ ] CSV → matplotlib grafiği: zaman vs güç, state'ler renkli

### 👤 Ü3 — Göz/Ses
- [ ] **Mobile-friendly Web UI iyileştirme**:
  - [ ] Bootstrap kullan, mobil görünümü düzelt
  - [ ] Telefon ekranında ARM/DISARM butonları büyük olsun
  - [ ] Son 10 olayın listesi (timestamp + olay tipi)
  - [ ] WebSocket ile gerçek zamanlı güncelleme (opsiyonel)
- [ ] Rapor — Bölüm 5: Yazılım Tasarımı (Ü2 ile birlikte yaz)
  - [ ] RTOS açıklaması
  - [ ] Task tablosu
  - [ ] Priority Inheritance bölümü ⭐
  - [ ] FSM kod özeti

### 🌙 Akşam Sync
- WCET ölçümleri için tablo dolduruldu mu?
- Enerji loglaması çalışıyor mu, veri toplanıyor mu?
- Rapor kaç sayfa şu anda?

---

## 📆 28 Mayıs — Perşembe

**Günün Hedefi:** İletişim — BLE veya WiFi/Telegram'ın hangisi MVP olacak son karar + Pareto için planlama.

### 👤 Ü3 — Göz/Ses (Yoğun gün)
- [ ] **BLE vs WiFi+Telegram karar verme**:
  - [ ] BLE peripheral kurulumu denedin mi?
  - [ ] Ne kadar pil yakıyor? (dakikalık tahmin)
  - [ ] Telegram daha pratik ama her zaman WiFi gerekiyor
  - [ ] **Karar**: MVP için **WiFi+Telegram** (zaten çalışıyor), BLE'yi "future work" olarak rapor et
- [ ] Telegram bot'a son özellikler:
  - [ ] `/photo` komutu çalışıyor mu?
  - [ ] `/disarm` komutu Web UI ile aynı mı? (her iki yoldan da gelmeli)
  - [ ] Bildirimde fotoğraf + IMU data'sı (özet)

### 👤 Ü2 — Beyin
- [ ] **Pareto deney tasarımı** (`tools/pareto_sweep.py`):
  - [ ] IMU sampling Hz'i parametre yap: [25, 50, 100, 200, 400]
  - [ ] Her Hz için 3 dakika çalıştır
  - [ ] Ölç: ortalama güç (W) + alarm reaksiyon süresi (ms)
  - [ ] Reaksiyon süresi: belirli bir zaman noktasında bisiklet sallanır → buzzer ne kadar sonra çalar?
- [ ] CSV → matplotlib scatter plot
- [ ] Pareto cephesi grafiği `docs/figures/pareto_front.png`

### 👤 Ü1 — Donanımcı
- [ ] **Termal modelleme ölçümü**:
  - [ ] Pi soğukken çalıştır, `vcgencmd measure_temp` ile sıcaklığı dakikada bir kaydet
  - [ ] Stress yükle (`stress-ng --cpu 4`), 30 dk
  - [ ] Sıcaklığın asimptota yaklaşması — RC modeli için fit
  - [ ] Eğri Python'da exponential fit → R_th, C_th, τ değerleri
- [ ] DHT22 ile ortam sıcaklığı paralel kayıt → ΔT hesabı
- [ ] Sonuç tabloya: `docs/thermal_model.md`

### 🌙 Akşam Sync
- Pareto deneyi başladı mı? Veri toplanıyor mu?
- Termal modelleme verisi alındı mı?
- Rapor toplam ne kadar?

### ⚠️ Bugünün Riski
**Pareto deneyi çok zaman alır** (5 senaryo × 3 dk + reset = ~20 dk). Bunu Pi'da background'da çalıştır, paralel başka şeyler yap.

---

## 📆 29 Mayıs — Cuma

**Günün Hedefi:** Sprint 3 kapanış + tüm RTOS dokümanlarını derle + büyük entegrasyon testi.

### 🤝 Sabah (10:00 - 13:00) — Büyük Entegrasyon Testi
- [ ] Tüm sistemi C+Python karma çalıştır:
  - [ ] C task'ları: IMU, FSM (RT prio'larla)
  - [ ] Python: Camera, Telegram, Web UI, Logger, INA219
- [ ] 2 saat aralıksız çalışsın
- [ ] Çeşitli senaryolar uygula (arm, disarm, alarm, tamper, ride)
- [ ] Hata olmazsa ✅ Sprint 3 başarılı

### 👤 Ü2 — Beyin (Öğleden sonra)
- [ ] Rapor — Bölüm 5 son hali:
  - [ ] PREEMPT-RT kurulum
  - [ ] Task tablosu (öncelik, periyot, WCET)
  - [ ] Priority Inheritance (3 sayfa) ⭐⭐⭐
  - [ ] Mutex tasarımı
  - [ ] Hata yönetimi
- [ ] `cyclictest` ile son ölçüm — rapora final grafik

### 👤 Ü1 — Donanımcı
- [ ] Rapor — Bölüm 6: Donanım Tasarımı son hali (4 sayfa):
  - [ ] BOM tablosu (gerçek alınanlar)
  - [ ] Devre şeması
  - [ ] Sensör seçim gerekçeleri
  - [ ] Mekanik tasarım (kutu, montaj)
  - [ ] Güç sistemi (pil, BMS, MT3608)
  - [ ] Mekanik fotoğraflar (kutu, bisikletteki montaj)

### 👤 Ü3 — Göz/Ses
- [ ] Pareto cephesi grafiği son hali
- [ ] Rapor — Bölüm 7: Görüntü İşleme (1.5 sayfa)
  - [ ] OpenCV motion detection açıklaması
  - [ ] HOG insan algılama (eğer dahil ettiyseniz)
  - [ ] Performans: FPS, hassasiyet
- [ ] Tüm grafiklerin ortak stil olarak kontrolü (font, renk paleti)

### 🌙 Akşam Sync — Sprint 3 KAPANIŞI 🎯
- Priority Inheritance tamamlandı mı? (en kritik puan)
- Rapor şu an kaç sayfa? (hedef: 15+ sayfa olmalı)
- Sprint 4 (metrikler) için hazır mıyız?

---

## 📆 30-31 Mayıs — Cumartesi & Pazar

### Cumartesi (30 May)
- [ ] 🤝 Sabah toplantısı (sadece 30 dk): "Bu hafta nerelerde takıldık?"
- [ ] Sarkanlar tamamlanır
- [ ] Ü1: Bisiklet montajı son hali — 24 saat sürekli arazi testi başlat (gece dahil)
- [ ] Ü2: WCET ölçümlerini bitir, eksik task'lar varsa ekle
- [ ] Ü3: Demo videosu için yeni çekim planı (final video için ham malzeme)

### Pazar (31 May)
- [ ] Sabah: 24 saatlik testin sonuçlarını topla, hata varsa bug fix
- [ ] 🤝 **Sprint 4 + Final Sprint hazırlık toplantısı** (akşam 19:00, 2 saat):
  - [ ] Geriye 5 gün kaldı (1-5 Haziran)
  - [ ] Metrikler tamamlanacak
  - [ ] Rapor 25-30 sayfaya çıkacak
  - [ ] Video kurgusu, sunum, Turnitin
  - [ ] **Görev paylaşımı netleşir**


---
---

# 📊 SPRINT 4 — Değerlendirme Metrikleri (1-2 Haziran)

## 🎯 Sprintin Ana Hedefi
**2 Haziran Salı**: hocanın "Evaluierungsmetriken (WCET, Energie) abgeschlossen" milestone'u. Tüm metrikler ölçülür, grafiklenir, rapora yerleştirilir.

## 🏁 Sprint Sonunda Elde Olması Gerekenler
- [ ] WCET tablosu hazır (10+ task için min/avg/max)
- [ ] Enerji tüketimi tablosu (state-bazlı, günlük tahmin)
- [ ] Termal modelleme grafiği (R_th, C_th, doğrulama)
- [ ] Pareto cephesi grafiği (enerji ↔ reaksiyon süresi)
- [ ] CPU/RAM/Disk performans grafikleri
- [ ] Tüm grafikler tutarlı stilde, rapora hazır
- [ ] Rapor 22+ sayfaya ulaştı

---

## 📆 01 Haziran — Pazartesi

**Günün Hedefi:** WCET, Enerji, Termal — tüm sayısal verileri rapora hazır hale getir.

### 👤 Ü2 — Beyin (Sayısallaştırma günü)
- [ ] **WCET tablosunu finalize et** (`docs/figures/wcet_table.md`):

```
| Task              | Min(µs) | Avg(µs) | Max(µs) | Bütçe(µs) | Ratio | Durum |
|-------------------|---------|---------|---------|-----------|-------|-------|
| reed_isr          | 12      | 18      | 38      | 50        | 0.76  | ✅    |
| imu_sampling      | 850     | 1100    | 1420    | 1500      | 0.95  | ✅    |
| fsm_core          | 80      | 150     | 480     | 500       | 0.96  | ✅    |
| ...               |         |         |         |           |       |       |
```

- [ ] Histogram grafikleri: her task için max latency dağılımı
- [ ] `cyclictest` final çalışma (1 saat) → bunun da grafiği

### 👤 Ü1 — Donanımcı (Enerji)
- [ ] **Enerji tablosunu finalize et** (`docs/figures/energy_table.md`):

```
| State        | V (V) | I (mA) | P (W) | 5h tüketim (Wh) |
|--------------|-------|--------|-------|------------------|
| DISARMED     | 5.05  | 95     | 0.48  | 2.4              |
| ARMED        | 5.04  | 380    | 1.92  | 9.6              |
| PRE_ALARM    | 5.04  | 520    | 2.62  | -                |
| ALARM        | 5.03  | 920    | 4.62  | -                |
| RIDE         | 5.04  | 280    | 1.41  | 7.0              |
| ECO          | 5.05  | 240    | 1.21  | 6.0              |
```

- [ ] **Pil ömrü tahmini**:
  - [ ] 18650 (3000 mAh) × 1 hücre × 3.7V = 11.1 Wh
  - [ ] ARMED durumunda 1.92 W → 5.7 saat
  - [ ] Karma kullanımda (ARMED %80, ALARM %5, RIDE %15) → daha fazla
  - [ ] **Çıktı**: "Sistem normal kullanımda **6-8 saat** dayanıyor" (önemli sayı, sunuma koy)

### 👤 Ü3 — Göz/Ses
- [ ] **Termal modelleme grafiği**:
  - [ ] X: zaman (dk), Y: sıcaklık (°C)
  - [ ] İki çizgi: ölçüm (ham veri) + model (exponential fit)
  - [ ] Etiketler: stress başladı, soğuma başladı
  - [ ] R_th, C_th değerleri grafikte annotation
  - [ ] `docs/figures/thermal_model.png`
- [ ] **Pareto grafiği son haline**:
  - [ ] X: ortalama güç (W), Y: reaksiyon süresi (ms)
  - [ ] Her nokta etiketli (Hz değeri)
  - [ ] **Pareto cephesi** (yeşil çizgi) belirtilmiş
  - [ ] **Domine edilen noktalar** (kırmızı x ile) işaretli
  - [ ] Annotation: "100Hz seçildi → denge"
  - [ ] `docs/figures/pareto_front.png`

### 🌙 Akşam Sync
- 4 ana grafik (WCET, Enerji, Termal, Pareto) hazır mı?
- Hepsi aynı stil/font/renk paletinde mi?
- Yarın deadline (2 Haz) için ne kaldı?

### ⚠️ Bugünün Riski
**Grafiklerin tutarsız olması** → rapor amatör görünür. Tek bir matplotlib stil dosyası kullan (`tools/plot_style.py` import et).

---

## 📆 02 Haziran — Salı 🚨 METRİK DEADLINE

**Günün Hedefi:** Hocanın "Evaluierungsmetriken abgeschlossen" milestone'u + rapor 22+ sayfa.

### 🤝 Sabah (09:00 - 13:00) — Final Metrik Bloğu
- [ ] Tüm grafikler PDF'e dönüştürülebilir kalitede mi? (vektörel SVG/PDF)
- [ ] CPU/RAM ölçümleri ekleniyor: `docs/figures/system_load.png`
  - [ ] `top -b -n 1 | head -20` her dakika çalıştır → tüm proje süresinde ortalama
  - [ ] Hocanın isteği: CPU<%70, RAM<%80
- [ ] Sıcaklık ölçümü tablo: max sıcaklık < 80°C ✅

### 👤 Ü2 — Beyin (Öğleden sonra)
- [ ] **Rapor — Bölüm 8: Değerlendirme** son hali (4 sayfa):
  - [ ] 8.1 WCET — tablo + histogram + yorum (1 sayfa)
  - [ ] 8.2 Enerji — tablo + grafik + DPM/DVS açıklaması (1.5 sayfa)
  - [ ] 8.3 Termal — model + grafik + yorum (0.75 sayfa)
  - [ ] 8.4 Pareto — grafik + yorum (0.75 sayfa)
- [ ] **Rapor — Bölüm 9: Sonuçlar ve Tartışma** taslak (1 sayfa)

### 👤 Ü1 — Donanımcı
- [ ] **Rapor — Donanım eki**:
  - [ ] Devre şeması büyük boyut PDF
  - [ ] Mekanik çizimler
  - [ ] BOM tablosu (gerçek fiyatlar)
- [ ] Bisikletten cihazı sök, son fotoğraflar çek
- [ ] **Hocaya gösterilecek demo planı**: hangi sırada ne göstereceksin?

### 👤 Ü3 — Göz/Ses
- [ ] **DEMO VİDEOSU başla** (max 5 dk):
  - [ ] Storyboard yaz: hangi sahne ne kadar sürecek?
  - [ ] Çekim listesi:
    1. Açılış (10 sn): proje adı, ekip
    2. Problem (30 sn): bisiklet hırsızlığı görsel + ses
    3. Sistem tanıtım (45 sn): donanım yakın çekim, blok diyagram
    4. Senaryo demo (2 dk): canlı kayıt
    5. Metrikler (45 sn): grafiklerin akışı
    6. Sonuç (30 sn): "neyi başardık, neyi geliştireceğiz"
  - [ ] Bugün ham çekimleri al (ses ayrı kayıt — daha temiz olur)
- [ ] **Slayt sunumu başla** (10-12 slayt):
  - [ ] PowerPoint veya Beamer (LaTeX) — Ü3 hangisini biliyor?

### 🌙 Akşam Sync — METRİK MILESTONE 🎯
- Hocanın 2 Haz milestone'u tamamlandı mı?
- Rapor sayfa sayısı? (hedef: 22+, Sprint 4 sonu için iyi)
- Demo videosu çekimi başladı mı?


---
---

# 🏁 FINAL SPRINT — Rapor + Video + Sunum + TESLİM (3-5 Haziran)

## 🎯 Sprintin Ana Hedefi
Rapor finalize, video kurgu, sunum hazır, Turnitin, basılı ciltli rapor → **05 Haziran 14:45 C208**'e teslim.

## 🏁 Sprint Sonunda Elde Olması Gerekenler
- [ ] ⭐ **Rapor PDF** (20-30 sayfa) hazır + 3 imza
- [ ] ⭐ **Basılı + ciltli rapor** elde
- [ ] ⭐ **Video** (≤5 dk) MP4 olarak GitHub'a + Classroom'a
- [ ] ⭐ **Sunum** (10-12 slayt) PDF olarak Classroom'a
- [ ] ⭐ **Turnitin raporu** PDF olarak Classroom'a (kayıt: TAU.INF.208)
- [ ] ⭐ **GitHub repo** public, README dolu, MIT lisans, CONTRIBUTING.md
- [ ] **05 Haz 14:45 C208**'e elden teslim
- [ ] **05 Haz 23:00**'a kadar Classroom upload

---

## 📆 03 Haziran — Çarşamba (Yazma günü — yoğun)

**Günün Hedefi:** Raporu 25-28 sayfa civarına çıkar + tüm bölümleri tutarlı hale getir.

### 🤝 Sabah (09:00 - 13:00) — Rapor Konsolidasyon Bloğu
- [ ] Üçü birlikte Google Docs'ta açık → her bölümü beraber gözden geçir
- [ ] **Bölüm sırası kontrolü**:
  1. Kapak + İçindekiler
  2. Özet (TR + DE)
  3. Giriş & Motivasyon
  4. Sistem İsterleri
  5. Modelleme (StateChart, Petri, UPPAAL)
  6. Donanım Tasarımı
  7. Yazılım Tasarımı (RTOS, FSM, Priority Inheritance)
  8. Görüntü İşleme
  9. Değerlendirme (WCET, Enerji, Termal, Pareto)
  10. Test Sonuçları
  11. Tartışma & Gelecek Çalışmalar
  12. Kaynakça
  13. Ek A: Devre şeması
  14. Ek B: Önemli kod parçacıkları

### 👤 Ü1 — Donanımcı (Öğleden sonra)
- [ ] Donanım bölümü (Bölüm 6) son hali, görseller yerinde
- [ ] BOM tablosu son hali, fiyatlar dahil
- [ ] **Tüm görsellerin yüksek çözünürlükte olduğundan emin ol** (300 DPI)
- [ ] Bisikletteki son demo fotoğrafları rapor "kapağı" gibi koy

### 👤 Ü2 — Beyin
- [ ] Yazılım bölümü (Bölüm 7) son hali — özellikle Priority Inheritance bölümü 3 sayfa
- [ ] Değerlendirme bölümü (Bölüm 9) tüm grafiklerle dolu
- [ ] Kaynakça (Bölüm 12): IEEE veya APA formatında
- [ ] Modelleme bölümü (Bölüm 5): StateChart + Petri + UPPAAL anlatımları

### 👤 Ü3 — Göz/Ses
- [ ] Giriş bölümü (Bölüm 3): motivasyon güçlü, hooks var
- [ ] Görüntü işleme bölümü (Bölüm 8) son hali
- [ ] Test sonuçları bölümü (Bölüm 10): tabloları temiz
- [ ] Tartışma & Gelecek Çalışmalar (Bölüm 11): "BLE", "GPS", "Cloud dashboard" gibi
- [ ] **Özet (Bölüm 2)**: TR + DE versiyonları (DE için Google Translate sonra Ü2 düzeltir, Ü2 belki Almanca biliyordur)

### 🌙 Akşam Sync
- Rapor toplam sayfa sayısı? (hedef: 25+)
- Hangi bölümler "%80 hazır"? Hangileri eksik?
- Yarın hangi bölüme öncelik verilecek?

### ⚠️ Bugünün Riski
**Çakışan değişiklikler**. Aynı paragrafa iki kişi dokunursa karışır. Google Docs'un comment ve suggestion özelliklerini aktif kullan.

---

## 📆 04 Haziran — Perşembe (SON RÖTUŞ)

**Günün Hedefi:** Rapor son haline gelsin, video kurgulansın, sunum hazır olsun, **TURNITIN gönder**.

### 🤝 Sabah (09:00 - 12:00) — Rapor Final Pass
- [ ] **Üç kişi sırayla** raporu baştan sona okur, hata bulanlar:
  - [ ] Yazım hatası
  - [ ] Tutarsızlık (örn. 100Hz dediğin yerde 200Hz olmamalı)
  - [ ] Eksik atıf
  - [ ] Çift kullanılan görsel
- [ ] **Format kontrolü**:
  - [ ] Margin (2.5 cm), font (Times 11pt veya Arial 10pt — tutarlı)
  - [ ] Sayfa numaraları
  - [ ] Bölüm numaralandırması
  - [ ] Görsel altyazıları "Şekil 1: ...", "Tablo 1: ..."

### 👤 Ü3 — Video Kurgu (Tüm gün)
- [ ] DaVinci Resolve / iMovie / CapCut
- [ ] Storyboard sırasıyla:
  1. Açılış (10 sn) — proje adı, ekip
  2. Problem (30 sn) — bisiklet hırsızlığı kısa kurgu, ses anlatım
  3. Sistem (45 sn) — donanım, mimari, mod akışı
  4. Demo (2 dk) — gerçek senaryolar
  5. Metrikler (45 sn) — grafikler kısa
  6. Sonuç (30 sn) — "120 puan hedefi, açık kaynak, gelecek"
- [ ] **Süre kontrolü**: 5 dakikayı kesinlikle geçme
- [ ] Müzik (telifsiz, YouTube Audio Library veya Pixabay)
- [ ] Altyazı (Türkçe + İngilizce)
- [ ] Export: 1080p, MP4, H.264, ~200 MB

### 👤 Ü2 — Sunum (Slaytlar)
- [ ] 10-12 slayt:
  1. Kapak (proje, ekip, tarih)
  2. Problem & motivasyon
  3. Sistem mimarisi
  4. StateChart
  5. Donanım (foto + bileşenler)
  6. RTOS task tablosu + Priority Inversion grafiği ⭐⭐⭐
  7. FSM senaryolar
  8. WCET grafiği + tablo
  9. Enerji + Termal modelleme
  10. Pareto cephesi
  11. Demo video link veya canlı demo
  12. Sonuç + gelecek + soru-cevap
- [ ] PowerPoint hazırlanırsa export PDF
- [ ] Sunum süresi: ~10-12 dakika (slayt başı 1 dakika)

### 👤 Ü1 — Turnitin + Basım
- [ ] **Turnitin raporu**:
  - [ ] Rapor metin halini (Word) Turnitin sistemine gönder
  - [ ] Sınıf ID: #48947170
  - [ ] Kayıt anahtarı: TAU.INF.208
  - [ ] Benzerlik %20 altında olsun (ideal); değilse Ü3 ile düzelt
  - [ ] Raporun PDF çıktısını al
- [ ] **Baskı için yazıcı/matbaa hazırlığı**:
  - [ ] Üniversite kütüphanesi yazıcısı uygun mu?
  - [ ] Yoksa yakın matbaa: spiral cilt 30 sayfa ~50 TL
  - [ ] Sınıf saatinden 1 gün önce baskı yap, son dakika riski almama!

### 🌙 Akşam Sync (UZUN, son toplantı)
- Rapor PDF olarak final mi? (Drive'da `final_v1.pdf`)
- Video MP4 olarak final mi?
- Sunum PDF/PPTX final mi?
- Turnitin raporu PDF olarak final mi?
- Basım yarın mı, bu gece mi?

### ⚠️ Bugünün Riski
**Turnitin yüksek benzerlik** veriyorsa panik yok. En sık kaynaklar: kütüphane docs'ları (Marwedel kitabından kopyalama), kendi exposé'niz (kendi metnize benzerse problem değil ama Turnitin işaretler — açıklama yazılır).

---

## 📆 05 Haziran — Cuma 🚨 SON TESLİM GÜNÜ

**Günün Hedefi:** Sabah son kontrol, **14:45**'te C208'de elden teslim, 23:00'a kadar Classroom upload.

### 🤝 Sabah (09:00 - 12:00) — Son Hazırlık
- [ ] Basılı rapor elde mi? (eğer dün yapılmadıysa SABAH 8:00'de yazıcıdaaaaa)
- [ ] **Üç imza** raporun son sayfasında atılmış mı? ⭐⭐ ⭐ (imza yoksa rapor geçersiz!)
- [ ] Tüm dosyaların son halleri tek klasörde:
  - [ ] `Rapor_VeloGuard_TAU_INF208_Final.pdf`
  - [ ] `Demo_Video_VeloGuard.mp4`
  - [ ] `Sunum_VeloGuard.pdf`
  - [ ] `Turnitin_Raporu_VeloGuard.pdf`
  - [ ] `GitHub_Link.txt` (URL içeren basit dosya)
- [ ] GitHub son commit'ler atıldı mı? `v1.0-final` tag'i konuldu mu?
- [ ] README final hali bonus için kontrol et:
  - [ ] Proje açıklaması
  - [ ] Donanım listesi (BOM görseli)
  - [ ] Kurulum talimatları
  - [ ] Lisans (MIT)
  - [ ] CONTRIBUTING.md var mı?
  - [ ] Demo video link
  - [ ] Ekran görüntüleri / GIF

### 🤝 Öğle (13:00 - 14:30) — Son Sprint
- [ ] Hep birlikte C208'e doğru yola çık (en az 30 dk önceden)
- [ ] Yedek olarak: USB belleğe tüm dosyalar (eğer hocadan istenirse)
- [ ] **14:45 ÖNCESİ teslim** (geç kalmak felaket olur!)

### 14:45 — TESLİM ANIIIII 🎯
- [ ] Hocaya basılı rapor + sözel açıklama
- [ ] Hocanın olası soruları için **30 saniyelik tanıtım** hazır olsun:
  > "Hocam, biz bisiklet/scooter/motosiklet için akıllı hırsızlık önleme sistemi yaptık. Raspberry Pi + PREEMPT-RT üzerinde, IMU + kamera + reed switch ile çalışıyor, priority inheritance protokolünü uyguladık ve ölçtük, kamera bonusu için OpenCV motion detection ekledik. GitHub'da açık kaynak."

### 🤝 Akşam (16:00 - 23:00) — Classroom Upload
- [ ] Google Classroom'a girilen tüm dosyalar:
  - [ ] Rapor PDF
  - [ ] Video MP4
  - [ ] Sunum PDF
  - [ ] Turnitin raporu PDF
  - [ ] Kod (GitHub link, ZIP'leme isteyebilir)
- [ ] **Onay screenshot'ı** ekipte herkesle paylaş (yedek için)
- [ ] **23:00'dan ÖNCE** her şey upload edilmiş olsun

### 🌙 Gece — KUTLAMA 🎉🍕🥳
- [ ] Tamamlandı, başardınız!
- [ ] Çıkardığımız dersleri (lessons learned) kısa bir not olarak yazın — gelecekte başka projeler için altın değerinde


---
---

# 📌 EK BÖLÜMLER

## 📊 Haftalık İlerleme Özet Tablosu (Doldur)

Her sprint sonunda bu tabloyu güncelle:

| Sprint | Hedef Tamamlama | Gerçek Tamamlama | Notlar |
|---|---|---|---|
| Sprint 0 (4-8 May) | 100% | __% | |
| Sprint 1 (9-15 May) | 100% | __% | |
| Sprint 2 (16-22 May) | 100% | __% | |
| Sprint 3 (23-29 May) | 100% | __% | |
| Sprint 4 (30-2 Haz) | 100% | __% | |
| Final (3-5 Haz) | 100% | __% | |

---

## ✅ Hocanın Zorunlu Şartları — Final Kontrol Listesi

Teslimden önce (5 Haziran sabah) bu listeyi tek tek tikle:

### Zorunlu (yoksa -50 puan!)
- [ ] **En az 2 sensör entegre edildi** (✅ MPU6050, Pi Camera, Reed, DHT22 = 4)
- [ ] **En az 1 aktüatör entegre edildi** (✅ Buzzer, LED = 2-3)
- [ ] **Mantıksal karar algoritması var** (✅ FSM 5-state)
- [ ] **En az 2 modelleme yöntemi kullanıldı** (✅ StateChart + Petri + UPPAAL = 3)
- [ ] **RTOS kullanıldı** (✅ Linux + PREEMPT-RT)
- [ ] **Priority Inversion çözümü kanıtlı** (✅ PRIO_INHERIT ölçümü)
- [ ] **En az 3 değerlendirme metriği** (✅ WCET + Enerji + Termal + Pareto = 4)

### Değerlendirme Tablosu (110 puan)
- [ ] **Sensör/Aktüatör + füzyon** (40p): Kalman + adaptif eşik
- [ ] **Algoritma** (10p): FSM + adaptif öğrenme
- [ ] **Performans** (10p): CPU<%70, RAM<%80, T<80°C
- [ ] **Yapı/Dokümantasyon** (15p): Modüler kod, README, Git
- [ ] **Hata yönetimi** (10p): try/except, watchdog, ISR
- [ ] **Özgün katkı** (10p): Çok-araçlı + adaptif öğrenme
- [ ] **Ölçeklenebilirlik** (5p): MQTT + BOM
- [ ] **Planlama** (10p): Gantt + iş bölümü tablosu RAPORDA
- [ ] **Sunum & Demo** (10p): Video ≤5dk + canlı demo

### Bonus (toplam +10)
- [ ] 🎁 **GitHub açık kaynak** (+5): Public + README + LICENSE + CONTRIBUTING
- [ ] 🎁 **Kamera + görüntü işleme** (+5): OpenCV motion detection / HOG insan algılama

### Teslim Kontrolleri
- [ ] Basılı rapor (20-30 sayfa, ciltli)
- [ ] **Üç üyenin İMZASI raporda** ⚠️ Eksik = geçersiz!
- [ ] Turnitin raporu (#48947170, kayıt: TAU.INF.208)
- [ ] GitHub repo public link
- [ ] Video MP4 (≤5 dk)
- [ ] Sunum PDF (10-12 slayt)
- [ ] Tümü Google Classroom'da

---

## 🆘 Acil Durum Senaryoları & B Planı

### "Donanım gelmedi" (Sprint 1 başlangıcı)
- Mock mode'da geliştirme yap (Ü2 hazır olduğu için)
- Eldeki Pi'da basit alternatif sensör kullan (Pi'nın kendi termal sensörü vs.)
- Kargo gecikme için 2-3 günlük tampon zaten plana eklenmiş

### "PREEMPT-RT kurulamıyor"
- Önce hazır .deb dene
- Olmuyorsa kernel derle (4-6 saat)
- En kötü durumda: standart Linux + `nice` değerleri ile dene + raporda "PREEMPT-RT'a yükselteceğiz" yaz (puan kaybı küçük)

### "Pi Camera çalışmıyor"
- ESP32-CAM yedek (~150 TL, 1 gün kargo)
- Veya USB webcam (Pi'da `/dev/video0`)
- Kamera bonus +5'i kaybetmek istemiyoruz!

### "Priority Inheritance ölçümü beklenen sonucu vermiyor"
- Test parametrelerini agresifleştir (daha uzun mutex tutma süresi)
- CPU yükü artır (`stress-ng`)
- Birden fazla denemenin ortalamasını al
- En kötü durumda: literatür değerleri ile karşılaştır, kavramsal anlatım önemli

### "Bir üye hastalanıyor / sınava girecek"
- Yapılan işin status'unu **GitHub Issues** üzerinden takip et
- Pair work zaten yapılıyor olmalı, başkası devralabilir
- Kritik task'ları yedekleyerek dağıt

### "Final sabahı sistem çökerse"
- Sunumda **ön kayıtlı video** her zaman olsun (yedek)
- Demo başarısız olursa hiç ısrar etme: "Şu anda küçük bir bug var, video gösterelim"

---

## 🎓 Öğrenme Notları (Hızlı Referans)

### `cyclictest` çıktısını okuma
```
T: 0 ( 1234) P:80 I:1000 C:  60000 Min:      4 Act:    8 Avg:    7 Max:      45
```
- T: thread no
- P: priority
- I: interval (µs)
- C: counter (kaç döngü)
- Min/Act/Avg/Max: latency (µs)
- **İdeal**: Max < 100 µs (PREEMPT-RT çalışıyor demek)
- **Kötü**: Max > 1000 µs (yamada sorun var ya da CPU çok yüklü)

### Priority Inheritance C kodu
```c
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);  // ← KRİTİK
pthread_mutex_init(&mutex, &attr);
pthread_mutexattr_destroy(&attr);
```

### MPU6050 I2C testi (1 satır)
```bash
python3 -c "import smbus2; b=smbus2.SMBus(1); print('OK' if b.read_byte_data(0x68,0x75)==0x68 else 'FAIL')"
```

### Pi'da kamera testi (1 satır)
```bash
libcamera-still -o /tmp/test.jpg && echo "Camera OK" || echo "Camera FAIL"
```

### CPU sıcaklık ve frekans
```bash
vcgencmd measure_temp        # CPU sıcaklığı
vcgencmd measure_clock arm   # ARM frekansı
vcgencmd get_throttled       # 0x0 = sorun yok
```

---

## 🗂️ Dosya/Klasör Hızlı Erişim

```
veloguard/                          ← GitHub root
├── README.md                        ← bonus için kritik 🎁
├── LICENSE                          ← MIT 🎁
├── CONTRIBUTING.md                  ← bonus 🎁
├── docs/
│   ├── architecture_v2.png
│   ├── statechart_v2.png
│   ├── petrinet_v2.png
│   ├── figures/
│   │   ├── prio_inheritance_comparison.png  ← ⭐⭐⭐
│   │   ├── wcet_table.md
│   │   ├── energy_table.md
│   │   ├── thermal_model.png
│   │   └── pareto_front.png
│   └── final_report.pdf
├── hardware/
│   ├── BOM_v2.csv
│   ├── schematic_v2.png
│   ├── enclosure.stl
│   └── mounting_guide.md
├── firmware/
│   ├── src/
│   │   ├── main.py
│   │   ├── fsm.py
│   │   ├── algorithms/
│   │   │   ├── kalman.py
│   │   │   └── adaptive_threshold.py
│   │   ├── drivers/
│   │   │   ├── imu_driver.py
│   │   │   ├── camera_driver.py
│   │   │   ├── reed_driver.py
│   │   │   ├── temp_driver.py
│   │   │   ├── ina219_driver.py
│   │   │   ├── pam8403_driver.py
│   │   │   └── led_driver.py
│   │   ├── comm/
│   │   │   ├── telegram_bot.py
│   │   │   ├── web_ui.py
│   │   │   └── mqtt.py
│   │   └── rtos/
│   │       ├── hello_rt.c
│   │       ├── prio_inv_demo.c   ← ⭐⭐⭐
│   │       ├── imu_task.c
│   │       └── fsm_task.c
│   └── tests/
├── tools/
│   ├── full_sensor_test.py
│   ├── energy_logger.py
│   ├── pareto_sweep.py
│   ├── wcet_analyzer.py
│   ├── thermal_model.py
│   ├── prio_inv_plot.py
│   └── plot_style.py
└── presentation/
    ├── slides.pdf
    ├── demo_video.mp4
    └── raw/
        ├── sprint1_demo.mp4
        ├── sprint2_milestone.mp4
        └── final_demo.mp4
```

---

## 💪 Motivasyon & Hatırlatmalar

### Her sabah kendine sor:
- Bugün **bir adım** daha yaklaşacak mıyım?
- Bloker varsa **erkenden** mi paylaşacağım?
- Hocanın istediği **en az bir madde** üzerinde çalışacak mıyım?

### Her hafta sonunda kendine sor:
- Sprint hedefimin **en az %80**'ini tamamladım mı?
- Ekiple iletişim **iyi** mi?
- Ben mi yorgunum, sistem mi yorgun? (kişisel sağlık önemli!)

### Her milestone öncesi kendine sor:
- "Eğer hocaya bugün gösterseydim, **gururla** mı sunardım?"

---

## 🎯 Final Hatırlatma

Bu plan **yol haritasıdır, kutsal değildir**. Gerçeklikte:
- Bazı günler erken bitirirsin → **dinlen**, tükenme
- Bazı günler iş uzar → **gerçekleştir**, panik yapma
- Bazı maddeler iptal olur → **alternatif** üret
- Bazı yeni fikirler çıkar → **plana ekle**, ama scope creep'ten kaçın

> *"Plans are nothing; planning is everything."* — Eisenhower

**Plan kâğıt üzerinde, başarı sahaya inilince yapılır. Hadi başlayın! 🚴💨**

---

*Versiyon 1.0 — 04.05.2026*  
*Hazırlandığı tarihte ekipte 3 kişi öngörülmüştür. Bir veya iki kişi olursa yeniden ölçeklenir.*
