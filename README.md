# 📚 Goodreads Most Popular Books Dataset - Web Scraping Project

This project is a Python web scraping application that automatically collects information about the most popular books from Goodreads.com's "Best Books Ever" list. It creates a rich dataset for book readers, authors, and aspiring data analysts.

## 🎯 Project Purpose

To create a cleaned dataset by collecting the following information from Goodreads' "Best Books Ever" list:
- 📖 Book Title 
- ✍️ Author Name
- ⭐ Average Rating
- 📊 Total Rating Count
- 💬 Review Count
- 🔗 Book URL
- 📈 Rating/Review Ratio (new feature)

## 🛠️ Technical Specifications

### Used technologies
- **Python 3.8+**
- **requests**: For HTTP requests
- **BeautifulSoup4**: For HTML parsing
- **pandas**: Data processing and analysis
- **tqdm**: Progress bar
- **lxml**: XML/HTML parser

### Scraping Specifications
- ✅ **Pagination**
- ✅ **Rate limiting** (1.5 seconds wait between requests)
- ✅ **Hata yakalama ve logging**
- ✅ **robots.txt compliant** operations
- ✅ **Data cleaning** and validation
- ✅ **Progress tracking** (with tqdm)
- ✅ **Checkpoint system** (resume after interruption)
- ✅ **Resume feature** (start from where you left off)

## 📁 Project Structure

```
goodreads-scraper/
│
├── src/
│   └── goodreads_scraper.py    # Main scraper code
│
├── data/
│   └── goodreads_top_1000_books.csv    # Collected dataset
│
├── requirements.txt            # Python dependencies
├── README.md                  # This documentation
└── scraper.log               # Operation logs
```

## 🚀 Installation and Usage

### 1. Download the Project
```bash
git clone <repository-url>
cd goodreads-scraper
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Scraper

#### Quick Start (Interactive)
```bash
python run_scraper.py
```

#### With Command Line
```bash
cd src
python goodreads_scraper.py --pages 10 --delay 1.5
```

#### With Different List
```bash
cd src
python goodreads_scraper.py \
  --url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books" \
  --pages 15 \
  --output "sci_fi_books.csv"
```

## ⚙️ Configuration

### Command Line Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--pages` | Number of pages to scrape | 10 | `--pages 5` |
| `--url` | Goodreads list URL | Best Books Ever | `--url "https://..."` |
| `--delay` | Delay between requests | 1.5s | `--delay 2.0` |
| `--output` | Output file name | goodreads_books.csv | `--output "my_books.csv"` |
| `--verbose` | Detailed logs | Off | `--verbose` |

### Examples
```bash
# Quick test (5 pages)
python goodreads_scraper.py --pages 5

# Large dataset (20 pages, slow)  
python goodreads_scraper.py --pages 20 --delay 2.0

# Science fiction books
python goodreads_scraper.py \
  --url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books" \
  --pages 10 \
  --output "sci_fi_books.csv"
```

## ✨ New Features (v2.0)

### 🔄 Checkpoint/Resume System
- **Automatic Resume**: Resume interrupted operations from where they left off
- **Session Management**: Switch between different scraping sessions
- **Checkpoint Listing**: View and manage existing checkpoints
- **Automatic Cleanup**: Old checkpoints are automatically cleaned up

### 🎛️ Command Line Arguments
- `--pages`: Specify how many pages to scrape (1-100)
- `--delay`: Set delay between requests (1-10 seconds)
- `--output`: Customize output file name
- `--resume`: Resume from last checkpoint
- `--session-id`: Resume from specific session

📖 **For detailed usage**: See [USAGE.md](USAGE.md) file.

## 📊 Data Cleaning Process

The script automatically performs the following cleaning operations:

1. **Missing Title Check**: Removes books without titles
2. **Duplicate Removal**: Removes identical book-author combinations
3. **Data Type Conversion**: Converts numerical data to int/float
4. **Feature Engineering**: Calculates rating/review ratio
5. **Sorting**: Sorts books by rating count

## 📈 Output Format

CSV file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `title` | Book title | "To Kill a Mockingbird" |
| `author` | Author name | "Harper Lee" |
| `average_rating` | Average rating | 4.27 |
| `ratings_count` | Total rating count | 5234567 |
| `reviews_count` | Review count | 234567 |
| `book_url` | Goodreads book link | "https://www.goodreads.com/book/..." |
| `rating_to_review_ratio` | Rating/Review ratio | 22.3 |

## 🚦 Rate Limiting and Ethical Usage

This project is designed to comply with Goodreads' robots.txt file:

- ✅ Listopia pages (`/list/show/`) are not banned in robots.txt
- ⏱️ 1.5-second delay between requests
- 📝 Respectful User-Agent usage
- 🔍 Targeting only public lists

## 🔧 Challenges Faced and Solutions

### 1. **Pagination Problem**
**Problem**: Finding Goodreads' "Next" button
**Solution**: Multiple CSS selector attempts and regex usage

### 2. **Data Format Inconsistencies**  
**Problem**: Extracting numbers from "1,234,567 ratings" format texts
**Solution**: Regex patterns and string cleaning functions

### 3. **Request Blocking**
**Problem**: Sending requests too quickly
**Solution**: Rate limiting and appropriate User-Agent usage

## 📋 Example Use Cases

1. **Book Recommendation Algorithm**: Finding books with highest rating/review ratios
2. **Author Analysis**: Identifying most popular authors  
3. **Trend Analysis**: Examining rating distributions
4. **Data Visualization**: Creating charts with Matplotlib/Seaborn

## 🤝 Contributing

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Legal Disclaimer

- This project is for educational purposes only
- Respects Goodreads' terms of service and robots.txt file
- Data is for personal use, should not be used commercially
- Always check the target site's rules when web scraping

## 📞 Contact

Please open an issue for any questions or suggestions.

---

**⭐ If this project helped you, don't forget to star the repository!**