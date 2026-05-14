# Katkı Rehberi — VeloGuard

## Dallanma Stratejisi
- `main` → stabil, her zaman çalışır
- `feature/XXX` → yeni özellikler
- `fix/XXX` → hata düzeltmeleri

## Kod Stili
- Python: PEP 8, tür ipuçları (type hints) zorunlu
- C: Linux Kernel coding style
- Docstring: Google-style

## Test
```bash
cd veloguard
pytest tests/ -v --tb=short
```

## Commit Mesajları
```
feat: IMU Kalman filtresi eklendi
fix: Reed switch debounce hatası düzeltildi
docs: Priority Inheritance bölümü güncellendi
```

## Ekip
- Üye-1 (Donanımcı): donanım, devre, BOM
- Üye-2 (Yazılım): FSM, RTOS, algoritmalar
- Üye-3 (Göz/Ses/Comm): kamera, Telegram, web UI
