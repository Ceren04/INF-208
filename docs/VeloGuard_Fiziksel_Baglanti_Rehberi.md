# VeloGuard — Fiziksel Bağlantı & Devre Rehberi

> **Son güncelleme:** 21 Mayıs 2026 — Breadboard güç rayı dağıtımı eklendi  
> **Platform:** Raspberry Pi 3B  
> **Pin numaralandırma:** BCM (tüm kod bu şemayı kullanır)

---

## 1. Proje Kod Durumu — Fiziksel Devreye Hazır mı?

| Bileşen | Yazılım | Fiziksel Test | Durum |
|---|---|---|---|
| MPU-6050 (IMU) | ✅ Tamamlandı | ✅ Pi'da çalışıyor | **HAZIR** |
| LED Yeşil (GPIO23) | ✅ Tamamlandı | ✅ Pi'da çalışıyor | **HAZIR** |
| LED Sarı (GPIO24) | ✅ Tamamlandı | ✅ Pi'da çalışıyor | **HAZIR** |
| LED Kırmızı (GPIO25) | ✅ Tamamlandı | ✅ Pi'da çalışıyor | **HAZIR** |
| Reed Switch KY-021 | ✅ Tamamlandı | ✅ Pi'da çalışıyor | **HAZIR** |
| Pasif Buzzer (GPIO18) | ✅ Tamamlandı | ⚠️ Bağlanacak, ses testi bekleniyor | **BAĞLA & TEST ET** |
| DHT11/22 | ✅ Tamamlandı | ❌ Fiziksel bağlantı yok | **BAĞLA & TEST ET** |
| INA219 | ✅ Tamamlandı | ❌ Fiziksel bağlantı yok | **BAĞLA & TEST ET** |
| Pi Camera | ✅ Tamamlandı | ❌ Fiziksel bağlantı yok | **BAĞLA & TEST ET** |
| 18650 Pil + BMS | — | ❌ Bağlanmadı | **BAĞLA** |

**Sonuç:** Tüm yazılım kodları eksiksiz ve testten geçmiş durumda (`54/54 birim testi PASSED`). Ses için PAM8403 gerekmez — elinizdeki **pasif buzzer** doğrudan GPIO18 PWM hattına bağlanır. Kalan bileşenleri fiziksel olarak bağladığınızda sistem tam fonksiyonel hale gelecektir.

---

## 2. Malzeme Listesi (Tam BOM)

| # | Bileşen | Adet | Not |
|---|---|---|---|
| 1 | Raspberry Pi 3B | 1 | PREEMPT-RT kernel gerekli |
| 2 | GY-521 (MPU-6050) modülü | 1 | 6-eksen IMU |
| 3 | INA219 modülü | 1 | Voltaj/akım ölçer |
| 4 | DHT11 veya DHT22 | 1 | Sıcaklık/nem sensörü |
| 5 | KY-021 Reed switch modülü | 1 | Sabotaj algılayıcı |
| 6 | Pasif buzzer (2 pin) | 1 | Alarm sesi — PAM8403 gerekmez |
| 7 | Pi Camera v2 (veya v1.3) | 1 | CSI ribbon kablo |
| 8 | LED Kırmızı (3mm veya 5mm) | 1 | Alarm göstergesi |
| 9 | LED Sarı (3mm veya 5mm) | 1 | Ön-alarm göstergesi |
| 10 | LED Yeşil (3mm veya 5mm) | 1 | Armed / RIDE göstergesi |
| 11 | 220Ω direnç | 3 | Her LED için 1 adet |
| 12 | 100Ω direnç | 1 | Pasif buzzer akım sınırlama (önerilir) |
| 13 | 10kΩ direnç | 1 | DHT pull-up (ham sensörse) |
| 14 | 18650 Li-ion pil | 2 | Seri bağlı ~7.4V |
| 15 | BMS (2S) veya MT3608 boost | 1 | Pil güvenlik devresi |
| 16 | Breadboard (830 tie-point) | 1 | Güç rayları + orta bölüm |
| 17 | Jumper kablo seti | — | M-F (Pi→breadboard) ve M-M (breadboard içi) |
| 18 | Mıknatıs (küçük neodim) | 1 | Reed switch için |

