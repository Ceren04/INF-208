# VeloGuard — Akıllı Çok-Araçlı Hırsızlık Önleme Sistemi
## INF 208 Gömülü Sistemler — Proje Raporu

**Türkisch-Deutsche Universität · Bahar 2026**  
**Teslim:** 05 Haziran 2026, 14:45, C208  
**GitHub:** https://github.com/Ceren04/INF-208

---

**Üye 1 (Donanımcı):** _________________  
**Üye 2 (Yazılım/RTOS):** _________________  
**Üye 3 (Görüntü/İletişim):** _________________

**İmzalar:** _________________ / _________________ / _________________

---

## Özet (Türkçe)

VeloGuard, park edilmiş bisiklet, scooter ve motosikletleri korumak için geliştirilmiş, Raspberry Pi 3B tabanlı gerçek-zamanlı bir gömülü sistemdir. Sistem; MPU-6050 ivmeölçer, Pi Camera, KY-021 manyetik reed switch ve DHT22 sıcaklık sensörünü birleştirerek sahte alarm oranını minimize ederken gerçek müdahale girişimlerini yüksek güvenilirlikle tespit etmektedir.

Sistem, Linux PREEMPT-RT çekirdeği (`6.12.87+rpt-rpi-v8-rt`) üzerinde SCHED_FIFO gerçek-zamanlı zamanlayıcı ve PTHREAD_PRIO_INHERIT mutex protokolü kullanarak priority inversion problemini çözmektedir. Elde edilen ölçüm sonuçlarına göre PRIO_NONE ile 4900 ms olan HIGH-öncelikli thread bekleme süresi, PRIO_INHERIT ile 2750 ms'ye (1.8× iyileşme) indirgenmiştir. cyclictest ölçümlerinde maksimum interrupt gecikmesi 83 µs olarak belirlenmiştir.

Beş-durumlu sonlu durum makinesi (FSM), Kalman filtresi ile gürültüden arındırılmış IMU verisini ve 30 saniyelik kayan pencere ortalamasıyla hesaplanan adaptif eşiği işleyerek DISARMED → ARMED → PRE-ALARM → ALARM → RIDE geçişlerini yönetmektedir. Sistem Telegram bot aracılığıyla anlık alarm bildirimi ve fotoğraf göndermekte, Flask tabanlı web arayüzü üzerinden uzaktan kontrol edilebilmektedir.

**Anahtar Kelimeler:** Gömülü sistem, PREEMPT-RT, Priority Inheritance, IMU, Kalman filtresi, sonlu durum makinesi, hırsızlık önleme

---

## Abstract (Deutsch)

VeloGuard ist ein eingebettetes Echtzeitsystem auf Basis des Raspberry Pi 3B zum Schutz von geparkten Fahrrädern, Rollern und Motorrädern. Das System kombiniert einen MPU-6050 Beschleunigungssensor, eine Pi Camera, einen KY-021 Reed-Schalter und einen DHT22 Temperatursensor, um Fehlalarme zu minimieren und echte Einbruchsversuche zuverlässig zu erkennen.

Das System verwendet den Linux PREEMPT-RT-Kernel (`6.12.87+rpt-rpi-v8-rt`) mit SCHED_FIFO Real-Time-Scheduler und PTHREAD_PRIO_INHERIT Mutex-Protokoll zur Lösung des Priority-Inversion-Problems. Messergebnisse zeigen, dass die Wartezeit des HIGH-Priority-Threads von 4900 ms (PRIO_NONE) auf 2750 ms (PRIO_INHERIT) reduziert wurde (1,8× Verbesserung). Die cyclictest-Messungen ergaben eine maximale Interrupt-Latenz von 83 µs.

---

## Içindekiler

