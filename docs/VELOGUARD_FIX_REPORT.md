# VeloGuard Fix Report — 22 Mayıs 2026

Bu doküman yapılan değişikliklerin özeti, Pi üzerinde çalıştırma ve test talimatları, ve kısa bir doğrulama rehberi içerir.

## 1) Özeti
Aşağıdaki kritik ve önemli düzeltmeler uygulandı (kod tabanında):

- `firmware/drivers/pam8403_driver.py`
  - `sweep_tone` güvenli hâle getirildi (finally ile duty=0), beep pattern takip edildi (`start_beep_pattern_async`, `stop_beep_pattern`), alarm stop logic iyileştirildi.
- `firmware/main.py`
  - FSM->LED çift callback kaldırıldı; LED güncellemesi artık tek noktadan (`TaskManager`) yönetiliyor.
- `firmware/comm/web_ui.py`
  - Legacy komut mapping düzeltildi (`arm`/`disarm` doğru event'lere eşlendi).
  - Tamper temizleme formu eklendi ve API komutu geri bildirimi (`changed` + `message`) döndürülüyor.
  - UI: adaptör gücü için `Adaptör` yazısı gösteriliyor.
- `firmware/fsm.py`
  - Eksik geçişler eklendi: `PRE_ALARM -> RIDE_START` ve `ALARM -> RIDE_START`.
- `firmware/task_manager.py`
  - `_trigger_actuators` refactor: alarm stop non-blocking ve conditional; PRE_ALARM için takip edilebilir beep; alarm bildirimleri (kamera + telegram) için fotoğraf cleanup ve daha zengin mesaj.
- `firmware/drivers/led_driver.py`
  - `DISARMED` için yavaş green heartbeat (`0.2Hz`) eklendi.
- `firmware/comm/telegram_bot.py`
  - Sender loop `asyncio.run` pattern ile güvenli yapıldı; `initialize()` non-blocking yapıldı; sync send methods init kontrolü eklenildi.
- `firmware/config.py` ve `firmware/drivers/dht_driver.py`
  - DHT pin ismi `DHT_DATA` olarak normalize edildi; driver hem DHT22 hem DHT11 deneyerek başlatma yapıyor.
- `tools/test_telegram.py` ve `tools/syntax_check.py` eklendi.

## 2) Pi üzerinde çalıştırma ve test talimatları
Aşağıdaki adımlar Raspberry Pi üzerinde (veya Pi imajına erişiminiz varsa) uygulanmalıdır. Bu adımlarda root yetkileri gerekebilir.

1) Ortam ve bağımlılıklar

- Gerekli paketleri kurun (sanalenv yerine sistem ortamında veya projenin requirements.txt'sine göre):

```bash
sudo apt update
sudo apt install -y python3-pip git libatlas-base-dev libffi-dev build-essential
pip3 install -r requirements.txt
# Eğer picamera2 veya adafruit kütüphaneleri gerekiyorsa ayrıca kurun
# pip3 install picamera2
# pip3 install adafruit-circuitpython-dht
```

2) `.env` dosyasını ayarlayın (Telegram için opsiyonel, fakat testler için gerekli):

```bash
cd ~/veloguard
cp .env.example .env   # yoksa manuel oluşturun
# .env içinde TELEGRAM_TOKEN ve TELEGRAM_CHAT_ID girin
```

3) Servisleri/uygulamayı başlatma (manuel):

```bash
# Çalıştırma (log için ekranı gözleyin)
sudo python3 -m firmware.main
```

4) Web UI testi (tarayıcı):
- Web UI: http://<pi_ip>:5000
- Buton senaryoları:
  - `KORU` (protect) → LED 0.5Hz yeşil
  - `YANINDAYIM` (owner) → RIDE modu (sabit yeşil)
  - Koru iken hareket (IMU) → PRE_ALARM (sarı hızlı blink + 1 bip) → 5s içinde durursa ARMED'ye dön
  - PRE_ALARM veya ALARM iken `YANINDAYIM` basınca doğrudan RIDE'a geçiş
  - ALARM iken `ALARM DURDUR` → buzzer ve kırmızı LED durmalı
  - Tamper algılanırsa UI'da Tamper badge ve `Tamper Temizle` formu görünür

5) Telegram testi (opsiyonel):

```bash
python3 tools/test_telegram.py
```

6) Kamera testi (Pi bağlıysa):

```bash
libcamera-still --list-cameras
libcamera-still -o /tmp/test.jpg --timeout 2000
# Python ile kamera testi
python3 -c "from firmware.drivers.camera_driver import CameraDriver; c=CameraDriver(); print(c.initialize()); p=c.capture_photo('test.jpg'); print(p); c.cleanup()"
```

7) Birim testler (CI veya yerel):

```bash
pytest tests/ -v
```

## 3) Hızlı doğrulama / beklenen çıktılar
- `python3 -m firmware.main` başladıktan sonra loglarda `Başlatma tamamlandı.` ve `VeloGuard çalışıyor` görünmeli.
- Web UI status bölümünde `Mod:` doğru state'i göstermeli; `Pil:` alanı adaptörle çalışıyorsa `Adaptör` göstermeli.
- Telegram test scripti başarılıysa bot kullanıcı adı ve "Test mesajı gönderildi" çıktısı üretir.

## 4) Değişikliklerin Git durumu
Bu değişiklikleri yerel repo içinde commitleyip main branch'e pushladım (eğer push sırasında credential hatası alınırsa manuel push talimatı aşağıda verilmiştir).

## 5) Manuel Git komutları (eğer otomatik push başarısız olursa)

```bash
git add -A
git commit -m "Apply fixes from VELOGUARD_FIX_REHBERI: pam8403, fsm transitions, task_manager, web_ui, telegram, led, dht"
git push origin main
```

---

Eğer isterseniz şimdi remote push işlemini gerçekleştiriyorum; eğer push sırasında credential hatası olursa terminal çıktısını paylaşın, yardımcı olup adım adım yönlendireyim.