---

## 3. Raspberry Pi 3B GPIO Haritası

```
         3V3 [ 1] [ 2] 5V
 SDA  GPIO2 [ 3] [ 4] 5V
 SCL  GPIO3 [ 5] [ 6] GND
      GPIO4 [ 7] [ 8] GPIO14
         GND [ 9] [10] GPIO15
     GPIO17 [11] [12] GPIO18  ← Pasif Buzzer PWM
     GPIO27 [13] [14] GND
     GPIO22 [15] [16] GPIO23
         3V3 [17] [18] GPIO24
     GPIO10 [19] [20] GND
      GPIO9 [21] [22] GPIO25
     GPIO11 [23] [24] GPIO8
         GND [25] [26] GPIO7
      ID_SD [27] [28] ID_SC
     GPIO22 [15] [16] GPIO23  ← LED YEŞİL
         3V3 [17] [18] GPIO24  ← LED SARI
     GPIO10 [19] [20] GND
      GPIO9 [21] [22] GPIO25  ← LED KIRMIZI
     GPIO19 [35] [36] GPIO16
     GPIO26 [37] [38] GPIO20
         GND [39] [40] GPIO21

Kullanılan pinler:
  Pin  3 — GPIO2  — I2C SDA (MPU-6050 + INA219)
  Pin  5 — GPIO3  — I2C SCL (MPU-6050 + INA219)
  Pin  7 — GPIO4  — DHT11/22 DATA
  Pin 12 — GPIO18 — Pasif Buzzer (+) PWM sinyali
  Pin 13 — GPIO27 — Reed Switch SİNYAL
  Pin 16 — GPIO23 — LED YEŞİL (+)
  Pin 18 — GPIO24 — LED SARI (+)
  Pin 22 — GPIO25 — LED KIRMIZI (+)
  CSI    — Kamera ribbon konektörü
```

---

## 3.5 Breadboard Kurulumu — VCC ve GND Dağıtımı

Tüm modüller **breadboard güç rayları** üzerinden beslenir. Pi'den breadboard'a yalnızca **2 jumper** (3.3V + GND) gider; geri kalan her bileşen raylardan VCC/GND alır.

### Breadboard yapısı

```
                    ┌─── Breadboard ───────────────────────────────────────┐
                    │                                                      │
  Pi Pin 1 (3.3V)───┤  BB+  + + + + + + + + + + + + + + + + + + + + + + +  │← Kırmızı ray (3.3V)
                    │  BB-  - - - - - - - - - - - - - - - - - - - - - - -  │← Mavi ray (GND)
  Pi Pin 6 (GND)────┤                                                      │
                    │         ┌─ orta bölüm (sinyal + LED devreleri) ─┐   │
                    │         │  a  b  c  d  e    f  g  h  i  j        │   │
                    │         │  ·  ·  ·  ·  ·    ·  ·  ·  ·  ·  ← LED │   │
                    │         │  ·  ·  ·  ·  ·    ·  ·  ·  ·  ·  ← I2C│   │
                    │         └──────────────────────────────────────┘   │
                    │  BB+  + + + + + + + + + + + + + + + + + + + + + + +  │← Alt ray (üstle köprüle)
                    │  BB-  - - - - - - - - - - - - - - - - - - - - - - -  │
                    └──────────────────────────────────────────────────────┘
```

> **Ray köprüleme:** Breadboard'un üst ve alt güç rayları varsayılan olarak **ayrıdır**.  
> Üst BB+ ile alt BB+ arasına **M-M jumper**, üst BB- ile alt BB- arasına **M-M jumper** koyun.  
> Böylece tüm breadboard boyunca tek ortak 3.3V ve tek ortak GND elde edersiniz.

