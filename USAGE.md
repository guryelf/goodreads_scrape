# 🛠️ Goodreads Scraper - Kullanım Kılavuzu

## 📋 Command Line Parametreleri

### Temel Kullanım
```bash
python goodreads_scraper.py [PARAMETRELER]
```

### Mevcut Parametreler

| Parametre | Açıklama | Varsayılan | Örnek |
|-----------|----------|------------|--------|
| `--pages` | Kazınacak sayfa sayısı | 10 | `--pages 5` |
| `--url` | Goodreads liste URL'si | Best Books Ever | `--url "https://..."` |
| `--delay` | İstekler arası gecikme (saniye) | 1.5 | `--delay 2.0` |
| `--output` | Çıktı CSV dosyası adı | goodreads_books.csv | `--output "my_books.csv"` |
| `--verbose` | Detaylı debug logları | Kapalı | `--verbose` |
| `--resume` | Önceki session'dan devam et | Kapalı | `--resume` |
| `--session-id` | Belirli session ID ile devam et | - | `--session-id session_123` |
| `--list-checkpoints` | Checkpoint'leri listele | - | `--list-checkpoints` |

## 🚀 Kullanım Örnekleri

### 1. Hızlı Test (5 sayfa)
```bash
python goodreads_scraper.py --pages 5
```

### 2. Büyük Veri Seti (20 sayfa)
```bash
python goodreads_scraper.py --pages 20 --delay 2.0 --output "big_dataset.csv"
```

### 3. Farklı Liste (Bilim Kurgu)
```bash
python goodreads_scraper.py \
  --url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books" \
  --pages 15 \
  --output "sci_fi_books.csv"
```

### 4. Debug Modunda
```bash
python goodreads_scraper.py --pages 3 --verbose
```

### 5. Checkpoint'leri Listele
```bash
python goodreads_scraper.py --list-checkpoints
```

### 6. Kesintiden Devam Et
```bash
# Otomatik checkpoint seçimi
python goodreads_scraper.py --resume

# Belirli session'dan devam
python goodreads_scraper.py --resume --session-id session_1727226123
```

### 7. Çok Hızlı Kazıma (Dikkatli Kullanın!)
```bash
python goodreads_scraper.py --pages 10 --delay 0.5
```

## 📊 Popüler Goodreads Listeleri

### En Popüler Listeler
```bash
# En İyi Kitaplar
--url "https://www.goodreads.com/list/show/1.Best_Books_Ever"

# Herkesin Okuması Gereken Kitaplar  
--url "https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once"

# En İyi Bilim Kurgu & Fantasy
--url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books"

# En İyi Gizem & Gerilim
--url "https://www.goodreads.com/list/show/18.Best_Mystery_Thriller_Books"

# En İyi Romantik Kitaplar
--url "https://www.goodreads.com/list/show/8.Best_Romance_Novels"
```

### Türe Göre Listeler
```bash
# Klasik Edebiyat
--url "https://www.goodreads.com/list/show/12.Best_Books_of_the_20th_Century"

# Genç Yetişkin (YA)
--url "https://www.goodreads.com/list/show/43.Best_Young_Adult_Books"

# Non-Fiction
--url "https://www.goodreads.com/list/show/7.Best_Nonfiction"
```

## 💡 İpuçları

### Performans Optimizasyonu
- **Küçük testler için**: `--pages 1-3`
- **Normal kullanım için**: `--pages 10-15` 
- **Büyük veri setleri için**: `--pages 20+`

### Rate Limiting
- **Güvenli**: `--delay 1.5-2.0`
- **Hızlı**: `--delay 1.0` (dikkatli kullanın)
- **Çok hızlı**: `--delay 0.5` (sadece test için)

### Çıktı Dosya İsimleri
- Tarih ekleyin: `--output "books_2025_09_25.csv"`
- Tür belirtin: `--output "fantasy_books.csv"`
- Sayfa sayısı ekleyin: `--output "books_20_pages.csv"`

## � Checkpoint Sistemi

### Checkpoint Nedir?
Scraping sırasında hata oluşursa veya işlem kesilirse, toplanan veriler otomatik olarak kaydedilir. Bu sayede kaldığınız yerden devam edebilirsiniz.

### Checkpoint'ler Ne Zaman Kaydedilir?
- ✅ Her 2 sayfada bir otomatik
- ✅ Hata oluştuğunda
- ✅ İşlem kesildiğinde (Ctrl+C)

### Checkpoint Kullanımı

#### 1. Mevcut Checkpoint'leri Görüntüle
```bash
python goodreads_scraper.py --list-checkpoints
```

#### 2. Kesintiden Sonra Devam Et
```bash
# İnteraktif seçim
python goodreads_scraper.py --resume

# Belirli session ile
python goodreads_scraper.py --resume --session-id session_1727226123
```

#### 3. Checkpoint Örnek Senaryosu
```bash
# 1. Büyük bir scraping başlat
python goodreads_scraper.py --pages 50 --output "big_dataset.csv"

# 2. Hata oluştu! (internet kesildi, vs.)
# Çıktıda şöyle bir mesaj görürsünüz:
# "Checkpoint kaydedildi. Resume için: --resume --session-id session_1727226123"

# 3. Kaldığınız yerden devam edin
python goodreads_scraper.py --resume --session-id session_1727226123
```

### Checkpoint Dosyaları
- 📁 Konum: `data/checkpoints/`
- 📝 Format: JSON (checkpoint_SESSION_ID.json)
- 🗑️ Otomatik silinme: İşlem başarıyla tamamlandığında

## �🔧 Sorun Giderme

### Yaygın Hatalar
```bash
# Dosya bulunamadı
cd src && python goodreads_scraper.py

# Kütüphane eksik
pip install -r requirements.txt

# Permission denied
chmod +x goodreads_scraper.py
```

### Checkpoint Sorunları
```bash
# Bozuk checkpoint temizle
rm -rf ../data/checkpoints/checkpoint_SESSION_ID.json

# Tüm checkpoint'leri temizle
rm -rf ../data/checkpoints/*.json
```

### Debug Modu
Herhangi bir sorun yaşarsanız `--verbose` parametresini kullanın:
```bash
python goodreads_scraper.py --pages 1 --verbose
```

## 📈 Performans Rehberi

| Sayfa Sayısı | Tahmini Süre | Kitap Sayısı | Dosya Boyutu |
|--------------|--------------|--------------|--------------|
| 1 | 10 saniye | ~100 | ~12 KB |
| 5 | 1 dakika | ~500 | ~60 KB |
| 10 | 2-3 dakika | ~1000 | ~120 KB |
| 20 | 5-6 dakika | ~2000 | ~240 KB |
| 50 | 12-15 dakika | ~5000 | ~600 KB |

---

**⚠️ Not**: Goodreads'in kullanım şartlarına saygı gösterin ve aşırı hızlı istek göndermeyin.