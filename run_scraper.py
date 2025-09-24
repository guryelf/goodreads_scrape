#!/usr/bin/env python3
"""
Goodreads Scraper - Hızlı Başlangıç Scripti
Bu script, gerekli kütüphaneleri kontrol eder ve scraper'ı çalıştırır
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Gerekli kütüphanelerin yüklenip yüklenmediğini kontrol eder"""
    required_packages = [
        'requests', 'beautifulsoup4', 'pandas', 'lxml', 'numpy', 'tqdm'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_requirements():
    """Eksik kütüphaneleri yükler"""
    print("🔧 Gerekli kütüphaneler yükleniyor...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Kütüphaneler başarıyla yüklendi!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Kütüphane yükleme hatası: {e}")
        return False

def run_scraper():
    """Ana scraper'ı çalıştırır"""
    print("\n📚 Goodreads scraper başlatılıyor...")
    
    # Kullanıcıdan parametreler al
    pages = input("� Kaç sayfa işlensin? (varsayılan: 10): ").strip()
    if not pages:
        pages = "10"
    
    url = input("🔗 Farklı liste URL'si? (Enter = Best Books Ever): ").strip()
    if not url:
        url = "https://www.goodreads.com/list/show/1.Best_Books_Ever"
    
    delay = input("⏱️  İstekler arası gecikme (saniye, varsayılan: 1.5): ").strip()
    if not delay:
        delay = "1.5"
    
    output = input("� Çıktı dosyası adı (varsayılan: goodreads_books.csv): ").strip()
    if not output:
        output = "goodreads_books.csv"
    
    print(f"\n🎯 Hedef: {url}")
    print(f"📄 {pages} sayfa (yaklaşık {int(pages) * 100} kitap) işlenecek...")
    print(f"⏱️  Bu işlem {int(pages) * 0.5}-{int(pages)} dakika sürebilir...\n")
    
    try:
        # src klasörüne geç
        original_dir = os.getcwd()
        os.chdir('src')
        
        # Scraper'ı argümanlarla çalıştır
        command = [
            sys.executable, "goodreads_scraper.py",
            "--pages", pages,
            "--url", url,
            "--delay", delay,
            "--output", output
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Orijinal klasöre geri dön
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✅ Scraping başarıyla tamamlandı!")
            print(f"📊 Çıktı: {result.stdout}")
            
            # Veri dosyası oluştu mu kontrol et
            data_file = Path(f'data/{output}')
            if data_file.exists():
                print(f"\n📁 Veri dosyası oluşturuldu: {data_file}")
                print(f"📏 Dosya boyutu: {data_file.stat().st_size / 1024:.1f} KB")
            
        else:
            print("❌ Scraping sırasında hata oluştu:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Script çalıştırma hatası: {e}")
        os.chdir(original_dir)

def show_project_info():
    """Proje bilgilerini gösterir"""
    print("="*60)
    print("📚 GOODREADS WEB SCRAPER PROJESİ")
    print("="*60)
    print("🎯 Amaç: Goodreads'ten en popüler kitapları toplamak")
    print("📊 Hedef: ~1000 kitap verisi")
    print("🔧 Teknoloji: Python + BeautifulSoup + Pandas")
    print("📁 Klasör yapısı:")
    print("   ├── src/                 # Python kodları")
    print("   ├── data/                # Toplanan veriler")
    print("   ├── requirements.txt     # Gerekli kütüphaneler")
    print("   └── README.md           # Dokümantasyon")
    print("="*60)

def main():
    """Ana fonksiyon"""
    show_project_info()
    
    # Gerekli kütüphaneleri kontrol et
    missing = check_requirements()
    
    if missing:
        print(f"\n⚠️  Eksik kütüphaneler tespit edildi: {', '.join(missing)}")
        
        install_choice = input("\n🤔 Eksik kütüphaneleri yüklemek ister misiniz? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes', 'e', 'evet']:
            if not install_requirements():
                print("❌ Kurulum başarısız. Manuel olarak 'pip install -r requirements.txt' çalıştırın.")
                return
        else:
            print("❌ Gerekli kütüphaneler olmadan scraper çalışmaz.")
            print("💡 Yükleme komutu: pip install -r requirements.txt")
            return
    
    else:
        print("\n✅ Tüm gerekli kütüphaneler yüklü!")
    
    # Scraper'ı çalıştır
    run_choice = input("\n🚀 Scraper'ı başlatmak ister misiniz? (y/n): ").lower().strip()
    
    if run_choice in ['y', 'yes', 'e', 'evet']:
        run_scraper()
        
        # Analiz önerisi
        print("\n💡 İPUCU: Toplanan veriyi analiz etmek için:")
        print("   cd src && python analyze_data.py")
        
    else:
        print("👋 İyi günler! Hazır olduğunuzda tekrar çalıştırın.")

if __name__ == "__main__":
    main()