### Adım 0 — Güç raylarını Pi'ye bağla (ilk yapılacak iş)

| Breadboard | Jumper | Raspberry Pi | Açıklama |
|---|---|---|---|
| **BB+** (kırmızı ray) | M-F kırmızı | **Pin 1** (3.3V) | Tüm modül VCC buradan beslenir |
| **BB-** (mavi ray) | M-F siyah | **Pin 6** (GND) | Tüm modül GND buradan beslenir |

> Pi'den GND için Pin 6, 9, 14, 20, 25, 30, 34 veya 39 kullanılabilir — **yalnızca birini** BB-'ye bağlayın.  
> **3.3V modüllere 5V vermeyin** (MPU-6050, INA219, DHT, Reed → hepsi 3.3V).

### Ortak hatlar (breadboard üzerinde)

| Hat adı | Pi kaynağı | Breadboard'ta | Bağlı bileşenler |
|---|---|---|---|
| **BB+** | Pin 1 (3.3V) | Kırmızı güç rayı | MPU-6050 VCC, INA219 VCC, DHT VCC, Reed VCC |
| **BB-** | Pin 6 (GND) | Mavi güç rayı | Tüm GND, LED katot, Buzzer (-), IMU AD0, INA219 A0/A1 |
| **I2C_SDA** | Pin 3 (GPIO2) | Orta satır (ör. satır 30e) | MPU-6050 SDA + INA219 SDA |
| **I2C_SCL** | Pin 5 (GPIO3) | Orta satır (ör. satır 31e) | MPU-6050 SCL + INA219 SCL |

```
I2C ortak hat (breadboard orta bölüm):

  Pi Pin 3 ──→ [satır 30e] ←── MPU-6050 SDA
                          ←── INA219 SDA

  Pi Pin 5 ──→ [satır 31e] ←── MPU-6050 SCL
                          ←── INA219 SCL
```

### Bağlantı sırası (önerilen)

1. Breadboard ray köprüleri (üst ↔ alt BB+ ve BB-)
2. Pi → BB+ (3.3V) ve Pi → BB- (GND)
3. I2C ortak hatları (SDA, SCL satırları)
4. MPU-6050 ve INA219 modülleri (VCC/GND raylardan, SDA/SCL ortak satırdan)
5. DHT, Reed, LED'ler, pasif buzzer
6. Pi Camera (breadboard dışı, CSI ribbon)

---

## 4. Bileşen Bağlantıları — Breadboard Üzerinden

> Tüm VCC bağlantıları **BB+** rayına, tüm GND bağlantıları **BB-** rayına gider.  
> Sinyal pinleri (GPIO) Pi'den doğrudan veya breadboard orta satırı üzerinden bileşene ulaşır.

---

### 4.1 MPU-6050 (GY-521) — IMU ✅ Zaten Bağlı

> **Durum:** Pi'da test edildi ve çalışıyor. Bağlantı stabilitesini kontrol edin.

```
GY-521 Modülü       Breadboard / Pi
─────────────       ───────────────
VCC          ──────  BB+ (3.3V ray)
GND          ──────  BB- (GND ray)
SDA          ──────  I2C_SDA satırı  ←── Pi Pin 3 (GPIO2)
SCL          ──────  I2C_SCL satırı  ←── Pi Pin 5 (GPIO3)
AD0          ──────  BB- (GND ray)   → I2C adresi 0x68
INT          ──      (bağlamayın)
XDA, XCL     ──      (bağlamayın)
```

> **Önemli:** AD0 pini GND'ye bağlı → adres `0x68`.  
> AD0'ı 3.3V'a bağlarsanız adres `0x69` olur ve `config.py`'de `IMU_I2C_ADDR` güncellenmeli.  
> Eğer klon modülünüz varsa `WHO_AM_I` = `0x72` döner — kod bunu destekliyor, sorun değil.

---

