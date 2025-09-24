# 📚 Goodreads En Popüler Kitaplar Veri Seti - Web Scraping Projesi

Bu proje, **Goodreads.com**'dan "Best Books Ever" listesindeki en popüler kitapların bilgilerini otomatik olarak toplayan bir Python web scraping uygulamasıdır. Kitap okurları, yazarlar ve veri analisti adayları için zengin bir veri seti oluşturur.

## 🎯 Proje Amacı

Goodreads'in "Best Books Ever" listesinden şu bilgileri toplayarak temizlenmiş bir veri seti oluşturmak:
- 📖 Kitap Adı 
- ✍️ Yazar Adı
- ⭐ Ortalama Puan
- 📊 Toplam Puan Sayısı
- 💬 Yorum Sayısı
- 🔗 Kitap URL'si
- 📈 Puan/Yorum Oranı (yeni özellik)

## 🛠️ Teknik Özellikler

### Kullanılan Teknolojiler
- **Python 3.8+**
- **requests**: HTTP istekleri için
- **BeautifulSoup4**: HTML parsing için
- **pandas**: Veri işleme ve analiz
- **tqdm**: Progress bar
- **lxml**: XML/HTML parser

### Scraping Özellikleri
- ✅ **Çoklu sayfa gezinme** (pagination)
- ✅ **Rate limiting** (istekler arası 1.5 saniye bekleme)
- ✅ **Hata yakalama ve logging**
- ✅ **robots.txt uyumlu** işlemler
- ✅ **Veri temizleme** ve doğrulama
- ✅ **Progress tracking** (tqdm ile)
- ✅ **Checkpoint sistemi** (kesintiden sonra devam etme)
- ✅ **Resume özelliği** (kaldığınız yerden başlayın)

## 📁 Proje Yapısı

```
goodreads-scraper/
│
├── src/
│   └── goodreads_scraper.py    # Ana scraper kodu
│
├── data/
│   └── goodreads_top_1000_books.csv    # Toplanan veri seti
│
├── requirements.txt            # Python bağımlılıkları
├── README.md                  # Bu dokümantasyon
└── scraper.log               # Çalışma logları
```

## 🚀 Kurulum ve Kullanım

### 1. Projeyi İndirin
```bash
git clone <repository-url>
cd goodreads-scraper
```

### 2. Virtual Environment Oluşturun (Önerilen)
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# veya
venv\Scripts\activate     # Windows
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Scraper'ı Çalıştırın

#### Hızlı Başlangıç (Interaktif)
```bash
python run_scraper.py
```

#### Command Line ile
```bash
cd src
python goodreads_scraper.py --pages 10 --delay 1.5
```

#### Farklı Liste ile
```bash
cd src
python goodreads_scraper.py \
  --url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books" \
  --pages 15 \
  --output "sci_fi_books.csv"
```

## ⚙️ Konfigürasyon

### Command Line Parametreleri

| Parametre | Açıklama | Varsayılan | Örnek |
|-----------|----------|------------|--------|
| `--pages` | Kazınacak sayfa sayısı | 10 | `--pages 5` |
| `--url` | Goodreads liste URL'si | Best Books Ever | `--url "https://..."` |
| `--delay` | İstekler arası gecikme | 1.5s | `--delay 2.0` |
| `--output` | Çıktı dosyası adı | goodreads_books.csv | `--output "my_books.csv"` |
| `--verbose` | Detaylı loglar | Kapalı | `--verbose` |

### Örnekler
```bash
# Hızlı test (5 sayfa)
python goodreads_scraper.py --pages 5

# Büyük veri seti (20 sayfa, yavaş)  
python goodreads_scraper.py --pages 20 --delay 2.0

# Bilim kurgu kitapları
python goodreads_scraper.py \
  --url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books" \
  --pages 10 \
  --output "sci_fi_books.csv"
```

### Resume/Checkpoint Sistemi
```bash
# Mevcut checkpoint'leri görüntüle
python goodreads_scraper.py --list-checkpoints

# Kesintiden sonra devam et
python goodreads_scraper.py --resume

# Belirli session'dan devam et
python goodreads_scraper.py --resume --session-id session_12345
```

📖 **Detaylı kullanım için**: [USAGE.md](USAGE.md) dosyasına bakın.

## 📊 Veri Temizleme Süreci

Script otomatik olarak şu temizleme işlemlerini yapar:

1. **Eksik Başlık Kontrolü**: Başlığı olmayan kitapları kaldırır
2. **Duplikat Temizleme**: Aynı kitap-yazar kombinasyonlarını kaldırır
3. **Veri Tipi Dönüşümü**: Sayısal verileri int/float'a çevirir
4. **Yeni Özellik Üretme**: Puan/Yorum oranı hesaplar
5. **Sıralama**: Kitapları puan sayısına göre sıralar

## 📈 Çıktı Formatı

CSV dosyası şu kolonları içerir:

| Kolon | Açıklama | Örnek |
|-------|----------|--------|
| `title` | Kitap başlığı | "To Kill a Mockingbird" |
| `author` | Yazar adı | "Harper Lee" |
| `average_rating` | Ortalama puan | 4.27 |
| `ratings_count` | Toplam puan sayısı | 5234567 |
| `reviews_count` | Yorum sayısı | 234567 |
| `book_url` | Goodreads kitap linki | "https://www.goodreads.com/book/..." |
| `rating_to_review_ratio` | Puan/Yorum oranı | 22.3 |

## 🚦 Rate Limiting ve Etik Kullanım

Bu proje Goodreads'in robots.txt dosyasına uygun şekilde tasarlanmıştır:

- ✅ Listopia sayfaları (`/list/show/`) robots.txt'de yasaklanmamış
- ⏱️ İstekler arası 1.5 saniye bekleme süresi
- 📝 Respectful User-Agent kullanımı
- 🔍 Sadece halka açık listeleri hedefleme

## 🔧 Karşılaşılan Zorluklar ve Çözümler

### 1. **Pagination Problemi**
**Problem**: Goodreads'in "Next" butonunu bulmak
**Çözüm**: Çoklu CSS selector deneme ve regex kullanımı

### 2. **Veri Formatı Tutarsızlıkları**  
**Problem**: "1,234,567 ratings" formatındaki metinlerden sayı çıkarma
**Çözüm**: Regex pattern'ları ve string temizleme fonksiyonları

### 3. **Request Blocking**
**Problem**: Çok hızlı istek gönderme
**Çözüm**: Rate limiting ve uygun User-Agent kullanımı

## 📋 Örnek Kullanım Senaryoları

1. **Kitap Önerisi Algoritması**: En yüksek puan/yorum oranına sahip kitapları bulma
2. **Yazar Analizi**: En popüler yazarları belirleme  
3. **Trend Analizi**: Puan dağılımlarını inceleme
4. **Veri Görselleştirme**: Matplotlib/Seaborn ile grafik oluşturma

## 🤝 Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## ⚠️ Yasal Uyarılar

- Bu proje yalnızca eğitim amaçlıdır
- Goodreads'in kullanım şartlarına ve robots.txt dosyasına saygı gösterir
- Veriler kişisel kullanım içindir, ticari amaçlarla kullanılmamalıdır
- Web scraping yaparken her zaman hedef sitenin kurallarını kontrol edin

## 📞 İletişim

Herhangi bir soru veya öneri için lütfen issue açın.

---

**⭐ Bu proje size yardımcı olduysa, repository'yi yıldızlamayı unutmayın!**