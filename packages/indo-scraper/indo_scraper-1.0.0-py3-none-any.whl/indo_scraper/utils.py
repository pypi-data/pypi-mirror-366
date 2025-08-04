# indo_scraper/utils.py
import re
from urllib.parse import urlparse
from typing import Dict, List

# Daftar domain Indonesia yang umum
INDONESIAN_DOMAINS = [
    '.id', '.co.id', '.or.id', '.ac.id', '.sch.id', '.net.id', '.web.id',
    '.my.id', '.go.id', '.mil.id', '.desa.id', '.ponpes.id'
]

def validate_indonesian_domain(url: str) -> bool:
    """
    Validasi apakah URL menggunakan domain Indonesia
    
    Args:
        url (str): URL yang akan divalidasi
        
    Returns:
        bool: True jika domain Indonesia
    """
    try:
        domain = urlparse(url).netloc.lower()
        return any(domain.endswith(indo_domain) for indo_domain in INDONESIAN_DOMAINS)
    except:
        return False

def clean_text(text: str) -> str:
    """
    Bersihkan teks dari karakter yang tidak perlu
    
    Args:
        text (str): Teks yang akan dibersihkan
        
    Returns:
        str: Teks yang sudah dibersihkan
    """
    if not text:
        return ""
    
    # Hapus whitespace berlebih
    text = re.sub(r'\s+', ' ', text)
    
    # Hapus karakter kontrol
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Trim
    text = text.strip()
    
    return text

def extract_contact_info(text: str) -> Dict[str, List[str]]:
    """
    Ekstrak informasi kontak dari teks
    
    Args:
        text (str): Teks yang akan diekstrak
        
    Returns:
        Dict: Informasi kontak yang ditemukan
    """
    contact_info = {
        'emails': [],
        'phones': [],
        'addresses': []
    }
    
    # Ekstrak email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    contact_info['emails'] = list(set(emails))
    
    # Ekstrak nomor telepon Indonesia
    phone_patterns = [
        r'\+62\s*\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,4}',  # +62 format
        r'0\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,4}',        # 08xx format
        r'\(0\d{2,3}\)\s*\d{3,4}[\s-]?\d{3,4}'        # (021) format
    ]
    
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        contact_info['phones'].extend(phones)
    
    contact_info['phones'] = list(set(contact_info['phones']))
    
    # Ekstrak alamat (kata kunci Indonesia)
    address_keywords = [
        r'jalan\s+[^,\n]+', r'jl\.?\s+[^,\n]+',
        r'alamat\s*:?\s*[^,\n]+', r'alamat\s+[^,\n]+',
        r'kota\s+[^,\n]+', r'kabupaten\s+[^,\n]+',
        r'provinsi\s+[^,\n]+', r'kelurahan\s+[^,\n]+',
        r'kecamatan\s+[^,\n]+'
    ]
    
    for pattern in address_keywords:
        addresses = re.findall(pattern, text, re.IGNORECASE)
        contact_info['addresses'].extend([clean_text(addr) for addr in addresses])
    
    contact_info['addresses'] = list(set(contact_info['addresses']))
    
    return contact_info

def is_valid_url(url: str) -> bool:
    """
    Validasi format URL
    
    Args:
        url (str): URL yang akan divalidasi
        
    Returns:
        bool: True jika URL valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def format_scraped_data(data: Dict) -> str:
    """
    Format data hasil scraping menjadi string yang mudah dibaca
    
    Args:
        data (Dict): Data hasil scraping
        
    Returns:
        str: Data yang diformat
    """
    output = []
    output.append(f"=== HASIL SCRAPING ===")
    output.append(f"URL: {data.get('url', 'N/A')}")
    output.append(f"Domain: {data.get('domain', 'N/A')}")
    output.append(f"Judul: {data.get('title', 'N/A')}")
    output.append(f"Status: {data.get('status', 'N/A')}")
    output.append(f"Halaman di-scrape: {data.get('scraped_pages', 0)}")
    output.append(f"Waktu scraping: {data.get('timestamp', 'N/A')}")
    output.append("")
    
    if data.get('description'):
        output.append(f"Deskripsi: {data['description']}")
        output.append("")
    
    if data.get('contact_info'):
        contact = data['contact_info']
        if any(contact.values()):
            output.append("=== INFORMASI KONTAK ===")
            if contact.get('emails'):
                output.append(f"Email: {', '.join(contact['emails'])}")
            if contact.get('phones'):
                output.append(f"Telepon: {', '.join(contact['phones'])}")
            if contact.get('addresses'):
                output.append("Alamat:")
                for addr in contact['addresses'][:3]:  # Maksimal 3 alamat
                    output.append(f"  - {addr}")
            output.append("")
    
    if data.get('links'):
        output.append(f"Jumlah link ditemukan: {len(data['links'])}")
        output.append("")
    
    if data.get('images'):
        output.append(f"Jumlah gambar ditemukan: {len(data['images'])}")
        output.append("")
    
    if data.get('content'):
        content_preview = data['content'][:500] + "..." if len(data['content']) > 500 else data['content']
        output.append("=== PREVIEW KONTEN ===")
        output.append(content_preview)
    
    return "\n".join(output)