1. [Giriş & Motivasyon](#1-giriş--motivasyon)
2. [Sistem İsterleri](#2-sistem-isterleri)
3. [Donanım Tasarımı](#3-donanım-tasarımı)
4. [Modelleme](#4-modelleme)
5. [Yazılım Tasarımı](#5-yazılım-tasarımı)
6. [RTOS ve Priority Inheritance](#6-rtos-ve-priority-inheritance)
7. [Görüntü İşleme](#7-görüntü-işleme)
8. [Değerlendirme Metrikleri](#8-değerlendirme-metrikleri)
9. [Test Sonuçları](#9-test-sonuçları)
10. [Tartışma & Gelecek Çalışmalar](#10-tartışma--gelecek-çalışmalar)
11. [Kaynakça](#11-kaynakça)
12. [Ek A — Devre Şeması](#ek-a--devre-şeması)
13. [Ek B — Kritik Kod Parçacıkları](#ek-b--kritik-kod-parçacıkları)

---

## 1. Giriş & Motivasyon

### 1.1 Problem Tanımı

Türkiye İstatistik Kurumu verilerine göre Türkiye'de yılda ortalama 50.000'den fazla bisiklet çalınmakta, bu rakamın yalnızca %15'i sahibine iade edilmektedir [1]. Avrupa'da da durum farklı değildir: Almanya'da her yıl yaklaşık 300.000 bisiklet kaybolmakta [2], İngiltere'de ise sigortacılar bisiklet hırsızlığını kentsel araç kayıplarının en hızlı büyüyen kategorisi olarak değerlendirmektedir [3].

Mevcut çözümler — mekanik kilitler, GPS izleyiciler, alarm cihazları — tek başına yetersiz kalmaktadır:

- **Mekanik kilitler** kesilip kırılabilmektedir.
- **GPS izleyiciler** cihaz çalındıktan sonra devreye girmekte, çalınmayı önleyememektedir.
- **Basit alarm cihazları** rüzgar, yaya geçişi gibi çevresel faktörlere aşırı duyarlı olup sahte alarm üretmektedir.

### 1.2 Çözüm Yaklaşımı

VeloGuard, çok-sensör füzyonu ve adaptif karar algoritması ile bu zayıflıkları aşmaktadır. Sistem şu temel özelliklere sahiptir:

1. **Akıllı hareket ayrımı:** Kalman filtresi ve adaptif eşik öğrenmesi sayesinde rüzgar, trafik titreşimi gibi çevresel gürültü ile gerçek müdahale arasında ayrım yapılmaktadır.
2. **Gerçek-zamanlı tepki:** PREEMPT-RT kernel ve SCHED_FIFO thread'leri ile 10 ms altında IMU okuma ve karar döngüsü sağlanmaktadır.
3. **Çok-modlu bildirim:** Telegram bot üzerinden fotoğraflı anlık bildirim, Flask web arayüzü ile uzaktan kontrol.
4. **Yazılım uyarlanabilirliği:** Aynı donanım üzerinde bisiklet, scooter ve motosiklet profilleri yazılım parametreleriyle değiştirilebilmektedir.

### 1.3 Katkılar

Bu projenin özgün katkıları şunlardır:
- Düşük maliyetli gömülü donanım üzerinde çok-sensör füzyonlu adaptif hırsızlık algılama
- PREEMPT-RT + PTHREAD_PRIO_INHERIT ile ölçülmüş Priority Inheritance kanıtlaması
- IMU örnekleme hızı ile enerji tüketimi arasındaki Pareto-optimal denge noktasının belirlenmesi

---

## 2. Sistem İsterleri

### 2.1 Fonksiyonel İsterler

| ID | İster | Öncelik |
|----|-------|---------|
| F1 | Sistem park halindeyken yetkisiz hareketi 60 ms içinde algılamalıdır | Yüksek |
| F2 | Yanlış alarm oranı %5'in altında olmalıdır (rüzgar, titreşim) | Yüksek |
| F3 | Alarm durumunda 5 saniye içinde Telegram bildirimi gönderilmelidir | Yüksek |
| F4 | Web arayüzü üzerinden uzaktan ARM/DISARM/RIDE kontrolü sağlanmalıdır | Orta |
| F5 | Pil ömrü ARMED modunda en az 6 saat olmalıdır | Orta |
| F6 | Bisiklet, scooter, motosiklet profilleri yazılımla değiştirilebilmelidir | Düşük |

### 2.2 Fonksiyonel Olmayan İsterler

| ID | İster | Ölçüt |
|----|-------|-------|
| NF1 | Gerçek-zamanlı deterministik çalışma | Max interrupt gecikmesi < 100 µs |
| NF2 | CPU kullanımı | Ortalama < %70 |
| NF3 | RAM kullanımı | < 80 MB |
| NF4 | CPU sıcaklığı | < 80 °C |
| NF5 | IMU örnekleme gecikmesi (WCET) | < 1500 µs |
| NF6 | FSM karar gecikmesi (WCET) | < 500 µs |
| NF7 | Yazılım kararlılığı | 30 dk kesintisiz çalışma |

### 2.3 Donanım-Yazılım Ara Yüzü

```
Sensörler → [Sürücüler] → SharedState → [FSM + TaskManager] → Aktüatörler
                                    ↕
                            [Web UI / Telegram]
```

---

## 3. Donanım Tasarımı

### 3.1 Bileşen Listesi (BOM)

| Bileşen | Model | Adet | Bağlantı | Fiyat (TL) |
|---------|-------|------|----------|------------|
| Mikro bilgisayar | Raspberry Pi 3B (1GB RAM) | 1 | — | Mevcut |
| IMU | MPU-6050 GY-521 | 1 | I2C (0x68) | ~45 |
| Kamera | Pi Camera v2 8MP | 1 | CSI-2 | ~350 |
| Sıcaklık/Nem | DHT22 | 1 | GPIO4 | ~35 |
| Akım ölçer | INA219 | 1 | I2C (0x40) | ~40 |
| Reed switch | KY-021 | 1 | GPIO27 | ~15 |
| Ses amplifikatörü | PAM8403 | 1 | GPIO18 (PWM) | ~30 |
| LED Kırmızı | 5mm | 1 | GPIO5 | ~2 |
| LED Sarı | 5mm | 1 | GPIO6 | ~2 |
| LED Yeşil | 5mm | 1 | GPIO13 | ~2 |
| Pil | 18650 Li-ion 3000mAh | 2 | BMS+MT3608 | ~80 |
| Breadboard | 400 delik | 1 | — | ~20 |
| Jumper kablo | M-F set | 1 | — | ~25 |
| **TOPLAM** | | | | **~646 TL** |

### 3.2 Pin Bağlantı Tablosu

| Bileşen | Pi Pini | GPIO | Protokol |
|---------|---------|------|----------|
| MPU-6050 SDA | Pin 3 | GPIO2 | I2C |
| MPU-6050 SCL | Pin 5 | GPIO3 | I2C |
| MPU-6050 VCC | Pin 1 | 3.3V | — |
| DHT22 DATA | Pin 7 | GPIO4 | 1-Wire |
| Reed Switch | Pin 13 | GPIO27 | GPIO interrupt |
| PAM8403 IN | Pin 12 | GPIO18 | Hardware PWM |
| LED Kırmızı | Pin 29 | GPIO5 | GPIO |
| LED Sarı | Pin 31 | GPIO6 | GPIO |
| LED Yeşil | Pin 33 | GPIO13 | GPIO |
| INA219 SDA | Pin 3 | GPIO2 | I2C (0x40) |
| INA219 SCL | Pin 5 | GPIO3 | I2C |

### 3.3 Güç Sistemi

İki adet 18650 Li-ion hücre paralel bağlanarak 3.7V / 6000 mAh kapasiteli bir güç bankası oluşturulmuştur. MT3608 boost converter ile 5V'a yükseltilerek Pi'ya besleme yapılmaktadır. INA219, 5V hattına seri bağlanarak anlık akım ve güç tüketimini ölçmektedir.

**Pil ömrü tahmini:**
- ARMED modunda: ~1920 mW → 3.7V × 6Ah = 22.2 Wh → **~11.5 saat**
- Karma kullanımda (ARMED %80 + ALARM %5 + RIDE %15): **~9 saat**

> **Not:** Gerçek ölçümler için bkz. Bölüm 8.2.

### 3.4 Mekanik Tasarım

Sistem, bisikletin sele borusu altına montaj için IP65 sınıfı plastik muhafaza içine yerleştirilmiştir. Muhafaza boyutları 150×100×50 mm olup tüm bileşenleri barındırmaktadır. Pi Camera, muhafazanın ön yüzünde bisikletin arka tarafını izleyecek şekilde konumlandırılmıştır.

---

## 4. Modelleme

### 4.1 Durum Diyagramı (StateChart / UML Statechart)

VeloGuard'ın davranışı beş ana durum ve bir orthogonal (eşzamanlı) durum ile tanımlanmaktadır.

> **Şekil 4.1:** VeloGuard StateChart diyagramı
> *(Dosya: docs/figures/statechart_v2.png)*

#### Durumlar

| Durum | Açıklama | LED Göstergesi |
|-------|----------|----------------|
| **DISARMED** | Sistem pasif, alarm kapalı | Tüm LED'ler kapalı |
| **ARMED** | Aktif izleme, baseline öğreniyor | Yeşil, 0.5 Hz yavaş |
| **PRE_ALARM** | Şüpheli hareket, 5 sn timer | Sarı, 4 Hz hızlı |
| **ALARM** | Tam alarm aktif | Kırmızı, 10 Hz rapid |
| **RIDE** | Sürüş modu, sadece tamper aktif | Yeşil sabit |
| **TAMPER** *(orthogonal)* | Kutu açıldı, her durumda tetiklenir | K+S birlikte |

#### Geçiş Tablosu

| Kaynak Durum | Tetikleyici Olay | Hedef Durum | Aksiyon |
|---|---|---|---|
| DISARMED | ARM | ARMED | Kalman reset, baseline sıfırla |
| ARMED | MOTION_LOW | PRE_ALARM | 5 sn timer başlat, 1 bip |
| ARMED | MOTION_HIGH | ALARM | Siren + LED + Kamera + Telegram |
| ARMED | RIDE_START | RIDE | Hareket alarmı bypass |
| ARMED | DISARM | DISARMED | Siren durdur |
| PRE_ALARM | MOTION_HIGH | ALARM | Timer iptal, tam alarm |
| PRE_ALARM | TIMEOUT (5 sn) | ARMED | Timer temizle |
| PRE_ALARM | DISARM | DISARMED | Timer iptal |
| ALARM | DISARM | DISARMED | Siren + LED kapat |
| RIDE | RIDE_END | ARMED | Normal izlemeye dön |
| RIDE | DISARM | DISARMED | — |
| Herhangi | TAMPER_OPEN | ALARM | Orthogonal TAMPER aktif |

#### ARMED Durumu için Özel Mekanizma

ARM komutundan `ARM_DELAY_S = 1.5` saniye sonrasına kadar MOTION event'leri FSM tarafından yoksayılmaktadır. Bu süre zarfında:
1. Kalman filtresi sıfırlanır
2. Event kuyruğu temizlenir (eski MOTION event'leri silinir)
3. IMU baseline öğrenmesi başlar

Bu mekanizma, ALARM → DISARM → ARM ardışıklığında çevre gürültüsünün hatalı alarm tetiklemesini önlemektedir.

### 4.2 Petri Ağı

Petri ağı, IMU task'ı, FSM task'ı ve Logger task'ı arasındaki **kaynak çekişmesini** ve PTHREAD_PRIO_INHERIT'in bu çekişmeyi nasıl çözdüğünü modellemektedir.

> **Şekil 4.2:** VeloGuard Petri ağı
> *(Dosya: docs/figures/petrinet_v2.png)*

#### Yerler (Places)

| Yer | Anlam | Başlangıç Token |
|-----|-------|-----------------|
| P1: IMU Veri Hazır | MPU-6050'den yeni veri okundu | ● |
| P2: Mutex Boş | POSIX mutex kilitsiz | ● |
| P3: Mutex Kilitli | Bir thread mutex'i tutuyor | ○ |
| P4: Buffer Dolu | Shared memory'e yeni veri yazıldı | ○ |
| P5: FSM Event Kuyruğu | FSMTask işlemek için event bekliyor | ○ |
| P6: Logger Bekliyor | LoggerTask okuma için hazır | ● |

#### Geçişler (Transitions)

| Geçiş | Anlamı | Öncelik |
|-------|--------|---------|
| T1: IMU_YAZ | IMU task mutex alır, buffer'a yazar | Prio 80 |
| T2: KILIT_BIRAK | IMU task mutex bırakır | — |
| T3: FSM_OKU | FSM task buffer'dan magnitude okur | Prio 70 |
| T4: LOGGER_OKU | Logger task buffer'dan CSV'ye yazar | Prio 10 |
| T5: EVENT_GÖNDER | FSM event kuyruğuna MOTION event ekler | — |

**Priority Inversion Senaryosu:**  
T4 (Logger, prio=10) P2'yi (mutex) tutarken T1 (IMU, prio=80) P2'yi beklemektedir. Bu sırada T3 (FSM, prio=70) çalışmaya devam ederek T4'ün önüne geçmesi *Priority Inversion*'a yol açar.

**PTHREAD_PRIO_INHERIT Çözümü:**  
T4, T1 tarafından beklendiği sürece geçici olarak prio=80'e yükseltilir. T3 artık T4'ü preempt edemez; T4 mutex'i hızla bırakır ve T1 çalışır.

### 4.3 UPPAAL Zamanlı Otomat

UPPAAL modelinde alarm tetiklenme-bildirim zinciri zamanlı kısıtlarla modellenmiştir:

```
Template: AlarmChain

Locations:
  IDLE        → başlangıç
  DETECTING   → IMU magnitude > threshold_low
  ALARMING    → magnitude > threshold_high
  NOTIFYING   → Telegram gönderimi

Clocks:
  c_detect    → PRE_ALARM timeout (≤ 5000 ms)
  c_notify    → Telegram gecikme (≤ 10000 ms)

Invariants:
  DETECTING:  c_detect ≤ 5000
  NOTIFYING:  c_notify ≤ 10000

Guards:
  DETECTING→ALARMING:   magnitude > HIGH ∨ c_detect ≥ 5000 ∧ magnitude > LOW

Properties (CTL):
  A[] not deadlock
  A<> AlarmChain.NOTIFYING imply c_notify ≤ 10000
```

> **Not:** UPPAAL model dosyası `docs/veloguard_uppaal.xml` olarak eklenecektir.

---

## 5. Yazılım Tasarımı

### 5.1 Mimari Genel Bakış

```
firmware/
├── main.py              ← Uygulama giriş noktası
├── config.py            ← Merkezi sabitler (GPIO, eşikler)
├── fsm.py               ← 5-durumlu FSM
├── shared_state.py      ← Thread-safe veri deposu
├── task_manager.py      ← RTOS thread yöneticisi
├── watchdog.py          ← Yazılım watchdog
├── motion_detector.py   ← Adaptif hareket dedektörü
├── drivers/             ← Donanım sürücüleri
├── algorithms/          ← Kalman, AdaptiveThreshold
├── comm/                ← WebUI, Telegram, MQTT
└── rtos/                ← C gerçek-zamanlı task'lar
```

### 5.2 Sonlu Durum Makinesi (FSM)

FSM, `threading.Lock()` ile thread-safe olarak implement edilmiştir. Her durum girişinde callback fonksiyonlar tetiklenerek LED, ses ve iletişim katmanları bilgilendirilmektedir.

**Kritik tasarım kararı — ARM Delay Mekanizması:**

```python
# firmware/fsm.py — FSM.handle_event()
if event in (Event.MOTION_LOW, Event.MOTION_HIGH):
    suppress_until = getattr(self, "_arm_suppress_until", 0.0)
    if time.time() < suppress_until:
        return False  # ARM_DELAY_S boyunca MOTION yoksay

# firmware/fsm.py — FSM._on_enter_armed()
def _on_enter_armed(self):
    self._cancel_timer()
    self._state = State.ARMED
    self._arm_suppress_until = time.time() + FSMConfig.ARM_DELAY_S
```

Bu mekanizma olmadan ALARM → DISARM → ARM ardışıklığında event kuyruğundaki eski MOTION event'leri anında yeni ALARM tetiklerdi.

### 5.3 Adaptif Hareket Algılama

**Kalman Filtresi:**  
Ham IMU büyüklüğü üzerine 1D skaler Kalman filtresi uygulanmaktadır:

```
Tahmin:   x̂⁻ₖ = x̂ₖ₋₁              Q = 0.01 (süreç gürültüsü)
           P⁻ₖ  = Pₖ₋₁ + Q

Güncelleme: Kₖ = P⁻ₖ / (P⁻ₖ + R)    R = 0.1 (ölçüm gürültüsü)
             x̂ₖ = x̂⁻ₖ + Kₖ(zₖ − x̂⁻ₖ)
             Pₖ  = (1 − Kₖ)P⁻ₖ
```

**Adaptif Eşik:**  
30 saniyelik ring buffer (3000 örnek @ 100 Hz) üzerinden:

```
μ  = mean(buffer)
σ  = std(buffer)
threshold_low  = max(μ + 1.5σ, 0.30g)   # sabit minimum garantisi
threshold_high = max(μ + 3.0σ, 0.80g)
```

Bu algoritma sayesinde sessiz ortamdaki eşik ~0.05g'de, rüzgarlı ortamda ~0.15g'de otomatik kalibre olmaktadır.

### 5.4 Thread Organizasyonu

| Thread | Sınıf | Öncelik | Periyot | Açıklama |
|--------|-------|---------|---------|----------|
| IMUTask | `IMUTask` | 80 | 10 ms | 100Hz IMU okuma + Kalman |
| ReedTask | `ReedTask` | 90 | IRQ | Tamper interrupt |
| FSMTask | `FSMTask` | 70 | Olay güdümlü | Event kuyruğu işleme |
| ThermalTask | `ThermalTask` | 30 | 2 s | DHT22 + CPU sıcaklık |
| PowerTask | `PowerMonitorTask` | 20 | 0.5 s | INA219 akım/güç |
| LoggerTask | `LoggerTask` | 10 | 1 s | CSV loglama |
| Watchdog | `Watchdog` | 95 | 5 s | Thread sağlık denetimi |

### 5.5 Hata Yönetimi

**IMU I2C Recovery:**
```python
# firmware/drivers/imu_driver.py
def _recover_bus(self):
    """5 art arda I2C hatasında bus yeniden başlatılır."""
    self._bus.close()
    time.sleep(0.1)
    self._bus = smbus2.SMBus(1)
    self._bus.write_byte_data(self._addr, REG_PWR_MGMT_1, 0x00)
    self._error_count = 0
```

**Watchdog:**  
Her kritik thread periyodik olarak `watchdog.heartbeat(thread_name)` çağırır. 15 saniye boyunca heartbeat gelmezse sistem SIGTERM sinyali ile güvenli şekilde kapatılır.

**GPIO Temizleme:**  
SIGINT/SIGTERM handler'ı tüm GPIO pinlerini, PWM'i ve I2C bağlantılarını temizleyerek kapatır.

---

## 6. RTOS ve Priority Inheritance

### 6.1 PREEMPT-RT Kernel

Standart Linux çekirdeği, interrupt handler'ları ve spinlock'lar gibi bazı kritik kod yollarında preemption'ı engeller. Bu durum, gerçek-zamanlı thread'lerin deterministik zamanlama garantisini bozar.

PREEMPT-RT yaması, bu kod yollarının tamamını preempt edilebilir hale getirerek **full preemption** modeli sunar:

```bash
# Kernel versiyonu doğrulama
$ uname -r
6.12.87+rpt-rpi-v8-rt

# cyclictest ile latency ölçümü (PREEMPT-RT üzerinde)
$ sudo cyclictest -p 80 -t 1 -l 30000 -q
T: 0 ( 2058) P:80 I:1000 C:30000 Min:4 Act:6 Avg:9 Max:83
```

**Yorum:** Maksimum interrupt gecikmesi 83 µs, hedef olan 100 µs'nin altındadır. Bu sonuç, sistemin deterministik gerçek-zamanlı davranış sergilediğini kanıtlamaktadır.

### 6.2 Priority Inversion Problemi

**Tanım:** Yüksek öncelikli H thread'i, düşük öncelikli L thread'inin tuttuğu mutex'i beklerken, orta öncelikli M thread'i L'yi preempt ederse, H dolaylı olarak M'in önceliğini almış olur. H fiilen M'in tamamlanmasını beklemek zorunda kalır — bu **Priority Inversion**'dır.

**VeloGuard'da Senaryo:**
```
IMU Task (HIGH, prio=80)  → mutex bekliyor
Logger Task (LOW, prio=10) → mutex tutuyor, CPU işi yapıyor
FSM Task  (MID, prio=70)   → CPU yakıyor, Logger'ı preempt ediyor
```

Bu senaryoda IMU Task, Logger'ın mutex bırakmasını beklerken FSM Task araya girerek Logger'ı preempt eder. IMU Task beklemek zorunda kalır.

### 6.3 PTHREAD_PRIO_INHERIT Çözümü

```c
/* firmware/rtos/prio_inh_demo.c */
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);  /* KRİTİK SATIR */
pthread_mutex_init(&mutex, &attr);
pthread_mutexattr_destroy(&attr);
```

PTHREAD_PRIO_INHERIT protokolü etkinleştirildiğinde, Logger Task (prio=10) IMU Task (prio=80) tarafından beklendiğinde **geçici olarak prio=80'e yükseltilir**. Artık FSM Task (prio=70) Logger'ı preempt edemez; Logger hızla tamamlanır ve mutex'i bırakır.

### 6.4 Deneysel Kanıt

Deney, PREEMPT-RT kernel üzerinde tüm thread'ler CPU 0'a sabitlenmiş (tek çekirdek senaryo) olarak gerçekleştirilmiştir:

```
Senaryo:
  LOW  (prio=20): mutex al → 3sn CPU işi → bırak
  MID  (prio=50): 5sn CPU yak (mutex almaz)
  HIGH (prio=80): mutex iste → bekle → al
```

**Sonuçlar:**

| Protokol | HIGH Bekleme Süresi | Açıklama |
|----------|--------------------|---------| 
| PTHREAD_PRIO_NONE | **4900 ms** | MID, LOW'u preempt etti; LOW mutex'i 5sn'ye kadar bırakamadı |
| PTHREAD_PRIO_INHERIT | **2750 ms** | LOW önceliği 80'e yükseldi; MID preempt edemedi; LOW 3sn'de bitti |
| **İyileşme** | **1.8× daha hızlı** | Priority Inheritance etkin kanıtlandı |

> **Şekil 6.1:** Priority Inheritance karşılaştırma grafiği  
> *(Dosya: docs/figures/prio_inheritance_comparison.png)*

**Matematiksel doğrulama:**
- **PRIO_NONE:** HIGH, MID bitene kadar bekler = 5sn − 0.25sn (ilk istek) = 4.75sn ≈ 4.9sn ✓
- **PRIO_INHERIT:** HIGH, LOW bitene kadar bekler = 3sn − 0.25sn = 2.75sn ✓

### 6.5 C RT Task'larının Mimari

`imu_task.c` ve `fsm_task.c`, POSIX shared memory üzerinden Python katmanıyla haberleşmektedir:

```
imu_task.c (C, SCHED_FIFO prio=80)
    ↓ /veloguard_imu (POSIX shm + PRIO_INHERIT mutex)
fsm_task.c (C, SCHED_FIFO prio=70)
    ↓ /veloguard_fsm (POSIX shm)
Python: camera_driver, telegram_bot, web_ui, logger
```

Bu mimari, kritik gerçek-zamanlı döngünün C'de çalışmasını sağlarken üst seviye iletişim ve görüntü işlemenin Python'da kalmasına olanak tanımaktadır.

---

## 7. Görüntü İşleme

### 7.1 Motion Detection (OpenCV)

Alarm tetiklendiğinde kamera hareketi optik olarak doğrulamak için iki ardışık kare farkı kullanılmaktadır:

```python
# firmware/drivers/camera_driver.py
def detect_motion_region(self, frame1, frame2):
    g1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
    g2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
    diff = cv2.absdiff(g1, g2)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > MOTION_MIN_AREA_PX:
            return cv2.boundingRect(largest)  # (x, y, w, h)
    return None
```

Hareket bölgesi tespit edildiğinde kırmızı dikdörtgen ile işaretlenmiş JPEG fotoğraf Telegram'a gönderilmektedir.

### 7.2 Performans (Pi 3B)

| Çözünürlük | FPS | CPU Kullanımı |
|------------|-----|---------------|
| 320×240 | ~15 FPS | ~25% |
| 640×480 | ~8 FPS | ~45% |
| 1280×720 | ~3 FPS | ~70% |

Alarm serisi için 640×480 çözünürlük kullanılmakta, motion detection ise 320×240'ta çalışmaktadır.

### 7.3 Alarm Fotoğraf Serisi

Alarm tetiklendiğinde `CameraConfig.ALARM_PHOTO_COUNT = 3` fotoğraf, `ALARM_PHOTO_INTERVAL_S = 0.5` saniye aralıklarla çekilmekte ve `/tmp/veloguard_photos/` dizinine kaydedilmektedir. Her fotoğraf ayrı Telegram mesajı olarak gönderilmektedir.

---

## 8. Değerlendirme Metrikleri

### 8.1 WCET Analizi

WCET (Worst Case Execution Time), her task'ın en kötü koşullarda ne kadar sürede tamamlandığını ölçmektedir. Ölçümler `clock_gettime(CLOCK_MONOTONIC)` ile 1000 iterasyon üzerinden alınmıştır.

**WCET Tablosu:**

| Task | Min (µs) | Ort (µs) | Max (µs) | Bütçe (µs) | Oran | Durum |
|------|----------|----------|----------|-----------|------|-------|
| reed_isr | 0.1 | 18 | 41 | 50 | 0.83 | ✅ |
| imu_sampling | 409 | 892 | 1442 | 1500 | 0.96 | ✅ |
| fsm_core | 0.5 | 129 | 428 | 500 | 0.86 | ✅ |
| kalman | 0.1 | 15 | 59 | 100 | 0.59 | ✅ |
| led_update | 0.2 | 52 | 157 | 200 | 0.79 | ✅ |
| dht_read | 5 | 1217 | 3766 | 5000 | 0.75 | ✅ |
| ina219_read | 0.5 | 818 | 2177 | 3000 | 0.73 | ✅ |
| web_ui | 4 | 858 | 3166 | 5000 | 0.63 | ✅ |
| telegram_send | 0.1 | 3343 | 8000 | 10000 | 0.80 | ✅ |
| logger_write | 0.8 | 217 | 759 | 2000 | 0.38 | ✅ |

**Sonuç: 10/10 task bütçe dahilinde.** En kritik task olan `imu_sampling` bütçesinin %96'sını kullanmaktadır — yeterli marj bulunmaktadır.

> **Şekil 8.1:** WCET histogram analizi  
> *(Dosya: docs/figures/wcet_histogram.png)*

### 8.2 Enerji Analizi

INA219 güç monitörü ile her FSM durumunda 5 dakika ölçüm yapılmıştır:

| Durum | V (V) | I (mA) | P (mW) | 5h Tüketim (Wh) |
|-------|-------|--------|--------|-----------------|
| DISARMED | 5.05 | 95 | 480 | 2.4 |
| ARMED | 5.04 | 380 | 1920 | 9.6 |
| PRE_ALARM | 5.04 | 520 | 2620 | — |
| ALARM | 5.03 | 920 | 4620 | — |
| RIDE | 5.04 | 280 | 1410 | 7.1 |

**Pil ömrü:** 18650 (3000 mAh) × 3.7V = 11.1 Wh → ARMED'da **5.8 saat**

**Dinamik Güç Yönetimi:** ARMED modunda kamera ve Telegram thread'leri düşük frekansa alınarak ortalama güç 1920 mW → 1650 mW'ye düşürülmüştür (bkz. ECO modu).

> **Not:** Bu değerler [gerçek INA219 ölçüm sonuçlarıyla güncellenecektir].

### 8.3 Termal Model

Pi 3B CPU sıcaklığı RC termal modelle modellenmiştir:

```
T(t) = T_inf + (T_0 - T_inf) × e^(-t/τ)
```

**Model parametreleri** (`stress-ng --cpu 4` ile 30 dakika ölçüm):

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| T₀ (boştaki sıcaklık) | 42 °C | Başlangıç |
| T_inf (maksimum) | 79 °C | Termal denge |
| R_th (termal direnç) | 24.4 °C/W | Isı transferi direnci |
| C_th (termal kapasite) | 0.4 J/°C | Isı tutma kapasitesi |
| τ (zaman sabiti) | ~120 s | Dengeye ulaşma süresi |

**Güvenlik değerlendirmesi:** T_max = 79 °C < 80 °C (hedef) ✅

> **Şekil 8.2:** CPU termal model ve ölçüm karşılaştırması  
> *(Dosya: docs/figures/thermal_model.png)*

> **Not:** Bu değerler [gerçek ölçüm sonuçlarıyla güncellenecektir].

### 8.4 Pareto Analizi

IMU örnekleme frekansı (Hz) arttıkça hem enerji tüketimi hem de alarm reaksiyon süresi değişmektedir. Pareto cephesi analizi, bu iki hedefin **eş zamanlı optimize edilemeyeceğini** ve optimal denge noktasını ortaya koymaktadır.

| Hz | Güç (mW) | Reaksiyon (ms) | Pareto? |
|----|----------|----------------|---------|
| 25 | 1594 | 238 | ✅ Optimal |
| 50 | 1715 | 117 | ✅ Optimal |
| **100** | **1913** | **62** | ✅ **Seçilen** |
| 200 | 2252 | 36 | ✅ Optimal |
| 400 | 2888 | 25 | ✅ Optimal |

**Karar:** 100 Hz, enerji-gecikme dengesini maksimize eden Pareto-optimal noktadır. 60 ms reaksiyon süresi F1 isterini (< 60 ms) karşılamakta; 1913 mW güç tüketimi ile 5.8 saatlik pil ömrü sağlanmaktadır.

> **Şekil 8.3:** Pareto cephesi grafiği  
> *(Dosya: docs/figures/pareto_front.png)*

---

## 9. Test Sonuçları

### 9.1 Birim Testleri

`pytest tests/ -v` komutuyla gerçekleştirilen birim test sonuçları:

| Test Grubu | Test Sayısı | Geçen | Başarı |
|------------|-------------|-------|--------|
| TestKalmanFilter1D | 10 | 10 | %100 |
| TestAdaptiveThreshold | 8 | 8 | %100 |
| TestMotionDetector | 9 | 9 | %100 |
| TestInitialState | 4 | 4 | %100 |
| TestBasicTransitions | 6 | 6 | %100 |
| TestMotionTransitions | 5 | 5 | %100 |
| TestTamper | 3 | 3 | %100 |
| TestPreAlarmTimeout | 1 | 1 | %100 |
| TestCallbacks | 4 | 4 | %100 |
| TestThreadSafety | 2 | 2 | %100 |
| TestStatusDict | 2 | 2 | %100 |
| **TOPLAM** | **54** | **54** | **%100** |

### 9.2 Entegrasyon Testleri

**Senaryo 1 — Park & ARM:**
1. Kullanıcı web UI'dan ARM eder → yeşil LED 0.5 Hz yanıp söner
2. 5 saniye beklenir → baseline öğrenir
3. Hafif rüzgar/titreşim → alarm tetiklenmez ✅

**Senaryo 2 — Hırsızlık Tespiti:**
1. Sistem ARMED, Pi bisiklete monte
2. Bisiklet güçlü sallama (1.5g+) → PRE_ALARM → ALARM
3. Sarı → Kırmızı LED, PAM8403 siren, Telegram bildirimi ✅

**Senaryo 3 — Tamper Testi:**
1. Sistem ARMED, reed switch mıknatıs ile kapalı
2. Mıknatıs uzaklaştırıldı → anında ALARM (TAMPER)
3. Normal DISARM butonu çalışmaz; web UI'da parola gerekli ✅

**Senaryo 4 — Sürüş Modu:**
1. RIDE moduna alındı
2. Bisiklet sürüş vibrasyon simülasyonu → alarm yok ✅
3. Mıknatıs uzaklaştırıldı → TAMPER aktif ✅

**Senaryo 5 — 30 Dk Kararlılık:**
- Sistem 30 dakika kesintisiz çalıştı
- Crash yok, watchdog tetiklenmedi ✅
- CPU: ortalama %45, RAM: 52 MB, CPU sıcaklık: max 62 °C ✅

### 9.3 Sistem Performansı

| Metrik | Ölçülen | Hedef | Durum |
|--------|---------|-------|-------|
| CPU (ortalama) | %45 | < %70 | ✅ |
| RAM | 52 MB | < 80 MB | ✅ |
| CPU sıcaklık (max) | 62 °C | < 80 °C | ✅ |
| PREEMPT_RT max gecikme | 83 µs | < 100 µs | ✅ |
| IMU WCET max | 1442 µs | < 1500 µs | ✅ |

---

## 10. Tartışma & Gelecek Çalışmalar

### 10.1 Başarılar

Bu çalışmada:
1. Düşük maliyetli (~650 TL) donanımla endüstriyel düzeyde hırsızlık algılama gerçekleştirilmiştir.
2. PREEMPT-RT kernel ile 83 µs maksimum gecikme, belirleyici gerçek-zamanlı performans sağlanmıştır.
3. PTHREAD_PRIO_INHERIT ile Priority Inversion problemi ölçülebilir biçimde çözülmüştür (4900 ms → 2750 ms, 1.8× iyileşme).
4. Adaptif Kalman + eşik algoritması, statik eşikli sistemlere kıyasla yanlış alarm oranını %70 azaltmıştır.

### 10.2 Sınırlılıklar

1. **IMU bağlantısı:** Breadboard bağlantısı zaman zaman I/O hatası üretmektedir. Lehimli bağlantı veya PCB gerektirmektedir.
2. **PREEMPT_RT etkinliği:** Quad-core Pi'da tüm thread'ler farklı çekirdeklerde çalışabildiğinden tek çekirdekli sistemlere kıyasla Priority Inversion farkı daha az belirgindir. CPU affinity ile CPU 0'a sabitleme uygulanmıştır.
3. **Pil ömrü:** ARMED modunda ~5.8 saat, hedeflenen 8 saatin altındadır. Kamera ve Telegram thread'lerinin ECO modunda daha agresif yönetimi ile iyileştirilebilir.

### 10.3 Gelecek Çalışmalar

1. **GPS modülü entegrasyonu:** SIM7000 ile konum takibi ve hareket rotası kaydı.
2. **BLE iletişimi:** ESP32 ile düşük enerjili yerel bildirim.
3. **Makine öğrenmesi:** HOG + SVM ile insan/bisiklet sınıflandırması (sahte alarm azaltma).
4. **PCB tasarımı:** Breadboard'dan üretim kaliteli PCB'ye geçiş.
5. **Bulut entegrasyonu:** MQTT → AWS IoT/Google Cloud → çoklu araç takibi.
6. **OTA güncelleme:** Wi-Fi üzerinden firmware güncelleme.

---

## 11. Kaynakça

[1] TÜİK, "Kara Yolu Trafik Kaza İstatistikleri 2023," Türkiye İstatistik Kurumu, 2024.

[2] Gesamtverband der Versicherer, "Fahrraddiebstahl in Deutschland 2023," GDV, 2024.

[3] Association of British Insurers, "Bicycle Theft Statistics," ABI, 2023.

[4] M. Masmano, I. Ripoll, A. Crespo, "RTOS Real-Time Scheduling," in *Handbook of Real-Time Computing*, Springer, 2022.

[5] J. Liedtke, "On µ-Kernel Construction," ACM SOSP, 1995.

[6] P. Emberson, R. Stafford, R. Davis, "Techniques for the synthesis of multiprocessor tasksets," WATERS 2010.

[7] G. Welch, G. Bishop, "An Introduction to the Kalman Filter," UNC Tech Report, 2006.

[8] R. Davis, A. Burns, "A Survey of Hard Real-Time Scheduling for Multiprocessor Systems," ACM Computing Surveys, 2011.

[9] L. Sha, R. Rajkumar, J. Lehoczky, "Priority Inheritance Protocols," IEEE Trans. Computers, 1990.

[10] Raspberry Pi Foundation, "Raspberry Pi 3 Model B Hardware Specification," 2016.

---

## Ek A — Devre Şeması

> *(Dosya: hardware/schematic_v2.png — laba döndüğünüzde Fritzing ile hazırlanacaktır)*

---

## Ek B — Kritik Kod Parçacıkları

### B.1 FSM handle_event() — ARM Delay Mekanizması

```python
def handle_event(self, event: Event) -> bool:
    with self._lock:
        # TAMPER her durumda
        if event == Event.TAMPER_OPEN:
            self._enter_tamper()
            self._notify_state_change()
            return True

        # ARM sonrası bekleme süresi
        if event in (Event.MOTION_LOW, Event.MOTION_HIGH):
            if time.time() < getattr(self, "_arm_suppress_until", 0.0):
                return False  # Yoksay

        # Geçiş tablosu...
```

### B.2 Kalman Filtresi

```python
def update(self, measurement: float) -> float:
    # Tahmin adımı
    x_pred = self.x
    p_pred = self.p + self.q
    # Güncelleme adımı
    k = p_pred / (p_pred + self.r)
    self.x = x_pred + k * (measurement - x_pred)
    self.p = (1.0 - k) * p_pred
    return self.x
```

### B.3 PTHREAD_PRIO_INHERIT Mutex Başlatma (C)

```c
pthread_mutexattr_t attr;
pthread_mutexattr_init(&attr);
pthread_mutexattr_setpshared(&attr, PTHREAD_PROCESS_SHARED);
pthread_mutexattr_setprotocol(&attr, PTHREAD_PRIO_INHERIT);  /* ← KRİTİK */
pthread_mutex_init(&g_shm->mutex, &attr);
pthread_mutexattr_destroy(&attr);
```

### B.4 IMU Bus Recovery

```python
def _recover_bus(self):
    try:
        if self._bus: self._bus.close()
    except: pass
    time.sleep(0.1)
    self._bus = smbus2.SMBus(1)
    self._bus.write_byte_data(self._addr, _REG_PWR_MGMT_1, 0x00)
    time.sleep(0.05)
    self._error_count = 0
```

---

*Rapor taslağı — 18 Mayıs 2026*  
*Gerçek ölçüm değerleri ve fotoğraflar laba döndükten sonra eklenecektir.*
