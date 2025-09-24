"""
Goodreads Veri Seti Analiz Scripti
Toplanan veri setini analiz etmek için örnek kod
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_data():
    """CSV dosyasını yükler"""
    data_path = Path('../data/goodreads_top_1000_books.csv')
    if data_path.exists():
        return pd.read_csv(data_path)
    else:
        print("Veri dosyası bulunamadı. Önce scraper'ı çalıştırın.")
        return None

def basic_statistics(df):
    """Temel istatistikler"""
    print("=== TEMEL İSTATİSTİKLER ===")
    print(f"Toplam kitap sayısı: {len(df)}")
    print(f"Benzersiz yazar sayısı: {df['author'].nunique()}")
    print(f"Ortalama puan: {df['average_rating'].mean():.2f}")
    print(f"Medyan puan: {df['average_rating'].median():.2f}")
    print(f"En yüksek puan: {df['average_rating'].max():.2f}")
    print(f"En düşük puan: {df['average_rating'].min():.2f}")
    print()
    
def top_books(df, n=10):
    """En popüler kitapları gösterir"""
    print(f"=== EN POPÜLER {n} KİTAP (Puan Sayısına Göre) ===")
    top_by_ratings = df.nlargest(n, 'ratings_count')[['title', 'author', 'average_rating', 'ratings_count']]
    print(top_by_ratings.to_string(index=False))
    print()
    
def top_authors(df, n=10):
    """En popüler yazarları gösterir"""
    print(f"=== EN POPÜLER {n} YAZAR (Toplam Puan Sayısına Göre) ===")
    author_stats = df.groupby('author').agg({
        'ratings_count': 'sum',
        'title': 'count',
        'average_rating': 'mean'
    }).round(2)
    author_stats.columns = ['Toplam_Puan_Sayisi', 'Kitap_Sayisi', 'Ortalama_Puan']
    top_authors_list = author_stats.nlargest(n, 'Toplam_Puan_Sayisi')
    print(top_authors_list.to_string())
    print()

def rating_distribution_analysis(df):
    """Puan dağılımı analizi"""
    print("=== PUAN DAĞILIMI ANALİZİ ===")
    rating_ranges = pd.cut(df['average_rating'], 
                          bins=[0, 3.5, 4.0, 4.2, 4.4, 5.0],
                          labels=['Zayıf (≤3.5)', 'Orta (3.5-4.0)', 'İyi (4.0-4.2)', 'Çok İyi (4.2-4.4)', 'Mükemmel (>4.4)'])
    
    rating_dist = rating_ranges.value_counts().sort_index()
    print(rating_dist)
    print()
    
def engagement_analysis(df):
    """Engagement (etkileşim) analizi"""
    print("=== ETKİLEŞİM ANALİZİ ===")
    
    # En yüksek puan/yorum oranına sahip kitaplar
    print("En çok 'tartışma' yaratan kitaplar (yüksek puan/yorum oranı):")
    high_engagement = df.nlargest(10, 'rating_to_review_ratio')[['title', 'author', 'rating_to_review_ratio', 'ratings_count', 'reviews_count']]
    print(high_engagement.to_string(index=False))
    print()

def create_visualizations(df):
    """Veri görselleştirme"""
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Puan dağılımı histogram
    axes[0,0].hist(df['average_rating'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0,0].set_title('Ortalama Puan Dağılımı')
    axes[0,0].set_xlabel('Ortalama Puan')
    axes[0,0].set_ylabel('Kitap Sayısı')
    
    # 2. Puan sayısı vs Ortalama puan scatter plot
    axes[0,1].scatter(df['ratings_count'], df['average_rating'], alpha=0.6, color='coral')
    axes[0,1].set_title('Puan Sayısı vs Ortalama Puan')
    axes[0,1].set_xlabel('Puan Sayısı')
    axes[0,1].set_ylabel('Ortalama Puan')
    axes[0,1].set_xscale('log')
    
    # 3. Top 15 yazarın kitap sayıları
    top_authors_count = df['author'].value_counts().head(15)
    axes[1,0].barh(range(len(top_authors_count)), top_authors_count.values, color='lightgreen')
    axes[1,0].set_yticks(range(len(top_authors_count)))
    axes[1,0].set_yticklabels(top_authors_count.index, fontsize=8)
    axes[1,0].set_title('En Çok Kitabı Olan 15 Yazar')
    axes[1,0].set_xlabel('Kitap Sayısı')
    
    # 4. Puan/Yorum oranı dağılımı (log scale)
    valid_ratios = df['rating_to_review_ratio'].dropna()
    valid_ratios = valid_ratios[valid_ratios > 0]  # Pozitif değerler
    axes[1,1].hist(np.log10(valid_ratios), bins=30, alpha=0.7, color='gold', edgecolor='black')
    axes[1,1].set_title('Puan/Yorum Oranı Dağılımı (Log Scale)')
    axes[1,1].set_xlabel('Log10(Puan/Yorum Oranı)')
    axes[1,1].set_ylabel('Kitap Sayısı')
    
    plt.tight_layout()
    plt.savefig('../data/goodreads_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Grafikler 'data/goodreads_analysis.png' dosyasına kaydedildi")
    plt.show()

def export_summary_report(df):
    """Özet raporu Excel formatında export eder"""
    with pd.ExcelWriter('../data/goodreads_summary_report.xlsx', engine='openpyxl') as writer:
        # Genel istatistikler
        summary_stats = pd.DataFrame({
            'Metrik': ['Toplam Kitap', 'Benzersiz Yazar', 'Ortalama Puan', 'Medyan Puan'],
            'Değer': [len(df), df['author'].nunique(), 
                     round(df['average_rating'].mean(), 2),
                     round(df['average_rating'].median(), 2)]
        })
        summary_stats.to_excel(writer, sheet_name='Özet_İstatistikler', index=False)
        
        # En popüler kitaplar
        df.nlargest(50, 'ratings_count').to_excel(writer, sheet_name='En_Popüler_Kitaplar', index=False)
        
        # Yazar istatistikleri
        author_stats = df.groupby('author').agg({
            'ratings_count': 'sum',
            'title': 'count',
            'average_rating': 'mean'
        }).round(2)
        author_stats.columns = ['Toplam_Puan_Sayisi', 'Kitap_Sayisi', 'Ortalama_Puan']
        author_stats.nlargest(30, 'Toplam_Puan_Sayisi').to_excel(writer, sheet_name='Yazar_İstatistikleri')
        
    print("📋 Detaylı rapor 'data/goodreads_summary_report.xlsx' dosyasına kaydedildi")

def main():
    """Ana analiz fonksiyonu"""
    # Veriyi yükle
    df = load_data()
    if df is None:
        return
    
    print("📚 GOODREADS VERİ SETİ ANALİZİ\n")
    
    # Analizleri çalıştır
    basic_statistics(df)
    top_books(df)
    top_authors(df)
    rating_distribution_analysis(df)
    engagement_analysis(df)
    
    # Görselleştirmeler
    create_visualizations(df)
    
    # Rapor export
    export_summary_report(df)
    
    print("\n✅ Analiz tamamlandı!")

if __name__ == "__main__":
    main()