### 4.2 INA219 Voltaj/Akım Sensörü — ❌ Bağlanmamış

> **Amaç:** 18650 pil voltajını ve devre akımını ölçer. Pil doluluk yüzdesi hesaplar.

```
INA219 Modülü       Breadboard / Pi
─────────────       ───────────────
VCC          ──────  BB+ (3.3V ray)
GND          ──────  BB- (GND ray)
SDA          ──────  I2C_SDA satırı  ←── MPU-6050 SDA ile aynı satır
SCL          ──────  I2C_SCL satırı  ←── MPU-6050 SCL ile aynı satır
A0           ──────  BB- (GND ray)   → I2C adresi 0x40
A1           ──────  BB- (GND ray)   → I2C adresi 0x40

INA219 Modülü       PİL DEVRE (breadboard dışı)
─────────────       ───────────────────────────
VIN+         ──────  Pil (+) / MT3608 çıkışı (+)
VIN-         ──────  Pi 5V besleme (+) — shunt üzerinden akım ölçümü
```

> **Adres çakışması YOK:** MPU-6050 → `0x68`, INA219 → `0x40`. Aynı I2C hattında birlikte çalışır.  
>
> **Güç ölçüm devresi şeması:**
> ```
> 18650 (+) ── BMS/Boost ── INA219 VIN+ ── INA219 VIN- ── Pi 5V Pin4
>                                    ↑ Buradaki shunt direnci akımı ölçer
> 18650 (-) ── GND ──────────────────────────────────── Pi GND Pin6
> ```
>
> **NOT:** INA219 modüllerinde genellikle dahili 0.1Ω shunt direnci vardır.  
> `ina219_driver.py` `set_calibration_32V_2A()` kullanıyor → maks 2A ölçüm.

---

### 4.3 DHT11 / DHT22 Sıcaklık & Nem Sensörü — ❌ Bağlanmamış

> **Kod notu:** `dht_driver.py` şu an `DHT11` sınıfını kullanıyor.  
> DHT22 kullanıyorsanız `dht_driver.py` satır 34'ü değiştirin:  
> `self._dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)`

#### Seçenek A — DHT modülü (3 pinli KY-015 veya benzeri)

```
DHT Modülü (3 pin)  Breadboard / Pi
──────────────────  ───────────────
VCC / +      ──────  BB+ (3.3V ray)
DATA / S     ──────  Pi Pin 7 (GPIO4) — doğrudan veya orta satır üzerinden
GND / -      ──────  BB- (GND ray)
```

> Modüllerde zaten pull-up direnci mevcut, harici direnç gerekmez.

#### Seçenek B — Ham DHT sensör (4 pin)

```
DHT Sensör (4 pin)  Breadboard
──────────────────  ──────────
Pin 1 VCC    ──────  BB+ (3.3V ray)
Pin 2 DATA   ──────  Pi Pin 7 (GPIO4) + 10kΩ pull-up → BB+
Pin 3 NC     ──      (bağlamayın)
Pin 4 GND    ──────  BB- (GND ray)
```

> **10kΩ pull-up zorunlu** — Ham sensör kullanıyorsanız DATA ve 3.3V arasına koyun!

---

### 4.4 KY-021 Reed Switch (Sabotaj Algılayıcı) ✅ Zaten Bağlı

> **Durum:** gpiozero ile yeniden yazıldı ve çalışıyor.

```
KY-021 Modülü       Breadboard / Pi
─────────────       ───────────────
VCC (+)      ──────  BB+ (3.3V ray)
GND (-)      ──────  BB- (GND ray)
SIG (S)      ──────  Pi Pin 13 (GPIO27)
```

> **Yazılım pull-up:** `reed_driver.py` → `Button(27, pull_up=True)`.  
> Harici pull-up direnci gerekmez, Pi'nin dahili pull-up'ı aktif.  
>
> **Mıknatıs konumu:**  
> - Mıknatıs yakında → devre KAPALI → `is_active=True` → NORMAL durum  
> - Mıknatıs uzakta → devre AÇIK → `is_active=False` → **TAMPER** tetiklenir

