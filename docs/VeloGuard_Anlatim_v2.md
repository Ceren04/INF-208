# 🛡️ VeloGuard — Akıllı Bisiklet Koruma Sistemi
## Proje Tanıtım Dokümanı

> *Kısa, anlaşılır, herkesin (aile, arkadaş, ekip arkadaşı) okuyup ne yaptığımızı anlayabileceği genel anlatım.*

---

## 🎯 Bir Cümlede

VeloGuard, bisikletinin başında olmadığında onu sana **gözlerin** ve **kulakların** olur — biri dokunursa fark eder, ciddi bir şey olursa anında **telefonuna bildirim** ve **fotoğraf** gönderir.

---

## 🤔 Neyi Çözüyor?

Gündelik hayatta hepimizin yaşadığı bir sorun var:
- Markete giderken bisikletini dışarıda bırakıyorsun.
- Üniversitedeki dersine girerken park ediyorsun.
- Kafede arkadaşınla otururken kapıdan dışarıya bakıp duruyorsun.

Aklının bir köşesi hep bisikletinde. **"Acaba kilidi yeterli mi?"**, **"Biri ona dokunuyor mu?"**, **"Çoktan götürmüş olmasınlar?"**.

VeloGuard tam burada devreye giriyor: bisikletini gözetlemek için orada olmak zorunda değilsin, çünkü **o kendini gözetliyor**.

---

## 💡 Nasıl Çalışıyor? (Hikaye gibi)

### Park ettiğinde
Bisikletini park ediyorsun, telefonundaki uygulamaya tıklayıp **"Beni koru"** diyorsun. Sistem uyanıyor, ortamı 30 saniye boyunca **"dinliyor"** — rüzgar var mı, yakında sürekli geçen araba var mı, gibi normal şeyleri öğreniyor. Sonra sessizce bekliyor.

### Biri dokunduğunda
Birisi bisikletine dokunuyor. Sistem hemen anlıyor ama **"durup düşünüyor"**:

> *"Bu hafif bir esinti mi, yoksa biri gerçekten elini sürdü mü?"*

Eğer hafif bir şey ise (rüzgar, yandan geçen biri sürtündü) — kısa bir LED yanıp sönüyor ama **sesli alarm vermiyor**. Çünkü sürekli yanlış alarm veren bir sistem, kimsenin işine yaramaz.

### Ciddi bir şey olduğunda
Hareket sürüyor, bisiklet sallanıyor, hatta yerinden oynatılıyor. İşte o zaman:

1. 🔊 **Yüksek sesli alarm** çalmaya başlıyor (mini hoparlör) — hırsızı caydırmak için.
2. 💡 **Kırmızı LED** yanıp sönüyor.
3. 📷 **Kamera bir kaç fotoğraf çekiyor** — kim yaklaşmış, suç delili gibi.
4. 📱 **Telefonuna bildirim** geliyor: *"Bisikletine dokunuluyor! İşte fotoğraf."*

Sen ister kafede oturuyor olasın, ister dersteysin — bisikletinde olan bitenden anında haberin oluyor.

### Sürmek istediğinde
Telefondan **"Sürüyorum"** dediğinde sistem rahatlıyor, alarm modunu kapatıyor. Tabii hâlâ uyanık — kutusunu açmaya kalkışan biri olursa yine alarm veriyor.

---

## 🚲 Neden Sadece Bisiklet Değil?

Aslında aynı sistem **scooter** ve **motosiklet** için de çalışabilir. Mantık aynı:
> *"Hareket eden bir aracı sahibi yokken koruyalım."*

Tek fark, motosikletin kendi titreşimi daha güçlü, scooter'ın yapısı farklı. Bunun için sistem akıllı: kullanıcı uygulamadan **"Ben bisikletteyim / scooter'dayım / motosikletteyim"** diye seçiyor, sistem ona göre kendini ayarlıyor.

Yani bir donanım, üç farklı araç, üç farklı kişilik.

---

## 🧠 Sistemin "Ruh Hali"

Sistem aslında 5 farklı ruh halinde olabiliyor:

| Mod | Ne yapıyor? |
|---|---|
| 😴 **Kapalı** | Hiçbir şey izlemiyor, dinleniyor. |
| 👁️ **Koruma** | Sessizce gözlüyor, en ufak şeyi bile fark eder. |
| 🤔 **Şüpheli** | "Bir şey oldu ama emin değilim" — uyarıyor ama bağırmıyor. |
| 🚨 **Alarm** | "Tamam, bu ciddi!" — sirenler, ışıklar, telefon bildirimi. |
| 🚴 **Sürüş** | "Sahibi sürüyor, alarm yok ama yine de uyanık." |

