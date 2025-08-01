<div align="center">

# 🚀 py-schedulerx

### ⚡ Lightweight Python Task Scheduler ⚡

*Periyodik görevlerinizi kolayca yönetin - Sıfır bağımlılık, maksimum performans*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Dependencies-Zero-orange?style=for-the-badge" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Threading-Supported-red?style=for-the-badge" alt="Threading Support">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Stable-success?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Version-0.1.0-informational?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Maintained-Yes-brightgreen?style=flat-square" alt="Maintained">
</p>

</div>

---

```python
import py_schedulerx as schedule

@schedule.every("30s")
def my_task():
    print("🎯 Task executed!")

schedule.run_forever()  # ✨ That's it!
```

---


**py-schedulerx**, Python projelerinde periyodik görevleri kolayca zamanlamak için geliştirilmiş hafif ve sade bir zamanlayıcı kütüphanedir. Fonksiyonları belirli aralıklarla otomatik olarak çalıştırmanızı sağlar.

## ✨ Özellikler

- 🎯 **Sade API**: `@schedule.every("30s")` gibi basit decorator kullanımı
- 🧵 **Threading Desteği**: `threaded=True` ile non-blocking görev çalıştırma
- ⏰ **Esnek Zaman Formatları**: "30s", "5m", "2h", "1d" gibi human-readable formatlar
- 🚀 **Sıfır Bağımlılık**: Pure Python, harici kütüphane gerektirmez
- 🛠️ **Robust Hata Yönetimi**: Görev hatalarında kütüphane çökmez
- 📏 **Hafif**: Minimal kod tabanı, hızlı başlangıç

## 🚀 Kurulum

```bash
pip install py-schedulerx
```

## 📖 Hızlı Başlangıç

### Temel Kullanım

```python
import py_schedulerx as schedule

@schedule.every("30s")
def fetch_data():
    print("API'den veri çekiliyor...")

@schedule.every("5m")
def cleanup_logs():
    print("Log dosyaları temizleniyor...")

@schedule.every("1h")
def backup_database():
    print("Veritabanı yedekleniyor...")

# Zamanlayıcıyı başlat
schedule.run_forever()
```

### Threading ile Paralel Çalışma

```python
import py_schedulerx as schedule
import time

@schedule.every("3s", threaded=True)
def heavy_task():
    print("Ağır işlem başladı...")
    time.sleep(10)  # Ana thread'i bloklamaz
    print("Ağır işlem tamamlandı!")

@schedule.every("1s")
def quick_task():
    print("Hızlı görev çalıştı")

schedule.run_forever()
```

### Gelişmiş Kullanım

```python
from py_schedulerx import Scheduler

# Özel scheduler instance'ı oluştur
scheduler = Scheduler()

# Programatik olarak görev ekleme
def my_task():
    print("Görev çalıştı!")

scheduler.add_job(my_task, "2m", threaded=True)

# Decorator ile görev ekleme
@scheduler.every("10s")
def another_task():
    print("Başka bir görev!")

# Zamanlayıcı bilgilerini görüntüle
print(f"Toplam görev sayısı: {len(scheduler)}")
for job in scheduler.get_jobs():
    print(f"Görev: {job}")

# Zamanlayıcıyı başlat
scheduler.run_forever()
```

## ⏰ Desteklenen Zaman Formatları

| Format | Açıklama | Örnek |
|--------|----------|-------|
| `s`, `sec`, `second`, `seconds` | Saniye | `"30s"`, `"5seconds"` |
| `m`, `min`, `minute`, `minutes` | Dakika | `"5m"`, `"2minutes"` |
| `h`, `hour`, `hours` | Saat | `"2h"`, `"1hour"` |
| `d`, `day`, `days` | Gün | `"1d"`, `"3days"` |
| `w`, `week`, `weeks` | Hafta | `"1w"`, `"2weeks"` |

### Ondalık Değerler

```python
@schedule.every("30.5s")  # 30.5 saniye
@schedule.every("1.5m")   # 1.5 dakika (90 saniye)
@schedule.every("0.5h")   # 30 dakika
```

## 🛠️ API Referansı

### Decorator API

```python
import py_schedulerx as schedule

@schedule.every(interval, threaded=False)
def my_function():
    pass
```

### Scheduler Sınıfı

```python
from py_schedulerx import Scheduler

scheduler = Scheduler()

# Görev ekleme
scheduler.add_job(func, interval, threaded=False)

# Görev kaldırma
scheduler.remove_job(func)

# Tüm görevleri temizleme
scheduler.clear_jobs()

# Bekleyen görevleri çalıştırma
scheduler.run_pending()

# Sonsuz döngü başlatma
scheduler.run_forever(sleep_interval=1.0)

# Zamanlayıcıyı durdurma
scheduler.stop()

# Görev listesi alma
jobs = scheduler.get_jobs()

# Sonraki çalışma zamanı
next_time = scheduler.next_run_time()
```

### Yardımcı Fonksiyonlar

```python
from py_schedulerx import format_duration, validate_interval

# Süreyi formatla
formatted = format_duration(3661)  # "1.0h"

# Interval formatını doğrula
is_valid = validate_interval("30s")  # True
```

## 🧪 Test Çalıştırma

```bash
# Temel testler
python -m unittest discover tests

# Coverage ile
pip install coverage
coverage run -m unittest discover tests
coverage report
```

## 📝 Örnek Kullanım Senaryoları

### 1. Web Scraping

```python
import py_schedulerx as schedule
import requests

@schedule.every("1h", threaded=True)
def scrape_news():
    response = requests.get("https://api.example.com/news")
    # Veri işleme...
    print("Haberler güncellendi")

schedule.run_forever()
```

### 2. Sistem Monitoring

```python
import py_schedulerx as schedule
import psutil

@schedule.every("30s")
def check_system():
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    print(f"CPU: {cpu}%, RAM: {memory}%")

@schedule.every("5m", threaded=True)
def cleanup_temp():
    # Geçici dosyaları temizle
    print("Temp dosyalar temizlendi")

schedule.run_forever()
```

### 3. Veritabanı Bakımı

```python
import py_schedulerx as schedule

@schedule.every("1d", threaded=True)
def backup_database():
    # Veritabanı yedekleme
    print("Veritabanı yedeklendi")

@schedule.every("1w", threaded=True)
def optimize_database():
    # Veritabanı optimizasyonu
    print("Veritabanı optimize edildi")

schedule.run_forever()
```

## 🤝 Katkıda Bulunma

1. Bu repo'yu fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 🆚 Diğer Kütüphanelerle Karşılaştırma

| Özellik | py-schedulerx | schedule | APScheduler |
|---------|---------------|----------|-------------|
| Sıfır bağımlılık | ✅ | ✅ | ❌ |
| Threading desteği | ✅ | ❌ | ✅ |
| Sade API | ✅ | ✅ | ❌ |
| Hafif | ✅ | ✅ | ❌ |
| Human-readable format | ✅ | ✅ | ❌ |

## 💡 İpuçları

- **Threading kullanımı**: Uzun süren görevler için `threaded=True` kullanın
- **Hata yönetimi**: Görevlerinizde try-catch blokları kullanın
- **Performans**: Çok sık çalışan görevler için düşük `sleep_interval` değeri kullanın
- **Debugging**: Görev durumlarını kontrol etmek için `scheduler.get_jobs()` kullanın

---

**py-schedulerx** ile periyodik görevlerinizi kolayca yönetin! 🚀
