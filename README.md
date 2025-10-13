# 🦁 LionBackup

**Автоматичен бекъп система с графичен интерфейс и system tray интеграция**

![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---
##⭐ Харесай проекта
Ако LionBackup ти е полезен, остави ⭐ на проекта!

## 📋 Описание

LionBackup е мощна и лесна за използване програма за автоматичен бекъп на файлове и папки. Програмата работи в background като system tray приложение и автоматично създава ZIP архиви на определени интервали.

### ✨ Ключови функционалности

- 🎨 **Интуитивен GUI интерфейс** - Лесен за използване графичен интерфейс
- 🔄 **Автоматичен бекъп** - Периодично архивиране на файлове
- 📦 **ZIP компресия** - Автоматично създаване на ZIP архиви
- 🔢 **Версиониране** - Автоматична номерация без презаписване (-2, -3, -4...)
- 💾 **System Tray интеграция** - Работи в background в скритите икони
- ⏱️ **Гъвкави интервали** - От 1 минута до 24 часа
- 🦁 **Красив дизайн** - Модерен интерфейс с lion тема

---

## 🚀 Инсталация

### Стъпка 1: Клониране на проекта
```bash
git clone https://github.com/yourusername/lionbackup.git
cd lionbackup
```

### Стъпка 2: Инсталиране на зависимости
```bash
pip install -r requirements.txt
```

### Стъпка 3: Стартиране
```bash
python lionbackup.py
```
или без терминал:
```bash
pythonw lionbackup.py
```

### 📦 Build на .EXE файл

### Метод 1: Основен build (по-бърз)
```bash
pyinstaller --name="LionBackup" --onefile --windowed --icon=lion.ico lionbackup.py
```

### Метод 2: Оптимизиран build (препоръчва се)
```bash
pyinstaller --name="LionBackup" ^
            --onefile ^
            --windowed ^
            --icon=lion.ico ^
            --add-data "icon.png;." ^
            --hidden-import=PIL ^
            --hidden-import=pystray ^
            --noconsole ^
            --clean ^
            lionbackup.py
```

###📞 Поддръжка
Ако имаш въпроси или проблеми:

Отвори Issue
Пиши на martin@liondevs.com
