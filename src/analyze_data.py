"""
Goodreads Dataset Analysis Script
Sample code for analyzing collected dataset
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_data(filename=None):
    """Load CSV file"""
    data_dir = Path('../data')
    
    # Try different possible filenames
    possible_files = [
        'goodreads_books.csv',
        'goodreads_top_1000_books.csv',
        'books.csv'
    ]
    
    # If specific filename provided, try that first
    if filename:
        data_path = data_dir / filename
        if data_path.exists():
            print(f"Loading data from: {data_path}")
            return pd.read_csv(data_path)
    
    # Try common filenames
    for file in possible_files:
        data_path = data_dir / file
        if data_path.exists():
            print(f"Loading data from: {data_path}")
            return pd.read_csv(data_path)
    
    # If no files found, list available CSV files
    csv_files = list(data_dir.glob('*.csv'))
    if csv_files:
        print("Data file not found with default names.")
        print("Available CSV files in data directory:")
        for f in csv_files:
            print(f"  - {f.name}")
        print(f"Use: load_data('{csv_files[0].name}') to load the first available file.")
    else:
        print("No CSV files found in data directory. Run the scraper first.")
    
    return None

def basic_statistics(df):
    """Basic statistics"""
    print("=== BASIC STATISTICS ===")
    print(f"Total books: {len(df)}")
    print(f"Unique authors: {df['author'].nunique()}")
    print(f"Average rating: {df['average_rating'].mean():.2f}")
    print(f"Median rating: {df['average_rating'].median():.2f}")
    print(f"Highest rating: {df['average_rating'].max():.2f}")
    print(f"Lowest rating: {df['average_rating'].min():.2f}")
    print()
    
def top_books(df, n=10):
    """Show most popular books"""
    print(f"=== TOP {n} MOST POPULAR BOOKS (By Rating Count) ===")
    top_by_ratings = df.nlargest(n, 'ratings_count')[['title', 'author', 'average_rating', 'ratings_count']]
    print(top_by_ratings.to_string(index=False))
    print()
    
def top_authors(df, n=10):
    """Show most popular authors"""
    print(f"=== TOP {n} AUTHORS (By Total Rating Count) ===")
    author_stats = df.groupby('author').agg({
        'ratings_count': 'sum',
        'title': 'count',
        'average_rating': 'mean'
    }).round(2)
    author_stats.columns = ['Total_Rating_Count', 'Book_Count', 'Average_Rating']
    top_authors_list = author_stats.nlargest(n, 'Total_Rating_Count')
    print(top_authors_list.to_string())
    print()

def rating_distribution_analysis(df):
    """Rating distribution analysis"""
    print("=== RATING DISTRIBUTION ANALYSIS ===")
    rating_ranges = pd.cut(df['average_rating'], 
                          bins=[0, 3.5, 4.0, 4.2, 4.4, 5.0],
                          labels=['Poor (≤3.5)', 'Average (3.5-4.0)', 'Good (4.0-4.2)', 'Very Good (4.2-4.4)', 'Excellent (>4.4)'])
    
    rating_dist = rating_ranges.value_counts().sort_index()
    print(rating_dist)
    print()
    
def engagement_analysis(df):
    """Engagement analysis"""
    print("=== ENGAGEMENT ANALYSIS ===")
    
    # Books with highest rating/review ratios
    print("Most 'discussed' books (high rating/review ratio):")
    high_engagement = df.nlargest(10, 'rating_to_review_ratio')[['title', 'author', 'rating_to_review_ratio', 'ratings_count', 'reviews_count']]
    print(high_engagement.to_string(index=False))
    print()

def create_visualizations(df):
    """Data visualization"""
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Rating distribution histogram
    axes[0,0].hist(df['average_rating'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0,0].set_title('Average Rating Distribution')
    axes[0,0].set_xlabel('Average Rating')
    axes[0,0].set_ylabel('Number of Books')
    
    # 2. Rating count vs Average rating scatter plot
    axes[0,1].scatter(df['ratings_count'], df['average_rating'], alpha=0.6, color='coral')
    axes[0,1].set_title('Rating Count vs Average Rating')
    axes[0,1].set_xlabel('Rating Count')
    axes[0,1].set_ylabel('Average Rating')
    axes[0,1].set_xscale('log')
    
    # 3. Top 15 authors by book count
    top_authors_count = df['author'].value_counts().head(15)
    axes[1,0].barh(range(len(top_authors_count)), top_authors_count.values, color='lightgreen')
    axes[1,0].set_yticks(range(len(top_authors_count)))
    axes[1,0].set_yticklabels(top_authors_count.index, fontsize=8)
    axes[1,0].set_title('Top 15 Authors by Book Count')
    axes[1,0].set_xlabel('Number of Books')
    
    # 4. Rating/Review ratio distribution (log scale)
    valid_ratios = df['rating_to_review_ratio'].dropna()
    valid_ratios = valid_ratios[valid_ratios > 0]  # Positive values only
    axes[1,1].hist(np.log10(valid_ratios), bins=30, alpha=0.7, color='gold', edgecolor='black')
    axes[1,1].set_title('Rating/Review Ratio Distribution (Log Scale)')
    axes[1,1].set_xlabel('Log10(Rating/Review Ratio)')
    axes[1,1].set_ylabel('Number of Books')
    
    plt.tight_layout()
    plt.savefig('../data/goodreads_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Charts saved to 'data/goodreads_analysis.png'")
    plt.show()

def export_summary_report(df):
    """Export summary report in Excel format"""
    with pd.ExcelWriter('../data/goodreads_summary_report.xlsx', engine='openpyxl') as writer:
        # General statistics
        summary_stats = pd.DataFrame({
            'Metric': ['Total Books', 'Unique Authors', 'Average Rating', 'Median Rating'],
            'Value': [len(df), df['author'].nunique(), 
                     round(df['average_rating'].mean(), 2),
                     round(df['average_rating'].median(), 2)]
        })
        summary_stats.to_excel(writer, sheet_name='Summary_Statistics', index=False)
        
        # Most popular books
        df.nlargest(50, 'ratings_count').to_excel(writer, sheet_name='Most_Popular_Books', index=False)
        
        # Author statistics
        author_stats = df.groupby('author').agg({
            'ratings_count': 'sum',
            'title': 'count',
            'average_rating': 'mean'
        }).round(2)
        author_stats.columns = ['Total_Rating_Count', 'Book_Count', 'Average_Rating']
        author_stats.nlargest(30, 'Total_Rating_Count').to_excel(writer, sheet_name='Author_Statistics')
        
    print("📋 Detailed report saved to 'data/goodreads_summary_report.xlsx'")

def main():
    """Main analysis function"""
    # Load data
    df = load_data()
    if df is None:
        return
    
    print("📚 GOODREADS DATASET ANALYSIS\n")
    
    # Run analyses
    basic_statistics(df)
    top_books(df)
    top_authors(df)
    rating_distribution_analysis(df)
    engagement_analysis(df)
    
    # Visualizations
    create_visualizations(df)
    
    # Export report
    export_summary_report(df)
    
    print("\n✅ Analysis completed!")

if __name__ == "__main__":
    main()