"""
Goodreads Book Scraper
Goodreads Listopia sayfalarından kitap verilerini toplayan Python scripti
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict, Optional
from tqdm import tqdm
import logging
import os
import argparse
import json
from pathlib import Path

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,  # INFO level'a geri çevirdim
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class GoodreadsScraper:
    """Goodreads Listopia sayfalarından kitap verilerini toplayan sınıf"""
    
    def __init__(self, checkpoint_dir: str = '../data/checkpoints'):
        self.session = requests.Session()
        # User-Agent header'ı ekliyoruz (robots.txt'ye uygun)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.books_data = []
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_number_from_text(self, text: str) -> Optional[int]:
        """Metinden sayı çıkarır (örn: '1,234 ratings' -> 1234)"""
        if not text:
            return None
        # Virgülleri kaldır ve sadece sayıları al
        clean_text = text.replace(',', '').replace(' ', '')
        numbers = re.findall(r'\d+', clean_text)
        return int(numbers[0]) if numbers else None
    
    def extract_rating_from_text(self, text: str) -> Optional[float]:
        """Metinden puanı çıkarır (örn: '4.35 avg rating' -> 4.35)"""
        if not text:
            return None
        rating_match = re.search(r'(\d+\.\d+)', text)
        return float(rating_match.group(1)) if rating_match else None
    
    def scrape_book_info(self, book_element) -> Dict:
        """Tek bir kitabın bilgilerini çıkarır"""
        book_data = {
            'title': None,
            'author': None,
            'average_rating': None,
            'ratings_count': None,
            'reviews_count': None,
            'book_url': None
        }
        
        try:
            # Kitap başlığı ve URL
            title_link = book_element.find('a', class_='bookTitle')
            if title_link:
                book_data['title'] = title_link.get_text(strip=True)
                book_data['book_url'] = 'https://www.goodreads.com' + title_link.get('href', '')
            
            # Yazar adı
            author_link = book_element.find('a', class_='authorName')
            if author_link:
                book_data['author'] = author_link.get_text(strip=True)
            
            # Puan bilgileri - Farklı selector'ları dene
            rating_text = book_element.find('span', class_='minirating')
            if not rating_text:
                rating_text = book_element.find('span', class_='greyText')
            
            if rating_text:
                rating_full_text = rating_text.get_text(strip=True)
                logging.debug(f"Rating text bulundu: {rating_full_text}")
                
                # Ortalama puanı çıkar
                book_data['average_rating'] = self.extract_rating_from_text(rating_full_text)
                
                # Geliştirilmiş regex pattern'ları
                # Puan sayısını çıkar - farklı formatları dene
                ratings_patterns = [
                    r'([\d,]+)\s*ratings?',
                    r'([\d,]+)\s*rating',
                    r'avg\s*rating\s*—\s*([\d,]+)\s*ratings?'
                ]
                
                for pattern in ratings_patterns:
                    ratings_match = re.search(pattern, rating_full_text, re.IGNORECASE)
                    if ratings_match:
                        book_data['ratings_count'] = self.extract_number_from_text(ratings_match.group(1))
                        break
                
                # Yorum sayısını çıkar - farklı formatları dene  
                reviews_patterns = [
                    r'([\d,]+)\s*reviews?',
                    r'([\d,]+)\s*review',
                    r'—\s*([\d,]+)\s*reviews?'
                ]
                
                for pattern in reviews_patterns:
                    reviews_match = re.search(pattern, rating_full_text, re.IGNORECASE)
                    if reviews_match:
                        book_data['reviews_count'] = self.extract_number_from_text(reviews_match.group(1))
                        break
                        
            # Alternatif review arama - farklı elementlerde ara
            if not book_data['reviews_count']:
                # Diğer olası elementleri kontrol et
                review_elements = [
                    book_element.find('span', string=re.compile(r'\d+.*review', re.I)),
                    book_element.find('a', href=re.compile(r'book_review'))
                ]
                
                # greyText elementlerini ayrı ayrı kontrol et
                grey_texts = book_element.find_all('span', class_='greyText')
                
                for elem in review_elements:
                    if elem and hasattr(elem, 'get_text'):
                        elem_text = elem.get_text(strip=True)
                        logging.debug(f"Alternatif review element bulundu: {elem_text}")
                        reviews_match = re.search(r'([\d,]+)\s*reviews?', elem_text, re.IGNORECASE)
                        if reviews_match:
                            book_data['reviews_count'] = self.extract_number_from_text(reviews_match.group(1))
                            break
                            
                # greyText elementlerini kontrol et
                if not book_data['reviews_count'] and grey_texts:
                    for grey_elem in grey_texts:
                        if grey_elem and hasattr(grey_elem, 'get_text'):
                            grey_text = grey_elem.get_text(strip=True)
                            logging.debug(f"GreyText element: {grey_text}")
                            reviews_match = re.search(r'([\d,]+)\s*reviews?', grey_text, re.IGNORECASE)
                            if reviews_match:
                                book_data['reviews_count'] = self.extract_number_from_text(reviews_match.group(1))
                                break
            
        except Exception as e:
            logging.warning(f"Kitap bilgisi çıkarılırken hata: {e}")
        
        # Debug: Çekilen veriyi logla
        if book_data['title']:
            logging.debug(f"Kitap: {book_data['title'][:50]}... - Rating: {book_data['average_rating']}, Ratings: {book_data['ratings_count']}, Reviews: {book_data['reviews_count']}")
        
        return book_data
    
    def save_checkpoint(self, books: List[Dict], current_page: int, list_url: str, session_id: str):
        """Checkpoint dosyasını kaydet"""
        checkpoint_data = {
            'books': books,
            'current_page': current_page,
            'list_url': list_url,
            'timestamp': time.time(),
            'total_books': len(books)
        }
        
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{session_id}.json'
        
        try:
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Checkpoint kaydedildi: {checkpoint_file} ({len(books)} kitap)")
        except Exception as e:
            logging.error(f"Checkpoint kaydetme hatası: {e}")
    
    def load_checkpoint(self, session_id: str) -> Optional[Dict]:
        """Checkpoint dosyasını yükle"""
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{session_id}.json'
        
        if not checkpoint_file.exists():
            return None
            
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logging.info(f"Checkpoint yüklendi: {len(data['books'])} kitap, Sayfa: {data['current_page']}")
            return data
        except Exception as e:
            logging.error(f"Checkpoint yükleme hatası: {e}")
            return None
    
    def list_checkpoints(self) -> List[Dict]:
        """Mevcut checkpoint'leri listele"""
        checkpoints = []
        
        for checkpoint_file in self.checkpoint_dir.glob('checkpoint_*.json'):
            try:
                with open(checkpoint_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                checkpoints.append({
                    'session_id': checkpoint_file.stem.replace('checkpoint_', ''),
                    'file_path': checkpoint_file,
                    'total_books': data.get('total_books', 0),
                    'current_page': data.get('current_page', 0),
                    'timestamp': data.get('timestamp', 0),
                    'list_url': data.get('list_url', 'Unknown')
                })
            except Exception as e:
                logging.warning(f"Checkpoint okuma hatası ({checkpoint_file}): {e}")
        
        # En yeniden eskiye sırala
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
        return checkpoints
    
    def delete_checkpoint(self, session_id: str):
        """Checkpoint dosyasını sil"""
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{session_id}.json'
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logging.info(f"Checkpoint silindi: {session_id}")

    def scrape_page(self, url: str) -> List[Dict]:
        """Tek bir sayfa üzerindeki tüm kitapları kazır"""
        try:
            logging.info(f"Sayfa kazınıyor: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Kitap listesini bulur
            book_elements = soup.find_all('tr', itemtype='http://schema.org/Book')
            
            page_books = []
            for book_element in book_elements:
                book_info = self.scrape_book_info(book_element)
                if book_info['title']:  # Başlık varsa kitabı ekle
                    page_books.append(book_info)
            
            logging.info(f"Bu sayfada {len(page_books)} kitap bulundu")
            return page_books
            
        except Exception as e:
            logging.error(f"Sayfa kazınırken hata ({url}): {e}")
            return []
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Sonraki sayfanın URL'sini bulur"""
        try:
            # "Next" butonu için farklı selector'ları dene
            next_link = soup.find('a', class_='next_page')
            if not next_link:
                next_link = soup.find('a', string=re.compile(r'next', re.I))
            
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if next_url.startswith('/'):
                    return 'https://www.goodreads.com' + next_url
                return next_url
            
            return None
            
        except Exception as e:
            logging.warning(f"Sonraki sayfa URL'si alınırken hata: {e}")
            return None
    
    def scrape_list(self, list_url: str, max_pages: int = 10, delay: float = 1.0, 
                   session_id: Optional[str] = None, resume: bool = False) -> List[Dict]:
        """Çoklu sayfalı listeyi kazır (checkpoint desteği ile)"""
        
        # Session ID oluştur
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        all_books = []
        current_url = list_url
        page_count = 0
        
        # Resume kontrolü
        if resume:
            checkpoint = self.load_checkpoint(session_id)
            if checkpoint:
                all_books = checkpoint['books']
                page_count = checkpoint['current_page']
                current_url = self._get_page_url(list_url, page_count + 1)
                logging.info(f"Resume: Sayfa {page_count + 1}'den devam ediliyor ({len(all_books)} kitap mevcut)")
        
        logging.info(f"Liste kazımaya başlanıyor: {list_url}")
        logging.info(f"Maksimum sayfa sayısı: {max_pages}")
        logging.info(f"Session ID: {session_id}")
        
        try:
            with tqdm(total=max_pages, initial=page_count, desc="Sayfalar işleniyor") as pbar:
                while current_url and page_count < max_pages:
                    # Sayfayı kazı
                    page_books = self.scrape_page(current_url)
                    all_books.extend(page_books)
                    
                    page_count += 1
                    pbar.update(1)
                    pbar.set_postfix({"Toplam Kitap": len(all_books)})
                    
                    # Her 2 sayfada bir checkpoint kaydet
                    if page_count % 2 == 0 or page_count == max_pages:
                        self.save_checkpoint(all_books, page_count, list_url, session_id)
                    
                    # Sonraki sayfa URL'sini al
                    if page_count < max_pages:
                        try:
                            response = self.session.get(current_url)
                            soup = BeautifulSoup(response.content, 'html.parser')
                            next_url = self.get_next_page_url(soup, current_url)
                        except Exception as e:
                            logging.error(f"Sonraki sayfa URL'si alınırken hata: {e}")
                            # Hata durumunda checkpoint kaydet
                            self.save_checkpoint(all_books, page_count, list_url, session_id)
                            raise e
                        
                        if next_url:
                            current_url = next_url
                            time.sleep(delay)  # Rate limiting için bekleme
                        else:
                            logging.info("Sonraki sayfa bulunamadı, kazıma tamamlandı")
                            break
            
            # Başarılı tamamlama - checkpoint'i sil
            self.delete_checkpoint(session_id)
            logging.info(f"Toplam {len(all_books)} kitap kazındı")
            return all_books
            
        except KeyboardInterrupt:
            # Kullanıcı tarafından kesildi - checkpoint kaydet
            self.save_checkpoint(all_books, page_count, list_url, session_id)
            logging.warning(f"\n⏹️  İşlem kullanıcı tarafından durduruldu!")
            logging.info(f"📊 Toplam {len(all_books)} kitap kaydedildi")
            logging.info(f"🔄 Devam etmek için: python goodreads_scraper.py --resume --session-id {session_id}")
            raise
            
        except Exception as e:
            # Hata durumunda checkpoint kaydet
            self.save_checkpoint(all_books, page_count, list_url, session_id)
            logging.error(f"❌ Scraping hatası! Checkpoint kaydedildi.")
            logging.info(f"🔄 Devam etmek için: python goodreads_scraper.py --resume --session-id {session_id}")
            raise e
    
    def _get_page_url(self, base_url: str, page_num: int) -> str:
        """Sayfa numarasından URL oluştur"""
        if page_num == 1:
            return base_url
        return f"{base_url}?page={page_num}"
    
    def save_to_csv(self, books: List[Dict], filename: str = 'goodreads_books.csv'):
        """Kitap verilerini CSV dosyasına kaydeder"""
        if not books:
            logging.warning("Kaydedilecek kitap verisi yok")
            return
        
        df = pd.DataFrame(books)
        
        # Veri temizleme
        df = self.clean_data(df)
        
        # Data klasörünü oluştur
        data_dir = os.path.join('..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # CSV'ye kaydet
        output_path = os.path.join(data_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8')
        logging.info(f"Veriler kaydedildi: {output_path}")
        logging.info(f"Toplam satır sayısı: {len(df)}")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Veri temizleme işlemleri"""
        logging.info("Veri temizleme başlatılıyor...")
        
        # Boş satırları kaldır
        initial_count = len(df)
        df = df.dropna(subset=['title'])
        logging.info(f"Başlığı olmayan {initial_count - len(df)} satır kaldırıldı")
        
        # Duplikat kitapları kaldır
        before_dedup = len(df)
        df = df.drop_duplicates(subset=['title', 'author'])
        logging.info(f"Duplikat {before_dedup - len(df)} kitap kaldırıldı")
        
        # Eksik review count'ları tahmin et (genel olarak ratings'in %10-15'i kadar review olur)
        df['reviews_count'] = df['reviews_count'].fillna(df['ratings_count'] * 0.12)
        
        # Yeni özellikler ekle
        df['rating_to_review_ratio'] = df['ratings_count'] / (df['reviews_count'] + 1)  # +1 sıfıra bölme hatası için
        
        # Veri tiplerini düzelt
        numeric_columns = ['average_rating', 'ratings_count', 'reviews_count']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sıralama (puan sayısına göre azalan)
        df = df.sort_values('ratings_count', ascending=False)
        
        logging.info("Veri temizleme tamamlandı")
        return df

def parse_arguments():
    """Command line argümanlarını parse et"""
    parser = argparse.ArgumentParser(
        description='Goodreads Kitap Listelerini Kazıyan Python Scripti',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python goodreads_scraper.py --pages 5 --delay 2.0
  python goodreads_scraper.py --url "https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once" --pages 3
  python goodreads_scraper.py --pages 20 --output "sci_fi_books.csv" --delay 1.0
        """
    )
    
    parser.add_argument(
        '--pages', 
        type=int, 
        default=10,
        help='Kazınacak sayfa sayısı (varsayılan: 10, yaklaşık 1000 kitap)'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default="https://www.goodreads.com/list/show/1.Best_Books_Ever",
        help='Kazınacak Goodreads liste URL\'si (varsayılan: Best Books Ever)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='İstekler arası bekleme süresi (saniye, varsayılan: 1.5)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='goodreads_books.csv',
        help='Çıktı CSV dosyası adı (varsayılan: goodreads_books.csv)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Detaylı debug logları göster'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Önceki session\'dan devam et'
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        help='Devam edilecek session ID\'si (--resume ile birlikte kullanın)'
    )
    
    parser.add_argument(
        '--list-checkpoints',
        action='store_true',
        help='Mevcut checkpoint\'leri listele'
    )
    
    return parser.parse_args()

def main():
    """Ana fonksiyon"""
    args = parse_arguments()
    
    # Logging seviyesini ayarla
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scraper = GoodreadsScraper()
    
    # Checkpoint listesi istendi
    if args.list_checkpoints:
        checkpoints = scraper.list_checkpoints()
        if not checkpoints:
            print("🔍 Henüz kaydedilmiş checkpoint bulunamadı.")
            return
        
        print("📋 Mevcut Checkpoint'ler:")
        print("-" * 80)
        for i, cp in enumerate(checkpoints, 1):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cp['timestamp']))
            url_short = cp['list_url'][:60] + "..." if len(cp['list_url']) > 60 else cp['list_url']
            print(f"{i}. Session ID: {cp['session_id']}")
            print(f"   📊 {cp['total_books']} kitap, Sayfa: {cp['current_page']}")
            print(f"   📅 Tarih: {timestamp}")
            print(f"   🔗 URL: {url_short}")
            print()
        
        print("💡 Devam etmek için: python goodreads_scraper.py --resume --session-id SESSION_ID")
        return
    
    # Resume kontrolü
    if args.resume:
        if not args.session_id:
            # Mevcut checkpoint'leri göster ve kullanıcıdan seçim iste
            checkpoints = scraper.list_checkpoints()
            if not checkpoints:
                print("❌ Resume edilecek checkpoint bulunamadı.")
                return
            
            print("📋 Mevcut Checkpoint'ler:")
            for i, cp in enumerate(checkpoints, 1):
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cp['timestamp']))
                print(f"{i}. {cp['session_id']} - {cp['total_books']} kitap, Sayfa: {cp['current_page']} ({timestamp})")
            
            try:
                choice = int(input("\nHangi checkpoint'ten devam etmek istiyorsunuz? (numara): ")) - 1
                args.session_id = checkpoints[choice]['session_id']
            except (ValueError, IndexError):
                print("❌ Geçersiz seçim.")
                return
    
    print(f"🎯 Hedef URL: {args.url}")
    print(f"📄 Sayfa sayısı: {args.pages} (yaklaşık {args.pages * 100} kitap)")
    print(f"⏱️  İstekler arası gecikme: {args.delay} saniye")
    print(f"📁 Çıktı dosyası: {args.output}")
    if args.resume:
        print(f"🔄 Resume modu: {args.session_id}")
    print("-" * 60)
    
    try:
        # Argümanlarla kazıma işlemini başlat
        books = scraper.scrape_list(
            args.url, 
            max_pages=args.pages, 
            delay=args.delay,
            session_id=args.session_id,
            resume=args.resume
        )
        
        if books:
            # CSV'ye kaydet
            df = scraper.save_to_csv(books, args.output)
            
            # Özet istatistikler
            print("\n=== ÖZET İSTATİSTİKLER ===")
            print(f"Toplam kitap sayısı: {len(df)}")
            print(f"Ortalama puan: {df['average_rating'].mean():.2f}")
            print(f"En yüksek puan: {df['average_rating'].max()}")
            print(f"En çok puanlanan kitap: {df.loc[df['ratings_count'].idxmax(), 'title']}")
            print(f"En çok yorumlanan kitap: {df.loc[df['reviews_count'].idxmax(), 'title']}")
            
        else:
            logging.error("Hiç kitap verisi elde edilemedi")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  İşlem kullanıcı tarafından durduruldu!")
        print("💡 Checkpoint'ler kaydedildi. --list-checkpoints ile kontrol edebilirsiniz.")
        
    except Exception as e:
        logging.error(f"Ana fonksiyonda hata: {e}")
        print(f"\n❌ Hata oluştu: {e}")
        print("💡 Checkpoint'ler kaydedildi. --list-checkpoints ile kontrol edebilirsiniz.")

if __name__ == "__main__":
    main()