---

### 4.5 Pasif Buzzer (Alarm Sesi) — ⚠️ Bağlanacak

> **Donanım:** PAM8403 amplifikatör **gerekmez**. Elinizdeki pasif buzzer doğrudan GPIO18 PWM hattına bağlanır.  
> **Yazılım:** Kod değişikliği gerekmez — `pam8403_driver.py` GPIO18 üzerinden PWM frekansı üretir; pasif buzzer bu sinyali ses olarak çevirir.

```
Pasif Buzzer        Breadboard / Pi
────────────        ───────────────
(+) uzun bacak ────  Pi Pin 12 (GPIO18) ← [100Ω direnç] seri (breadboard satırında)
(-) kısa bacak ────  BB- (GND ray)
```

> **Pasif vs aktif buzzer:**  
> - **Pasif buzzer** (2 pin, üzerinde devre yok) → PWM frekansına göre ses üretir → **projede kullanılan**  
> - **Aktif buzzer** (3 pin, üzerinde devre var) → sabit ton verir, PWM ile uyumlu değildir  
>
> **Polarite:** Uzun bacak (+) → GPIO18 tarafı. Ses çıkmazsa kabloları ters çevirin.  
> **Direnç:** 100–220Ω seri direnç GPIO pinini korur (önerilir).  
> **Besleme:** Buzzer'a 3.3V veya 5V **doğrudan bağlamayın** — sadece GPIO18 + GND.  
>
> **Beklenen ses davranışı:**

| FSM Durumu | Ses |
|---|---|
| PRE_ALARM | 1000 Hz kısa bip |
| ALARM | 880–2200 Hz siren (yukarı-aşağı) |
| DISARM | Sessiz |

> Ses seviyesi PAM8403 + hoparlöre göre daha düşük olur; lab/demo ortamında yeterlidir.  
>
> **Pi ayarı:** `raspi-config` → `Advanced Options` → `Audio` → `None` yapın.  
> Aksi halde GPIO18 ses kartıyla çakışır.

#### Alternatif (opsiyonel): PAM8403 + Hoparlör

Daha yüksek ses gerekirse ileride PAM8403 modülü eklenebilir — kod değişikliği gerekmez:

```
PAM8403 VCC  → Pi Pin 4 (5V) — BB+ rayına BAĞLAMAYIN  |  PAM8403 IN-R → Pi Pin 12 (GPIO18)
PAM8403 GND  → BB- (GND ray)                           |  PAM8403 OUT  → Hoparlör
```

---

### 4.6 LED'ler (Kırmızı / Sarı / Yeşil) ✅ Zaten Bağlı

> **Durum:** Pi'da tüm FSM pattern'ları test edildi ve çalışıyor.

```
LED Devre Şeması (breadboard orta bölümde, her LED ayrı satırda):

Pi Pin 16 (GPIO23) ── [220Ω] ── LED YEŞİL  (+) ── LED (-) ── BB-
Pi Pin 18 (GPIO24) ── [220Ω] ── LED SARI    (+) ── LED (-) ── BB-
Pi Pin 22 (GPIO25) ── [220Ω] ── LED KIRMIZI (+) ── LED (-) ── BB-
```

> **Direnç hesabı:**  
> V_gpio = 3.3V, V_led ≈ 2.0V (kırmızı), I_led = 10mA  
> R = (3.3 - 2.0) / 0.01 = 130Ω → **220Ω kullanın** (güvenli marj)  
>
> **LED polaritesi:** Uzun bacak = anot (+) = GPIO tarafı.

---

### 4.7 Pi Camera — ❌ Bağlanmamış

> **Bağlantı:** Ribbon kablo ile CSI konektörü.

