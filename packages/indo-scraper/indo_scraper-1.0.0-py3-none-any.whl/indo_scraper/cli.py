# indo_scraper/cli.py
import argparse
import sys
from .scraper import IndoScraper
from .utils import format_scraped_data

def main():
    """Command line interface untuk Indo Scraper"""
    parser = argparse.ArgumentParser(
        description="Library untuk scraping website Indonesia dengan mudah",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  indo-scraper https://www.smkn5bandung.sch.id/
  indo-scraper https://www.detik.com --max-pages 3 --output hasil.json
  indo-scraper https://www.kemendikbud.go.id --no-images --delay 2
        """
    )
    
    parser.add_argument(
        'url',
        help='URL website yang akan di-scrape'
    )
    
    parser.add_argument(
        '--max-pages',
        type=int,
        default=1,
        help='Maksimal halaman yang akan di-scrape (default: 1)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Jeda waktu antar request dalam detik (default: 1.0)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout untuk request dalam detik (default: 30)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='File output untuk menyimpan hasil (format JSON)'
    )
    
    parser.add_argument(
        '--no-links',
        action='store_true',
        help='Jangan ekstrak link'
    )
    
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='Jangan ekstrak gambar'
    )
    
    parser.add_argument(
        '--no-contact',
        action='store_true',
        help='Jangan ekstrak informasi kontak'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='indo-scraper 1.0.0'
    )
    
    args = parser.parse_args()
    
    # Inisialisasi scraper
    scraper = IndoScraper(delay=args.delay, timeout=args.timeout)
    
    print(f"Memulai scraping: {args.url}")
    print(f"Maksimal halaman: {args.max_pages}")
    print(f"Jeda waktu: {args.delay} detik")
    print("-" * 50)
    
    try:
        # Jalankan scraping
        hasil = scraper.scrape(
            url=args.url,
            extract_links=not args.no_links,
            extract_images=not args.no_images,
            extract_contact=not args.no_contact,
            max_pages=args.max_pages
        )
        
        # Tampilkan hasil
        print(format_scraped_data(hasil))
        
        # Simpan ke file jika diminta
        if args.output:
            scraper.save_to_json(hasil, args.output)
            print(f"\nHasil disimpan ke: {args.output}")
        
        # Status exit
        if hasil['status'] == 'success':
            sys.exit(0)
        else:
            print(f"\nError: {hasil.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nScraping dibatalkan oleh user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()