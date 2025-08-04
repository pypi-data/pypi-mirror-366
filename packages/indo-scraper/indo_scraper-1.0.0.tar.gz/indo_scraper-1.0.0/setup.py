# setup.py
from setuptools import setup, find_packages

# Baca README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Baca requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh.readlines() if line.strip()]

setup(
    name="indo-scraper",
    version="1.0.0",
    author="ADE PRATAMA",
    author_email="adepratama20071907@gmail.com",
    description="Library Python untuk scraping website Indonesia dengan mudah",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adepratama840/indo-scraper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="scraping, indonesia, web scraping, data extraction, website",
    project_urls={
        "Bug Reports": "https://github.com/adepratama840/indo-scraper/issues",
        "Source": "https://github.com/adepratama840/indo-scraper",
        "Documentation": "https://github.com/adepratama840/indo-scraper/wiki",
    },
    entry_points={
        'console_scripts': [
            'indo-scraper=indo_scraper.cli:main',
        ],
    },
)