```
Adımlar:
1. Pi'yi KAPATIP güç kablosunu çıkarın
2. CSI konektörünün plastik kilidini kaldırın (hafifçe yukarı çekin)
3. Ribbon kabloyu mavi/metal tarafı USB portlarına bakacak şekilde takın
4. Plastik kilidi aşağı bastırarak kilitleyin
5. Pi'yi yeniden başlatın
```

> **Yazılım aktivasyonu:**
> ```bash
> sudo raspi-config
> # Interface Options → Camera → Enable → Reboot
> ```
>
> Veya `/boot/config.txt`'e ekleyin:
> ```
> start_x=1
> gpu_mem=128
> ```
>
> **Test:**
> ```bash
> libcamera-still -o test.jpg
> ```

---

### 4.8 18650 Pil + BMS Devre

> **Hedef:** Pi'yi 5V ile beslemek ve INA219 ile pil durumunu izlemek.

```
Güç Devresi Şeması:
─────────────────
2× 18650 (seri)  →  BMS 2S  →  MT3608 Boost (5V çıkış)
                                       │
                               INA219 VIN+
                               INA219 VIN−
                                       │
                               Pi GPIO (Pin 4 veya 2) — 5V
                               Pi GND  (Pin 6)
```

> **BMS neden gerekli?**  
> 18650 aşırı şarj (>4.25V/hücre) ve aşırı deşarj (<2.5V/hücre) koruması.  
>
> **MT3608 ayarı:**  
> Trim potansiyometreyi çevirerek çıkışı **5.1V**'a ayarlayın (voltmetre ile kontrol edin).  
> Pi 4.75–5.25V aralığında çalışır.  
>
> **INA219 bağlantısı için:** Boost çıkışı ile Pi arasına INA219 shunt'ını seri bağlayın.

---

## 5. Tam Bağlantı Özet Tablosu

### 5.1 Pi → Breadboard (sadece 2 güç + sinyal hatları)

| Pi Fiziksel Pin | GPIO / Hat | Breadboard / Hedef | Bağlantı tipi |
|---|---|---|---|
| Pin 1 (3.3V) | — | **BB+** kırmızı ray | M-F jumper — tüm VCC buradan |
| Pin 6 (GND) | — | **BB-** mavi ray | M-F jumper — tüm GND buradan |
| Pin 3 | GPIO2 (SDA) | I2C_SDA orta satır | M-F → MPU-6050 + INA219 SDA |
| Pin 5 | GPIO3 (SCL) | I2C_SCL orta satır | M-F → MPU-6050 + INA219 SCL |
| Pin 7 | GPIO4 | DHT DATA | M-F doğrudan |
| Pin 12 | GPIO18 | Pasif buzzer (+) via 100Ω | M-F → breadboard satırı |
| Pin 13 | GPIO27 | Reed SIG | M-F doğrudan |
| Pin 16 | GPIO23 | LED Yeşil (+) via 220Ω | M-F → breadboard satırı |
| Pin 18 | GPIO24 | LED Sarı (+) via 220Ω | M-F → breadboard satırı |
| Pin 22 | GPIO25 | LED Kırmızı (+) via 220Ω | M-F → breadboard satırı |
| CSI | — | Pi Camera | Ribbon (breadboard dışı) |

### 5.2 Breadboard rayları → Bileşenler (VCC / GND dağıtımı)

| Breadboard ray | Bağlı bileşen pinleri |
|---|---|
| **BB+** (3.3V) | MPU-6050 VCC, INA219 VCC, DHT VCC, Reed VCC |
| **BB-** (GND) | MPU-6050 GND, INA219 GND, DHT GND, Reed GND |
| **BB-** (GND) | MPU-6050 AD0, INA219 A0, INA219 A1 |
| **BB-** (GND) | LED Kırmızı/Sarı/Yeşil katot (-) |
| **BB-** (GND) | Pasif buzzer (-) |

### 5.3 Sinyal özeti

