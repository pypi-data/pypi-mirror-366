"""
Setup script for TikTok Reup Package
"""
import os
from setuptools import setup, find_packages

# Read the contents of README file
current_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A modular Python package for downloading and uploading TikTok videos"

# Read requirements
try:
    with open(os.path.join(current_directory, 'requirements.txt'), encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
except FileNotFoundError:
    requirements = [
        'requests>=2.31.0',
        'tqdm>=4.65.0', 
        'colorama>=0.4.6',
        'yt-dlp>=2023.7.6',
        'selenium>=4.15.0',
        'webdriver-manager>=4.0.1',
        'urllib3>=1.26.0',
        'certifi>=2023.7.22'
    ]

setup(
    name="tiktok-reup",
    version="2.0.0",
    author="xuancuong2006",
    author_email="xuancuong2006@gmail.com",
    description="A modular Python package for downloading and uploading TikTok videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuancuong2006/tiktok-reup",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tiktok-reup=tiktok_reup.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        'tiktok_reup': ['*.md', '*.txt'],
    },
    keywords=[
        'tiktok', 
        'video', 
        'download', 
        'upload', 
        'social media', 
        'automation', 
        'scraping'
    ],
    project_urls={
        "Bug Reports": "https://github.com/xuancuong2006/tiktok-reup/issues",
        "Source": "https://github.com/xuancuong2006/tiktok-reup",
        "Telegram": "https://t.me/xuancuong2006",
    },
)
