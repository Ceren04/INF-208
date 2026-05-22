"""
Telegram bağlantısı ve fotoğraf gönderimi test scripti.
Çalıştır: python3 tools/test_telegram.py
"""
import asyncio
import os

async def test_telegram():
    token = os.getenv("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("ERROR: TELEGRAM_TOKEN veya TELEGRAM_CHAT_ID .env'de eksik")
        return

    import telegram
    bot = telegram.Bot(token=token)

    # 1. Bağlantı testi
    me = await bot.get_me()
    print(f"✓ Bot bağlı: @{me.username}")

    # 2. Mesaj gönder
    await bot.send_message(chat_id=chat_id, text="🧪 VeloGuard test mesajı")
    print("✓ Test mesajı gönderildi")

    # 3. Test fotoğrafı gönder (varsa)
    test_img_path = "/tmp/test_alarm.jpg"
    if os.path.exists(test_img_path):
        with open(test_img_path, "rb") as f:
            await bot.send_photo(chat_id=chat_id, photo=f, caption="🧪 Test fotoğrafı")
        print(f"✓ Test fotoğrafı gönderildi: {test_img_path}")
    else:
        print(f"ℹ Test fotoğrafı yok ({test_img_path}), sadece mesaj testi yapıldı")
        print("  Fotoğraf testi için önce kamerayı test edin:")
        print("  libcamera-still -o /tmp/test_alarm.jpg")

if __name__ == "__main__":
    asyncio.run(test_telegram())
