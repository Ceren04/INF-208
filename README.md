# INF-208

```markdown
# 🛡️ VeloGuard

> Smart anti-theft system for bicycles, scooters, and motorcycles  
> Raspberry Pi 4 + PREEMPT-RT + IMU + Camera + Image Processing

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Status: WIP](https://img.shields.io/badge/status-work%20in%20progress-orange)](#)

## 🎯 Project Goal

VeloGuard detects unauthorized movement of two-wheel vehicles using IMU + camera fusion,
and notifies the owner via Telegram with photographic evidence. The same hardware module
adapts to bikes, scooters, and motorcycles via software profiles.

## 📚 Course

INF 208 — Embedded Systems / Eingebettete Systeme  
Türkisch-Deutsche Universität (TAU), Spring 2026  
Instructor: Prof. Dr. Murat Beken

## 👥 Team

- [Üye 1] — Hardware Engineer
- [Üye 2] — RTOS / Software Lead
- [Üye 3] — Vision / Communication / Evaluation

## 🚧 Status

Currently in **Sprint 0**: planning + exposé preparation. See [docs/](./docs) for current state.

## 📄 License

MIT — see [LICENSE](./LICENSE)
```

**Commit changes** → "Update README.md" → **Commit changes** butonuna tıkla.

##### Adım 5: Klasör Yapısını Oluştur
GitHub web arayüzünden:
1. **"Add file"** → **"Create new file"**
2. Dosya adı: `docs/.gitkeep` (sadece boş dosya, klasör oluşması için)
3. **"Commit new file"**
4. Aynı şekilde:
   - `firmware/.gitkeep`
   - `hardware/.gitkeep`
   - `tools/.gitkeep`
   - `presentation/.gitkeep`

##### Adım 6: CONTRIBUTING.md Ekle
Bonus puan için:
1. **"Add file"** → **"Create new file"**
2. Dosya adı: `CONTRIBUTING.md`
3. İçerik:

```markdown
# Contributing to VeloGuard

Thank you for your interest! VeloGuard is an academic project, but we welcome external contributions.

## How to Contribute

1. Fork this repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add some feature"`
4. Push to your fork: `git push origin feature/your-feature`
5. Open a Pull Request

## Code Style

- **Python**: Follow PEP 8. Use `black` for formatting.
- **C**: Follow the Linux kernel style. Use 4-space indentation.

## Reporting Bugs

Use GitHub Issues. Include:
- Description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Hardware/software environment
```
