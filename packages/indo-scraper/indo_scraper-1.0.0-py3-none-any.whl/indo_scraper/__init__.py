# indo_scraper/__init__.py
"""
Indonesian Web Scraper Library
Library untuk scraping data website Indonesia dengan mudah
"""

__version__ = "1.0.0"
__author__ = "ADE PRATAMA"
__email__ = "adepratama20071907@gmail.com"

from .scraper import IndoScraper
from .utils import validate_indonesian_domain, clean_text, extract_contact_info

__all__ = ['IndoScraper', 'validate_indonesian_domain', 'clean_text', 'extract_contact_info']