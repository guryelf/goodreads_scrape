#!/usr/bin/env python3
"""
Goodreads Scraper -     url = input("🔗 Different list URL? (Enter = Best Books Ever): ").strip()
    if not url:
        url = "https://www.goodreads.com/list/show/1.Best_Books_Ever"
    
    delay = input("⏱️ Delay between requests (seconds, default: 1.5): ").strip()
    if not delay:
        delay = "1.5"
    
    output = input("💾 Output filename (default: goodreads_books.csv): ").strip()
    if not output:
        output = "goodreads_books.csv" Script
This script checks required libraries and runs the scraper
"""

import subprocess
import sys
import os
from pathlib import Path

def check_requirements():
    """Check if required libraries are installed"""
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
    """Install missing libraries"""
    print("🔧 Installing required libraries...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Libraries successfully installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Library installation error: {e}")
        return False

def run_scraper():
    """Run the scraper script with user-defined parameters"""
    print("\n📚 Starting Goodreads Scraper")
    
    # Kullanıcıdan parametreler al
    pages = input("How many pages do you want to be processed?(Default 10):  ").strip()
    if not pages:
        pages = "10"
    
    url = input("🔗 Different List URL? (Enter = Best Books Ever): ").strip()
    if not url:
        url = "https://www.goodreads.com/list/show/1.Best_Books_Ever"
    
    delay = input("⏱️  Dely between requests(Default:1.5 secs): ").strip()
    if not delay:
        delay = "1.5"
    
    output = input("� Output file name(Default: goodreads_books.csv): ").strip()
    if not output:
        output = "goodreads_books.csv"
    
    print(f"\n🎯 Target: {url}")
    print(f"📄 {pages} pages (approximately {int(pages) * 100} books) will be processed...")
    print(f"⏱️ This process may take {int(pages) * 0.5}-{int(pages)} minutes...\n")
    
    try:
        # Change to src folder
        original_dir = os.getcwd()
        os.chdir('src')
        
        # Run scraper with arguments
        command = [
            sys.executable, "goodreads_scraper.py",
            "--pages", pages,
            "--url", url,
            "--delay", delay,
            "--output", output
        ]
        
        result = subprocess.run(command, capture_output=True, text=True)
        
        # Return to original folder
        os.chdir(original_dir)
        
        if result.returncode == 0:
            print("✅ Scraping completed successfully!")
            print(f"📊 Output: {result.stdout}")
            
            # Check if data file was created
            data_file = Path(f'data/{output}')
            if data_file.exists():
                print(f"\n📁 Data file created: {data_file}")
                print(f"📏 File size: {data_file.stat().st_size / 1024:.1f} KB")
            
        else:
            print("❌ Error occurred during scraping:")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Script execution error: {e}")
        os.chdir(original_dir)

def show_project_info():
    """Display project information"""
    print("="*60)
    print("📚 GOODREADS WEB SCRAPER PROJECT")
    print("="*60)
    print("🎯 Purpose: Collect most popular books from Goodreads")
    print("📊 Target: ~1000 book records")
    print("🔧 Technology: Python + BeautifulSoup + Pandas")
    print("📁 Folder structure:")
    print("   ├── src/                 # Python code")
    print("   ├── data/                # Collected data")
    print("   ├── requirements.txt     # Required libraries")
    print("   └── README.md           # Documentation")
    print("="*60)

def main():
    """Main function"""
    show_project_info()
    
    # Check required libraries
    missing = check_requirements()
    
    if missing:
        print(f"\n⚠️ Missing libraries detected: {', '.join(missing)}")
        
        install_choice = input("\n🤔 Would you like to install missing libraries? (y/n): ").lower().strip()
        
        if install_choice in ['y', 'yes']:
            if not install_requirements():
                print("❌ Installation failed. Run 'pip install -r requirements.txt' manually.")
                return
        else:
            print("❌ Scraper cannot run without required libraries.")
            print("💡 Install command: pip install -r requirements.txt")
            return
    
    else:
        print("\n✅ All required libraries are installed!")
    
    # Run scraper
    run_choice = input("\n🚀 Would you like to start the scraper? (y/n): ").lower().strip()
    
    if run_choice in ['y', 'yes']:
        run_scraper()
        
        # Analysis suggestion
        print("\n💡 TIP: To analyze the collected data:")
        print("   cd src && python analyze_data.py")
        
    else:
        print("👋 Have a great day! Run again when you're ready.")

if __name__ == "__main__":
    main()