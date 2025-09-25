"""
Goodreads Book Scraper
Python script for collecting book data from Goodreads Listopia pages
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

# Logging configuration
logging.basicConfig(
    level=logging.INFO,  # Reverted to INFO level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

class GoodreadsScraper:
    """Class for collecting book data from Goodreads Listopia pages"""
    
    def __init__(self, delay=1.5):
        self.delay = delay
        self.books = []
        self.session = requests.Session()
        
        # Initialize checkpoint directory
        self.checkpoint_dir = Path('../data/checkpoints')
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Respectful User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Logging configuration
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def extract_number_from_text(self, text: str) -> Optional[int]:
        """Extracts number from text (e.g.: '1,234 ratings' -> 1234)"""
        if not text:
            return None
        # Remove commas and get only numbers
        clean_text = text.replace(',', '').replace(' ', '')
        numbers = re.findall(r'\d+', clean_text)
        return int(numbers[0]) if numbers else None
    
    def extract_rating_from_text(self, text: str) -> Optional[float]:
        """Extracts rating from text (e.g.: '4.35 avg rating' -> 4.35)"""
        if not text:
            return None
        rating_match = re.search(r'(\d+\.\d+)', text)
        return float(rating_match.group(1)) if rating_match else None
    
    def scrape_book_info(self, book_element) -> Dict:
        """Extracts information for a single book"""
        book_data = {
            'title': None,
            'author': None,
            'average_rating': None,
            'ratings_count': None,
            'reviews_count': None,
            'book_url': None
        }
        
        try:
            # Book title and URL
            title_link = book_element.find('a', class_='bookTitle')
            if title_link:
                book_data['title'] = title_link.get_text(strip=True)
                book_data['book_url'] = 'https://www.goodreads.com' + title_link.get('href', '')
            
            # Author name
            author_link = book_element.find('a', class_='authorName')
            if author_link:
                book_data['author'] = author_link.get_text(strip=True)
            
            # Rating information - Try different selectors
            rating_text = book_element.find('span', class_='minirating')
            if not rating_text:
                rating_text = book_element.find('span', class_='greyText')
            
            if rating_text:
                rating_full_text = rating_text.get_text(strip=True)
                logging.debug(f"Rating text found: {rating_full_text}")
                
                # Extract average rating
                book_data['average_rating'] = self.extract_rating_from_text(rating_full_text)
                
                # Enhanced regex patterns
                # Extract rating count - try different formats
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
                
                # Extract review count - try different formats  
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
                        
            # Alternative review search - search in different elements
            if not book_data['reviews_count']:
                # Check other possible elements
                review_elements = [
                    book_element.find('span', string=re.compile(r'\d+.*review', re.I)),
                    book_element.find('a', href=re.compile(r'book_review'))
                ]
                
                # Check greyText elements separately
                grey_texts = book_element.find_all('span', class_='greyText')
                
                for elem in review_elements:
                    if elem and hasattr(elem, 'get_text'):
                        elem_text = elem.get_text(strip=True)
                        logging.debug(f"Alternative review element found: {elem_text}")
                        reviews_match = re.search(r'([\d,]+)\s*reviews?', elem_text, re.IGNORECASE)
                        if reviews_match:
                            book_data['reviews_count'] = self.extract_number_from_text(reviews_match.group(1))
                            break
                            
                # Check greyText elements
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
            logging.warning(f"Error extracting book information: {e}")
        
        # Debug: Log extracted data
        if book_data['title']:
            logging.debug(f"Book: {book_data['title'][:50]}... - Rating: {book_data['average_rating']}, Ratings: {book_data['ratings_count']}, Reviews: {book_data['reviews_count']}")
        
        return book_data
    
    def save_checkpoint(self, books: List[Dict], current_page: int, list_url: str, session_id: str):
        """Save checkpoint file"""
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
            logging.info(f"Checkpoint saved: {checkpoint_file} ({len(books)} books)")
        except Exception as e:
            logging.error(f"Checkpoint save error: {e}")
    
    def load_checkpoint(self, session_id: str) -> Optional[Dict]:
        """Load checkpoint file"""
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{session_id}.json'
        
        if not checkpoint_file.exists():
            return None
            
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logging.info(f"Checkpoint loaded: {len(data['books'])} books, Page: {data['current_page']}")
            return data
        except Exception as e:
            logging.error(f"Checkpoint loading error: {e}")
            return None
    
    def list_checkpoints(self) -> List[Dict]:
        """List existing checkpoints"""
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
                logging.warning(f"Checkpoint read error ({checkpoint_file}): {e}")
        
        # Sort from newest to oldest
        checkpoints.sort(key=lambda x: x['timestamp'], reverse=True)
        return checkpoints
    
    def delete_checkpoint(self, session_id: str):
        """Delete checkpoint file"""
        checkpoint_file = self.checkpoint_dir / f'checkpoint_{session_id}.json'
        if checkpoint_file.exists():
            checkpoint_file.unlink()
            logging.info(f"Checkpoint deleted: {session_id}")

    def scrape_page(self, url: str) -> List[Dict]:
        """Scrape all books on a single page"""
        try:
            logging.info(f"Scraping page: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the book list
            book_elements = soup.find_all('tr', itemtype='http://schema.org/Book')
            
            page_books = []
            for book_element in book_elements:
                book_info = self.scrape_book_info(book_element)
                if book_info['title']:  # Add book if title exists
                    page_books.append(book_info)
            
            logging.info(f"Found {len(page_books)} books on this page")
            return page_books
            
        except Exception as e:
            logging.error(f"Error scraping page ({url}): {e}")
            return []
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """Find the URL of the next page"""
        try:
            # Try different selectors for "Next" button
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
            logging.warning(f"Error getting next page URL: {e}")
            return None
    
    def scrape_list(self, list_url: str, max_pages: int = 10, delay: float = 1.0, 
                   session_id: Optional[str] = None, resume: bool = False) -> List[Dict]:
        """Scrape multi-page list (with checkpoint support)"""
        
        # Create Session ID
        if not session_id:
            session_id = f"session_{int(time.time())}"
        
        all_books = []
        current_url = list_url
        page_count = 0
        
        # Resume check
        if resume:
            checkpoint = self.load_checkpoint(session_id)
            if checkpoint:
                all_books = checkpoint['books']
                page_count = checkpoint['current_page']
                current_url = self._get_page_url(list_url, page_count + 1)
                logging.info(f"Resume: Sayfa {page_count + 1}'den devam ediliyor ({len(all_books)} kitap mevcut)")
        
        logging.info(f"Starting list scraping: {list_url}")
        logging.info(f"Maximum pages: {max_pages}")
        logging.info(f"Session ID: {session_id}")
        
        try:
            with tqdm(total=max_pages, initial=page_count, desc="Processing pages") as pbar:
                while current_url and page_count < max_pages:
                    # Scrape the page
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
                            logging.error(f"Error getting next page URL: {e}")
                            # Hata durumunda checkpoint kaydet
                            self.save_checkpoint(all_books, page_count, list_url, session_id)
                            raise e
                        
                        if next_url:
                            current_url = next_url
                            time.sleep(delay)  # Wait for rate limiting
                        else:
                            logging.info("Next page not found, scraping completed")
                            break
            
            # Successful completion - delete checkpoint
            self.delete_checkpoint(session_id)
            logging.info(f"Total {len(all_books)} books scraped")
            return all_books
            
        except KeyboardInterrupt:
            # Interrupted by user - save checkpoint
            self.save_checkpoint(all_books, page_count, list_url, session_id)
            logging.warning(f"\n⏹️  Operation stopped by user!")
            logging.info(f"📊 Total {len(all_books)} books saved")
            logging.info(f"🔄 To resume: python goodreads_scraper.py --resume --session-id {session_id}")
            raise
            
        except Exception as e:
            # Hata durumunda checkpoint kaydet
            self.save_checkpoint(all_books, page_count, list_url, session_id)
            logging.error(f"❌ Scraping error! Checkpoint saved.")
            logging.info(f"🔄 To resume: python goodreads_scraper.py --resume --session-id {session_id}")
            raise e
    
    def _get_page_url(self, base_url: str, page_num: int) -> str:
        """Generate URL from page number"""
        if page_num == 1:
            return base_url
        return f"{base_url}?page={page_num}"
    
    def save_to_csv(self, books: List[Dict], filename: str = 'goodreads_books.csv'):
        """Save book data to CSV file"""
        if not books:
            logging.warning("Kaydedilecek kitap verisi yok")
            return
        
        df = pd.DataFrame(books)
        
        # Veri temizleme
        df = self.clean_data(df)
        
        # Create data folder
        data_dir = "../data"
        os.makedirs(data_dir, exist_ok=True)
        
        # Save to CSV
        output_path = os.path.join(data_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8')
        logging.info(f"Data saved: {output_path}")
        logging.info(f"Total rows: {len(df)}")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Data cleaning operations"""
        logging.info("Starting data cleaning...")
        
        # Remove empty rows
        initial_count = len(df)
        df = df.dropna(subset=['title'])
        logging.info(f"Removed {initial_count - len(df)} rows without titles")
        
        # Remove duplicate books
        before_dedup = len(df)
        df = df.drop_duplicates(subset=['title', 'author'])
        logging.info(f"Removed {before_dedup - len(df)} duplicate books")
        
        # Estimate missing review counts (generally reviews are about 10-15% of ratings)
        df['reviews_count'] = df['reviews_count'].fillna(df['ratings_count'] * 0.12)
        
        # Add new features
        df['rating_to_review_ratio'] = df['ratings_count'] / (df['reviews_count'] + 1)  # +1 to avoid division by zero
        
        # Fix data types
        numeric_columns = ['average_rating', 'ratings_count', 'reviews_count']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Sort (descending by rating count)
        df = df.sort_values('ratings_count', ascending=False)
        
        logging.info("Data cleaning completed")
        return df

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Python Script for Scraping Goodreads Book Lists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python goodreads_scraper.py --pages 5 --delay 2.0
  python goodreads_scraper.py --url "https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once" --pages 3
  python goodreads_scraper.py --pages 20 --output "sci_fi_books.csv" --delay 1.0
        """
    )
    
    parser.add_argument(
        '--pages', 
        type=int, 
        default=10,
        help='Number of pages to scrape (default: 10, approximately 1000 books)'
    )
    
    parser.add_argument(
        '--url',
        type=str,
        default="https://www.goodreads.com/list/show/1.Best_Books_Ever",
        help='Goodreads list URL to scrape (default: Best Books Ever)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.5,
        help='Delay between requests (seconds, default: 1.5)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='goodreads_books.csv',
        help='Output CSV file name (default: goodreads_books.csv)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed debug logs'
    )
    
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from previous session'
    )
    
    parser.add_argument(
        '--session-id',
        type=str,
        help='Session ID to resume from (use with --resume)'
    )
    
    parser.add_argument(
        '--list-checkpoints',
        action='store_true',
        help='List existing checkpoints'
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_arguments()
    
    # Logging seviyesini ayarla
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    scraper = GoodreadsScraper()
    
    # Checkpoint listesi istendi
    if args.list_checkpoints:
        checkpoints = scraper.list_checkpoints()
        if not checkpoints:
            print("🔍 No saved checkpoints found yet.")
            return
        
        print("📋 Existing Checkpoints:")
        print("-" * 80)
        for i, cp in enumerate(checkpoints, 1):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cp['timestamp']))
            url_short = cp['list_url'][:60] + "..." if len(cp['list_url']) > 60 else cp['list_url']
            print(f"{i}. Session ID: {cp['session_id']}")
            print(f"   📊 {cp['total_books']} kitap, Sayfa: {cp['current_page']}")
            print(f"   📅 Tarih: {timestamp}")
            print(f"   🔗 URL: {url_short}")
            print()
        
        print("💡 To resume: python goodreads_scraper.py --resume --session-id SESSION_ID")
        return
    
    # Resume check
    if args.resume:
        if not args.session_id:
            # Show available checkpoints and ask user to select
            checkpoints = scraper.list_checkpoints()
            if not checkpoints:
                print("❌ No checkpoint found to resume.")
                return
            
            print("📋 Existing Checkpoints:")
            for i, cp in enumerate(checkpoints, 1):
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cp['timestamp']))
                print(f"{i}. {cp['session_id']} - {cp['total_books']} books, Page: {cp['current_page']} ({timestamp})")
            
            try:
                choice = int(input("\nWhich checkpoint would you like to resume from? (number): ")) - 1
                args.session_id = checkpoints[choice]['session_id']
            except (ValueError, IndexError):
                print("❌ Invalid selection.")
                return
    
    print(f"🎯 Hedef URL: {args.url}")
    print(f"📄 Page count: {args.pages} (approximately {args.pages * 100} books)")
    print(f"⏱️  Delay between requests: {args.delay} seconds")
    print(f"📁 Output file: {args.output}")
    if args.resume:
        print(f"🔄 Resume modu: {args.session_id}")
    print("-" * 60)
    
    try:
        # Start scraping with arguments
        books = scraper.scrape_list(
            args.url, 
            max_pages=args.pages, 
            delay=args.delay,
            session_id=args.session_id,
            resume=args.resume
        )
        
        if books:
            # Save to CSV
            df = scraper.save_to_csv(books, args.output)
            
            # Summary statistics
            print("\n=== SUMMARY STATISTICS ===")
            print(f"Total books: {len(df)}")
            print(f"Average rating: {df['average_rating'].mean():.2f}")
            print(f"Highest rating: {df['average_rating'].max()}")
            print(f"Most rated book: {df.loc[df['ratings_count'].idxmax(), 'title']}")
            print(f"Most reviewed book: {df.loc[df['reviews_count'].idxmax(), 'title']}")
            
        else:
            logging.error("No book data could be obtained")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation stopped by user!")
        print("💡 Checkpoints saved. You can check with --list-checkpoints.")
        
    except Exception as e:
        logging.error(f"Error in main function: {e}")
        print(f"\n❌ Error occurred: {e}")
        print("💡 Checkpoint'ler kaydedildi. --list-checkpoints ile kontrol edebilirsiniz.")

if __name__ == "__main__":
    main()