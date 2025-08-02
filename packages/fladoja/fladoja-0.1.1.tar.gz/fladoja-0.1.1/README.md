<div align="center">
  <h1>Fladoja Framework</h1>
  
  ![Python Version](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)
  ![License](https://img.shields.io/badge/license-SiteProjectGo-green)
  ![PyPI Version](https://img.shields.io/pypi/v/fladoja)
  ![Downloads](https://img.shields.io/pypi/dm/fladoja)

  <p>Гибридный фреймворк, сочетающий простоту Flask, функциональность Django и скорость FastAPI</p>
</div>

---

## 📦 Установка
```bash
pip install fladoja
```

## 🚀 Быстрый старт
```python
from fladoja import Fladoja

app = Fladoja("MyApp")

@app.site("/")
def home(params):
    return app.file_template("index.html", {"title": "Главная"})

app.start(port=8000)
```

## ✨ Основные возможности
- 🛠️ Встроенная админ-панель
- 🚀 Простая маршрутизация через `@app.site()`
- 📦 Система плагинов `@app.plagen()`
- 🎨 Поддержка шаблонов с наследованием
- 🔒 Авторизация через переменные окружения

## 📚 Документация
Полная документация доступна на [GitHub Wiki](https://github.com/yourusername/fladoja/wiki)

---

## 🔒 Лицензия
<div align="center">
  <img src="https://raw.githubusercontent.com/yourusername/fladoja/main/docs/assets/license_logo.png" width="200" alt="SiteProjectGo License">
  
  **SiteProjectGo License**  
  [Полный текст лицензии](LICENSE)
</div>

### Основные положения:
- ✅ Разрешено коммерческое использование
- ✅ Возможность модификации кода
- ❌ Запрещена перепубликация под другим именем
- ⚠️ Без гарантий поддержки

---

## 📬 Контакты
- Email: support@yourproject.com
- Telegram: [@fladoja_support](https://t.me/fladoja_support)
- Issues: [GitHub Issues](https://github.com/yourusername/fladoja/issues)