Bu modlar arasında **akıllıca** geçiş yapıyor — sahibinin tepkisine, çevreye, geçen zamana göre.

---

## 🛠️ Neye İhtiyacımız Var?

Donanım tarafında:

- 🍓 **Raspberry Pi** — sistemin beyni (zaten elimizde var)
- 📍 **Hareket sensörü** — bir telefonda olan jiroskoba benzer, titreşimi ve eğimi anlıyor
- 📷 **Kamera** — alarm anında fotoğraf çekiyor
- 🔊 **Mini hoparlör + amplifikatör (PAM8403)** — yüksek sesli alarm
- 💡 **LED'ler** — görsel uyarı
- 🔋 **Pil** — bisikletin yanında prizi olmaz, kendi gücüyle çalışacak
- 🌡️ **Sıcaklık sensörü** — yazın aşırı ısınmasın diye kontrol
- 📦 **Su geçirmez kutu** — yağmurda bozulmasın diye
- 🔧 **Bisiklet bağlantı aparatı** — sele altına gizlice monte edilecek

Yazılım tarafında:
- Pi üzerinde çalışan **gerçek zamanlı işletim sistemi**
- Bisikletinin "ruh halini" yöneten **karar verici program**
- Telefonuna bildirim gönderen **mesajlaşma servisi** (Telegram gibi)
- Kameradaki görüntüleri analiz eden **görüntü işleme**

---

## 🏗️ Cihaz Bisiklette Nereye Konacak?

Düşündüğümüz yer: **sele altı**. Üç sebebi var:

1. **Gizli** — hırsız ilk bakacağı yerlerden değil.
2. **Titreşimi iyi alır** — kadronun iskeletine bağlı, en küçük dokunuşu hisseder.
3. **Bakım kolay** — sele kaldırılınca kutuya ulaşılır.

LED ve buzzer ise **biraz görünür** olacak — çünkü "bu bisiklette alarm var" görüntüsü, hırsızın elini durdurabilir. Yani **beyin gizli, ses yüksek**.

---

## 👥 Kim Ne Yapacak? (3 Kişilik Ekip)

Projeyi üç ana parçaya bölüyoruz, her birinin bir sorumlusu var:

### 👤 Birinci Arkadaş — "Donanımcı"
> *Sistemin elleri ve gözleri.*

- Sensörleri ve diğer modülleri Pi'a bağlayacak.
- Devreyi düzenli ve sağlam hale getirecek.
- Kutunun ve bisiklet bağlantı aparatının tasarımını yapacak.
- Pil ve güç sistemini kuracak.
- Bisiklete fiili montajı yapacak ve test edecek.

### 👤 İkinci Arkadaş — "Beyin Mühendisi"
> *Sistemin nasıl düşüneceğini yazıyor.*

- Pi üzerinde işletim sistemi kurulumunu yapacak.
- Sistemin "ruh hallerini" ve geçişlerini programlayacak.
- Hareket verisini temizleyip anlamlı hale getirecek (gürültü ayıklama).
- Yanlış alarmları engelleyen akıllı eşik mantığını yazacak.
- Sistemin tüm parçalarının uyum içinde çalıştığından emin olacak.

### 👤 Üçüncü Arkadaş — "Göz ve Ses"
> *Sistemin dış dünyayla iletişimi.*

- Kamerayı çalıştıracak ve hareket gördüğünde fotoğraf almasını sağlayacak.
- Telegram botunu kuracak — alarm bildirimleri için.
- Basit bir telefon arayüzü yapacak (web sayfası gibi: ARM/DISARM tuşları).
- Sistemin enerji/sıcaklık verilerini grafiklere dönüştürecek.
- Demo videosunu çekip kurgulayacak.

### 🤝 Birlikte Yapılacaklar
- Haftada 2 kez toplantı
- Final raporun yazımı
- Sunum hazırlığı
- Test günleri (gerçek bisiklette deneme)

---

## 📅 Zaman Çizelgesi (Genel Bakış)

