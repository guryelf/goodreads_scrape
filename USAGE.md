# � Goodreads Scraper - Detailed Usage Guide

This documentation explains the detailed usage of all Goodreads Scraper features.

## 📋 Table of Contents

1. [B## � Checkpoint System

### What is a Checkpoint?
If an err- 🗑️ Auto-cleanup: Files are deleted when process completes successfully

## 🔧 Troubleshooting

### Common Errorscurs during scraping or the process is interrupted, collected data is automatically saved. This allows you to resume from where you left off. Usage](#basic-usage)
2. [Command Line Parameters](#command-line-parameters)
3. [Checkpoint/Resume System](#checkpointresume-system)
4. [Working with Different Lists](#working-with-different-lists)
5. [Error Management](#error-management)
6. [Tips and Best Practices](#tips-and-best-practices)

## 🚀 Basic Usage

### 1. Quick Start (Recommended)

For the simplest usage, run the interactive script:

### Available Parameters

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `--pages` | Number of pages to scrape | 10 | `--pages 5` |
| `--url` | Goodreads list URL | Best Books Ever | `--url "https://..."` |
| `--delay` | Delay between requests (seconds) | 1.5 | `--delay 2.0` |
| `--output` | Output CSV file name | goodreads_books.csv | `--output "my_books.csv"` |
| `--verbose` | Detailed debug logs | Off | `--verbose` |
| `--resume` | Resume from previous session | Off | `--resume` |
| `--session-id` | Resume with specific session ID | - | `--session-id session_123` |
| `--list-checkpoints` | List available checkpoints | - | `--list-checkpoints` |

## 🚀 Usage Examples

### 1. Quick Test (5 pages)
```bash
python goodreads_scraper.py --pages 5
```

### 2. Large Dataset (20 pages)
```bash
python goodreads_scraper.py --pages 20 --delay 2.0 --output "big_dataset.csv"
```

### 3. Different List (Science Fiction)
```bash
python goodreads_scraper.py \
  --url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books" \
  --pages 15 \
  --output "sci_fi_books.csv"
```

### 4. Debug Mode
```bash
python goodreads_scraper.py --pages 3 --verbose
```

### 5. List Checkpoints
```bash
python goodreads_scraper.py --list-checkpoints
```

### 6. Resume from Interruption
```bash
# Automatic checkpoint selection
python goodreads_scraper.py --resume

# Resume from specific session
python goodreads_scraper.py --resume --session-id session_1727226123
```

### 7. Very Fast Scraping (Use Carefully!)
```bash
python goodreads_scraper.py --pages 10 --delay 0.5
```

## 📊 Popular Goodreads Lists

### Most Popular Lists
```bash
# Best Books Ever
--url "https://www.goodreads.com/list/show/1.Best_Books_Ever"

# Books Everyone Should Read At Least Once  
--url "https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once"

# Best Science Fiction & Fantasy
--url "https://www.goodreads.com/list/show/3.Best_Science_Fiction_Fantasy_Books"

--url "https://www.goodreads.com/list/show/18.Best_Mystery_Thriller_Books"

# Best Romance Books
--url "https://www.goodreads.com/list/show/8.Best_Romance_Novels"
```

### Lists by Genre
```bash
# Classic Literature
--url "https://www.goodreads.com/list/show/12.Best_Books_of_the_20th_Century"

# Young Adult (YA)
--url "https://www.goodreads.com/list/show/43.Best_Young_Adult_Books"

# Non-Fiction
--url "https://www.goodreads.com/list/show/7.Best_Nonfiction"
```

## 💡 Tips

### Performance Optimization
- **For small tests**: `--pages 1-3`
- **For normal usage**: `--pages 10-15` 
- **For large datasets**: `--pages 20+`

### Rate Limiting
- **Safe**: `--delay 1.5-2.0`
- **Fast**: `--delay 1.0` (use carefully)
- **Very fast**: `--delay 0.5` (for testing only)

### Output File Names
- Add date: `--output "books_2025_09_25.csv"`
- Specify genre: `--output "fantasy_books.csv"`
- Add page count: `--output "books_20_pages.csv"`

## 🔄 Checkpoint System

### What is a Checkpoint?
If an error occurs during scraping or the process is interrupted, collected data is automatically saved. This allows you to resume from where you left off.
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

## 💡 Tips

### Performance Optimization
- **For small tests**: `--pages 1-3`
- **For normal usage**: `--pages 10-15` 
- **For large datasets**: `--pages 20+`

### Rate Limiting
- **Safe**: `--delay 1.5-2.0`
- **Fast**: `--delay 1.0` (use carefully)
- **Very fast**: `--delay 0.5` (for testing only)

### Output File Names
- Add date: `--output "books_2025_09_25.csv"`
- Specify genre: `--output "fantasy_books.csv"`
- Add page count: `--output "books_20_pages.csv"`

## What is Checkpoint?
If an error occurs during scraping or the process is interrupted, collected data is automatically saved. This allows you to resume from where you left off.

### When are Checkpoints Saved?
- ✅ Automatically every 2 pages
- ✅ When an error occurs
- ✅ When the process is interrupted (Ctrl+C)

### Using Checkpoints

#### 1. View Available Checkpoints
```bash
python goodreads_scraper.py --list-checkpoints
```

#### 2. Resume After Interruption
```bash
# Interactive selection
python goodreads_scraper.py --resume

# With specific session
python goodreads_scraper.py --resume --session-id session_1727226123
```

#### 3. Checkpoint Example Scenario
```bash
# 1. Start a large scraping operation
python goodreads_scraper.py --pages 50 --output "big_dataset.csv"

# 2. Error occurred! (internet disconnected, etc.)
# You will see a message like:
# "Checkpoint saved. To resume: --resume --session-id session_1727226123"

# 3. Resume from where you left off
python goodreads_scraper.py --resume --session-id session_1727226123
```

### Checkpoint Files
- 📁 Location: `data/checkpoints/`
- 📝 Format: JSON (checkpoint_SESSION_ID.json)
- 🗑️ Auto-deletion: When operation completes successfully

## 🔧 Troubleshooting

### Common Errors
```bash
# File not found
cd src && python goodreads_scraper.py

# Missing library

### Checkpoint Files
- 📁 Location: `data/checkpoints/`
- 📝 Format: JSON (checkpoint_SESSION_ID.json)
- 🗑️ Auto-cleanup: Files are deleted when process completes successfully

## �🔧 Sorun Giderme

### Common Errors
```bash
# File not found
cd src && python goodreads_scraper.py

# Missing library
pip install -r requirements.txt

# Permission denied
chmod +x goodreads_scraper.py
```

### Checkpoint Issues
```bash
# Clean corrupted checkpoint
rm -rf ../data/checkpoints/checkpoint_SESSION_ID.json

# Clean all checkpoints
rm -rf ../data/checkpoints/*.json
```

### Debug Mode
If you experience any problems, use the `--verbose` parameter:
```bash
python goodreads_scraper.py --pages 1 --verbose
```

## 📈 Performance Guide

| Page Count | Estimated Time | Book Count | File Size |
|------------|----------------|------------|-----------|
| 1 | 10 seconds | ~100 | ~12 KB |
| 5 | 1 minute | ~500 | ~60 KB |
| 10 | 2-3 minutes | ~1000 | ~120 KB |
| 20 | 5-6 minutes | ~2000 | ~240 KB |
| 50 | 12-15 minutes | ~5000 | ~600 KB |

---

**⚠️ Note**: Respect Goodreads' terms of service and don't send requests too quickly.