| GPIO (BCM) | Bağlı bileşen | Not |
|---|---|---|
| GPIO2 (SDA) | MPU-6050 + INA219 | Ortak I2C satırı |
| GPIO3 (SCL) | MPU-6050 + INA219 | Ortak I2C satırı |
| GPIO4 | DHT11/22 DATA | Ham sensörse 10kΩ → BB+ |
| GPIO23 / 24 / 25 | LED Yeşil / Sarı / Kırmızı | 220Ω seri, katot → BB- |
| GPIO18 | Pasif buzzer (+) | 100Ω seri, (-) → BB- |
| GPIO27 | Reed SIG | Pull-up yazılımsal |

---

## 6. I2C Adresleri Çakışma Kontrolü

```
I2C Bus 1 (GPIO2/GPIO3):
  ├── 0x40 — INA219
  └── 0x68 — MPU-6050 (klon: 0x72)

Kontrol komutu (Pi'da):
  sudo i2cdetect -y 1

Beklenen çıktı:
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
  00:          -- -- -- -- -- -- -- -- -- -- -- -- --
  10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
  60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --
  70: -- -- -- -- -- -- -- --
```

---

## 7. Kritik Yazılım Notu: DHT11 vs DHT22

`dht_driver.py` içinde **şu an DHT11** kullanılıyor:

```python
# satır 34 — dht_driver.py
self._dht = adafruit_dht.DHT11(board.D4, use_pulseio=False)
```

**Elinizde DHT22 varsa** bu satırı değiştirin:

```python
self._dht = adafruit_dht.DHT22(board.D4, use_pulseio=False)
```

DHT22 daha hassas (-40~80°C, ±0.5°C) ve projede önerilen sensördür.

---

## 8. Fiziksel Bağlantı Sonrası Test Prosedürü

### Adım 1 — I2C Taraması

```bash
# Tüm bileşenleri bağladıktan sonra
sudo i2cdetect -y 1
# 0x40 (INA219) ve 0x68 (MPU-6050) görünmeli
```

### Adım 2 — Kamera Testi

```bash
libcamera-still -o /tmp/test.jpg && echo "Kamera OK"
```

### Adım 3 — Tüm Sensör Entegrasyon Testi

```bash
cd ~/veloguard
source venv/bin/activate
python3 tools/sensor_test_all.py
```

Beklenen çıktı:
```
[1/3] Sürücü başlatma:
  IMU (MPU-6050)       ✓ HAZIR
  LED (GPIO23/24/25)   ✓ HAZIR
  Reed Switch (GPIO27) ✓ HAZIR
  PAM8403 (GPIO18)     ✓ HAZIR   ← log adı; fiziksel olarak pasif buzzer
  DHT22 (GPIO4)        ✓ HAZIR   ← yeni
  INA219 (I2C 0x40)   ✓ HAZIR   ← yeni

[2/3] 30 saniye veri akışı:
  (IMU, CPU sıcaklık, voltaj/akım, reed durumu tablosu)

[3/3] Aktüatör testi:
  LED ✓
  PAM8403 ✓  (pasif buzzer'dan 2 bip duyulacak)
```

### Adım 4 — Birim Testleri

```bash
pytest tests/ -v
# 54/54 PASSED bekleniyor
```

### Adım 5 — Ana Sistemi Başlat

```bash
sudo venv/bin/python3 -m firmware.main
```

Başarılı başlatma logu:
```
INFO  IMU: WHO_AM_I: 0x68 ✓
INFO  IMU: MPU-6050 başlatıldı — adres 0x68
INFO  LED sürücüsü başlatıldı.
INFO  Reed switch başlatıldı — GPIO27 — durum: kapalı
INFO  PAM8403 ses sürücüsü başlatıldı.   ← pasif buzzer GPIO18'e bağlı
INFO  DHT11 başlatıldı — GPIO4          ← yeni
INFO  INA219 başlatıldı — voltaj: 3.85V ← yeni
INFO  VeloGuard başlatıldı — Web UI: http://<Pi_IP>:5000
```

### Adım 6 — Web UI ile FSM Testi

