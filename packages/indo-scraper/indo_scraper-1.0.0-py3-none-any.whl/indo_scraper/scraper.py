# indo_scraper/scraper.py
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Union
import logging
from .utils import validate_indonesian_domain, clean_text, extract_contact_info

class IndoScraper:
    """
    Library untuk scraping website Indonesia dengan mudah
    
    Contoh penggunaan:
    scraper = IndoScraper()
    hasil = scraper.scrape("https://www.smkn5bandung.sch.id/")
    """
    
    def __init__(self, delay: float = 1.0, timeout: int = 30):
        """
        Inisialisasi IndoScraper
        
        Args:
            delay (float): Jeda waktu antar request (detik)
            timeout (int): Timeout untuk request (detik)
        """
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def scrape(self, url: str, extract_links: bool = True, extract_images: bool = True, 
              extract_contact: bool = True, max_pages: int = 1) -> Dict:
        """
        Scraping data dari website Indonesia
        
        Args:
            url (str): URL website yang akan di-scrape
            extract_links (bool): Ekstrak semua link
            extract_images (bool): Ekstrak semua gambar
            extract_contact (bool): Ekstrak informasi kontak
            max_pages (int): Maksimal halaman yang akan di-scrape
            
        Returns:
            Dict: Data hasil scraping
        """
        
        # Validasi domain Indonesia
        if not validate_indonesian_domain(url):
            self.logger.warning(f"Website {url} mungkin bukan domain Indonesia")
        
        hasil = {
            'url': url,
            'domain': urlparse(url).netloc,
            'title': '',
            'description': '',
            'content': '',
            'links': [],
            'images': [],
            'contact_info': {},
            'metadata': {},
            'status': 'success',
            'scraped_pages': 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Scrape halaman utama
            page_data = self._scrape_single_page(url, extract_links, extract_images, extract_contact)
            hasil.update(page_data)
            hasil['scraped_pages'] = 1
            
            # Scrape halaman tambahan jika diminta
            if max_pages > 1 and hasil['links']:
                internal_links = [link for link in hasil['links'] 
                                if urlparse(link).netloc == urlparse(url).netloc][:max_pages-1]
                
                for link in internal_links:
                    try:
                        time.sleep(self.delay)
                        additional_data = self._scrape_single_page(link, False, False, False)
                        hasil['content'] += f"\n\n--- Halaman: {link} ---\n" + additional_data['content']
                        hasil['scraped_pages'] += 1
                    except Exception as e:
                        self.logger.error(f"Error scraping {link}: {str(e)}")
            
            self.logger.info(f"Berhasil scraping {hasil['scraped_pages']} halaman dari {url}")
            
        except Exception as e:
            hasil['status'] = 'error'
            hasil['error'] = str(e)
            self.logger.error(f"Error scraping {url}: {str(e)}")
        
        return hasil
    
    def _scrape_single_page(self, url: str, extract_links: bool = True, 
                           extract_images: bool = True, extract_contact: bool = True) -> Dict:
        """Scrape satu halaman website"""
        
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Hapus script dan style tags
        for script in soup(["script", "style"]):
            script.decompose()
        
        hasil = {
            'title': self._extract_title(soup),
            'description': self._extract_description(soup),
            'content': clean_text(soup.get_text()),
            'links': [],
            'images': [],
            'contact_info': {},
            'metadata': self._extract_metadata(soup)
        }
        
        if extract_links:
            hasil['links'] = self._extract_links(soup, url)
        
        if extract_images:
            hasil['images'] = self._extract_images(soup, url)
        
        if extract_contact:
            hasil['contact_info'] = extract_contact_info(soup.get_text())
        
        return hasil
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Ekstrak judul halaman"""
        title_tag = soup.find('title')
        if title_tag:
            return clean_text(title_tag.get_text())
        
        h1_tag = soup.find('h1')
        if h1_tag:
            return clean_text(h1_tag.get_text())
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Ekstrak deskripsi halaman"""
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return clean_text(meta_desc['content'])
        
        # Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return clean_text(og_desc['content'])
        
        # Paragraf pertama
        first_p = soup.find('p')
        if first_p:
            text = clean_text(first_p.get_text())
            return text[:200] + "..." if len(text) > 200 else text
        
        return ""
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Ekstrak semua link dari halaman"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            if full_url not in links:
                links.append(full_url)
        return links
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Ekstrak semua gambar dari halaman"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            full_url = urljoin(base_url, src)
            if full_url not in images:
                images.append(full_url)
        return images
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Ekstrak metadata dari halaman"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata[meta['name']] = meta.get('content', '')
            elif meta.get('property'):
                metadata[meta['property']] = meta.get('content', '')
        
        return metadata
    
    def save_to_json(self, data: Dict, filename: str) -> None:
        """Simpan hasil scraping ke file JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Data disimpan ke {filename}")
    
    def scrape_multiple(self, urls: List[str], **kwargs) -> List[Dict]:
        """Scrape multiple URLs"""
        hasil = []
        for url in urls:
            self.logger.info(f"Scraping {url}...")
            data = self.scrape(url, **kwargs)
            hasil.append(data)
            time.sleep(self.delay)
        return hasil