| Ne zaman? | Ne olacak? |
|---|---|
| **Bu hafta (4-8 Mayıs)** | Plan netleşecek, ön rapor (Exposé) hocaya teslim edilecek, donanım siparişi verilecek |
| **9-19 Mayıs** | Donanım eline ulaşacak, sensörler tek tek test edilecek, ilk prototip kurulacak |
| **20-26 Mayıs** | Sistemin "beyni" yazılacak — karar verme, modlar, alarm mantığı |
| **27 May - 2 Haz** | Kamera, telefon bildirimleri, ölçümler, grafikler tamamlanacak |
| **3-5 Haziran** | Rapor yazımı, sunum hazırlığı, demo videosu |
| **5 Haziran 14:45** | 🚨 **TESLİM!** |

---

## 🎬 Sunumda Ne Göstereceğiz?

Hocaya canlı demo yapacağız:

1. **"Park ettim"** → uygulamaya basıyoruz, sistem korumaya geçiyor
2. **"Hafifçe dokundum"** → sistem fark ediyor ama ses çıkarmıyor (yanlış alarm engelleme)
3. **"Sallıyorum"** → ALARM! Buzzer çalıyor, telefonumuza bildirim geliyor, fotoğraf görünüyor
4. **"İndim, sürüyorum"** → sistem sürüş moduna geçiyor, sessizleşiyor
5. **"Kutuyu açmaya çalışıyorum"** → tamper alarmı, bu mod kapatılamıyor

5 dakikalık bir video da çekeceğiz — gerçek bisiklette, gerçek senaryolarla.

---

## ⚡ Bu Projeyi Özel Yapan Şey

Çoğu öğrenci projesi ya çok teorik kalıyor ya da çok basit bir oyuncak oluyor. **VeloGuard farklı:**

- ✅ **Gerçek bir problemi çözüyor** — bisiklet hırsızlığı her şehirde var
- ✅ **Tek araçla sınırlı değil** — bisiklet, scooter, motosiklet
- ✅ **Akıllı** — yanlış alarm vermemek için kendi kendine öğreniyor
- ✅ **Görsel kanıt üretiyor** — sadece "alarm verdi" demiyor, fotoğraf gösteriyor
- ✅ **Açık kaynak** — kodumuzu herkesle paylaşıyoruz, başkaları geliştirebilir

Hocamızın değerlendirme tablosundaki **inovasyon** ve **uygulanabilirlik** kalemlerinde tam puan almayı hedefliyoruz.

---

## 🎁 Ekstra Bonuslar

İki tane fazladan puan getirecek şey ekledik:

1. **GitHub'da açık kaynak yapacağız** → +5 puan
2. **Kamera ve görüntü işleme kullanacağız** → +5 puan

Yani toplam puan hedefi 110 değil, **120**.

---

## 🔮 İleride Neler Eklenebilir?

Bu proje bittikten sonra (mezun olduktan sonra bile devam edebilir), eklenebilecekler:

- 📍 **GPS modülü** — bisiklet götürülürse nerede olduğunu gör
- 📱 **Mobil uygulama** — Telegram yerine güzel bir Android/iOS app
- 🔓 **Otomatik kilit** — alarm anında bisiklet tekerleğini kilitleyen mekanizma
- 🤖 **Yapay zeka** — sadece hareket değil, "kim yaklaşıyor"u anlasın (sahip mi, hırsız mı?)
- ☁️ **Bulut sistemi** — birden fazla bisiklet, harita üzerinde dashboard

Bu özellikler raporda **"Gelecek Çalışma"** olarak yer alacak — hocaya "vizyonumuz var" mesajı verecek.

---

## 🌟 Son Söz

VeloGuard, 4 hafta gibi kısa sürede yapılabilecek **ama gerçek hayatta da işe yarar** bir proje. Üçümüzün becerilerini birleştirdiğimizde:

- Donanım çalışır,
- Yazılım akıllı çalışır,
- Sunum etkileyici olur,
- Hocanın istediği her teknik şart karşılanır,
- Üstüne biraz bonus alırız.

Önemli olan **disiplin ve iletişim**. Her hafta sonunda kim ne yaptı paylaşırız, takılan olursa hemen söyler. Mükemmellik ileride gelir, **şimdi hareket etme zamanı**.

🚲💨 **Hadi başlayalım!**

---

*Bu doküman, VeloGuard projesinin genel anlatımıdır. Teknik detaylar (sensör modelleri, devre şemaları, kod yapıları, ölçüm yöntemleri vs.) için **VeloGuard_Proje_Plani.md** dosyasına bakınız.*

*Versiyon 1.1 — 09.05.2026 — Mevcut envantere göre güncellendi (PAM8403+hoparlör, DHT22, Pi 3B)*