```
Tarayıcıdan: http://<Pi_IP_adresi>:5000

Test sırası:
1. "ARM" → Yeşil LED 0.5Hz yanıp sönmeli
2. Bisiklete hafifçe vur → Sarı LED 4Hz yanıp sönmeli (PRE_ALARM)
3. Güçlü vur → Kırmızı LED 10Hz + pasif buzzer siren (ALARM)
4. "DISARM" → Tüm LED'ler söner
5. Reed switch mıknatısını uzaklaştır → TAMPER tetikler
```

### Adım 7 — Telegram Botu

```bash
nano .env
# TELEGRAM_TOKEN=<BotFather'dan alınan token>
# TELEGRAM_CHAT_ID=<kendi chat ID'niz>
```

### Adım 8 — 30 Dakika Kararlılık Testi

```bash
sudo venv/bin/python3 -m firmware.main &
# 30 dakika çalışmasını izleyin
tail -f /var/log/veloguard/veloguard.log
```

---

## 9. Sık Karşılaşılan Sorunlar

| Sorun | Olası Sebep | Çözüm |
|---|---|---|
| `i2cdetect` 0x68 göstermiyor | Loose kablo veya BB+ beslemesi yok | BB+/BB- ray köprülerini ve I2C SDA/SCL satırlarını kontrol et |
| `i2cdetect` 0x40 göstermiyor | INA219 VCC/GND raylara bağlı değil | INA219 VCC→BB+, GND→BB- kontrol et |
| Modül çalışmıyor, Pi ısınıyor | BB+ ile BB- kısa devre | Raylarda ters polarite veya metal temas kontrol et |
| Breadboard'ta bazı satırlar çalışmıyor | Üst/alt ray köprüsü eksik | BB+↔BB+ ve BB-↔BB- arası M-M jumper ekle |
| DHT `RuntimeError: Checksum error` | Hızlı okuma veya gürültü | Pull-up direnci ekle; `use_pulseio=False` dene |
| Pasif buzzer ses çıkmıyor | GPIO18 çakışması veya polarite ters | `raspi-config` → Audio → None; (+) ve (-) kablolarını ters dene |
| Buzzer çok zayıf | GPIO akımı sınırlı (normal) | Lab için yeterli; daha yüksek ses için PAM8403 eklenebilir |
| Aktif buzzer kullanıldı | PWM frekans değişimini desteklemez | Pasif buzzer (2 pin) kullanın |
| Kamera `Failed to open` | CSI kablosu gevşek | Güç kapalıyken tekrar tak |
| Reed `TAMPER` sürekli tetikliyor | Mıknatıs çok uzak | Mıknatısı switch'e 5mm'den yakın konumlandır |
| INA219 `Geçersiz voltaj: 0` | Pil bağlı değil | VIN+ ve VIN- bağlantılarını kontrol et |

---

## 10. Güvenlik Uyarıları

> ⚠️ **Breadboard BB+ yalnızca Pi Pin 1 (3.3V) ile beslenmeli** — 5V'u BB+'ya bağlamayın.  
> ⚠️ **Pi'yi kapatmadan bağlantı değiştirmeyin** — özellikle güç raylarında.  
> ⚠️ **GPIO pinlerine 3.3V'dan fazla uygulamamayın** — Pi kalıcı zarar görebilir.  
> ⚠️ **18650 pili koruyucu devre (BMS) olmadan kullanmayın** — yangın riski.  
> ⚠️ **LED'leri dirençsiz bağlamayın** — GPIO veya LED yanar.  
> ⚠️ **Pasif buzzer'a 3.3V/5V doğrudan bağlamayın** — sadece GPIO18 + GND kullanın.  
> ⚠️ **MT3608 çıkışını ölçmeden Pi'ye bağlamayın** — 5.1V'a ayarlı olmalı.

---

*Bu belge `firmware/config.py` ve tüm sürücü dosyaları esas alınarak hazırlanmıştır.*
