# TikTok Reup - Python Package

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Package Version](https://img.shields.io/badge/version-2.0.0-orange.svg)](https://github.com/xuancuong2006/tiktok-reup)

A modular Python package for downloading and uploading TikTok videos with enhanced organization and maintainability.

## 🌟 Features

- **📁 Modular Architecture**: Clean separation of concerns with organized modules
- **⬇️ Download TikTok Videos**: Download videos from any TikTok user profile
- **🎯 Single Video Download**: Download individual videos by URL
- **⬆️ Automated Upload**: Upload downloaded videos back to TikTok with captions
- **🔄 Bulk Operations**: Handle multiple videos efficiently
- **🔗 Multiple Download Methods**: API scraping and Selenium fallback
- **📝 Caption Management**: Automatic caption extraction and upload
- **📊 Progress Tracking**: Visual progress bars and status updates

## 📦 Installation

### Option 1: Install from Source (Development)

```bash
# Clone the repository
git clone https://github.com/xuancuong2006/tiktok-reup.git
cd tiktok-reup

# Install in development mode
pip install -e .
```

### Option 2: Install as Package

```bash
# Install from local directory
pip install .
```

### Option 3: Install Dependencies Only

```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### As a Python Package

```python
from tiktok_reup import TikTokDownloader, TikTokUploader, SeleniumHandler

# Initialize downloader
downloader = TikTokDownloader("downloads")

# Download videos from a user
downloader.download_user_videos("username", max_videos=10)

# Download single video
downloader.download_single_video("https://www.tiktok.com/@user/video/123456789")

# Initialize uploader
selenium_handler = SeleniumHandler()
uploader = TikTokUploader(selenium_handler)

# Upload videos
uploader.bulk_upload_videos("downloads/username", upload_limit=5)
```

### As a Command Line Tool

```bash
# Run the CLI interface
tiktok-reup

# Or run the module directly
python -m tiktok_reup.cli
```

## 📁 Package Structure

```
tiktok_reup/
├── 📁 api/                    # TikTok API handling
│   ├── __init__.py
│   └── tiktok_api.py
├── 📁 config/                 # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── 📁 core/                   # Core downloader functionality
│   ├── __init__.py
│   └── downloader.py
├── 📁 selenium_handler/       # Browser automation
│   ├── __init__.py
│   └── browser.py
├── 📁 upload/                 # Upload functionality
│   ├── __init__.py
│   └── uploader.py
├── 📁 utils/                  # Utility functions
│   ├── __init__.py
│   └── helpers.py
├── __init__.py               # Package initialization
└── cli.py                    # Command line interface
```

## 🎮 Usage Examples

### Download Examples

```python
from tiktok_reup import TikTokDownloader

# Create downloader instance
downloader = TikTokDownloader("my_downloads")

# Download all videos from a user
downloader.download_user_videos("cooluser123")

# Download limited number of videos
downloader.download_user_videos("cooluser123", max_videos=5)

# Download single video with custom filename
downloader.download_single_video(
    "https://www.tiktok.com/@user/video/123456789",
    custom_filename="my_video"
)
```

### Upload Examples

```python
from tiktok_reup import TikTokUploader, SeleniumHandler

# Initialize selenium handler and uploader
selenium_handler = SeleniumHandler()
uploader = TikTokUploader(selenium_handler)

# Login to TikTok (manual browser login)
uploader.login_to_tiktok()

# Upload videos from a folder
uploader.bulk_upload_videos("downloads/username")

# Upload with limit
uploader.bulk_upload_videos("downloads/username", upload_limit=3)
```

### Configuration

```python
from tiktok_reup import settings

# Access configuration
print(settings.DEFAULT_DOWNLOAD_FOLDER)
print(settings.MAX_CAPTION_LENGTH)

# Modify settings (if needed)
settings.DEFAULT_UPLOAD_DELAY = 20  # seconds between uploads
```

## 🔧 API Reference

### TikTokDownloader

```python
class TikTokDownloader:
    def __init__(self, download_folder="downloads"):
        """Initialize downloader with custom download folder"""
    
    def download_user_videos(self, username, max_videos=None):
        """Download all videos from a TikTok user"""
    
    def download_single_video(self, video_url, custom_filename=None):
        """Download a single video by URL"""
    
    def close_browser(self):
        """Close any open browser instances"""
```

### TikTokUploader

```python
class TikTokUploader:
    def __init__(self, selenium_handler):
        """Initialize uploader with selenium handler"""
    
    def login_to_tiktok(self):
        """Login to TikTok (manual browser login)"""
    
    def upload_video(self, video_path, caption_path, custom_caption=None):
        """Upload a single video with caption"""
    
    def bulk_upload_videos(self, user_folder, upload_limit=None):
        """Upload multiple videos from folder"""
```

## ⚙️ Configuration

### Settings File (`config/settings.py`)

```python
# Default settings
DEFAULT_DOWNLOAD_FOLDER = "downloads"
DEFAULT_UPLOAD_DELAY = 15  # seconds between uploads
MAX_CAPTION_LENGTH = 2200
MAX_SCROLLS = 5
UPLOAD_TIMEOUT = 120  # seconds

# Browser options
CHROME_OPTIONS_HEADLESS = [...]  # Headless browsing options
CHROME_OPTIONS_UPLOAD = [...]    # Upload browsing options

# API endpoints
API_ENDPOINTS = [...]  # TikTok API endpoints
```

## 📋 Requirements

- Python 3.8+
- Google Chrome browser (for Selenium)
- All packages listed in `requirements.txt`:
  - requests>=2.31.0
  - tqdm>=4.65.0
  - colorama>=0.4.6
  - yt-dlp>=2023.7.6
  - selenium>=4.15.0
  - webdriver-manager>=4.0.1
  - urllib3>=1.26.0
  - certifi>=2023.7.22

## 🔒 Security & Privacy

- **Manual Login**: Upload functionality requires manual login for security
- **No Credentials Stored**: The package does not store any login credentials
- **Respectful Usage**: Built-in delays to avoid rate limiting
- **Terms Compliance**: Please respect TikTok's Terms of Service

## 🛠️ Development

### Install for Development

```bash
# Clone repository
git clone https://github.com/xuancuong2006/tiktok-reup.git
cd tiktok-reup

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements.txt
```

### Building the Package

```bash
# Build distribution packages
python -m build

# Install locally
pip install dist/tiktok_reup-2.0.0-py3-none-any.whl
```

### Running Tests

```bash
# Run the CLI interface
python -m tiktok_reup.cli

# Or use the installed command
tiktok-reup
```

## 📚 Module Descriptions

### Core Module (`core/downloader.py`)
- Main `TikTokDownloader` class
- Video downloading logic
- User video scanning
- File management

### API Module (`api/tiktok_api.py`)
- `TikTokAPI` class for API interactions
- Multiple API endpoint handling
- Direct URL downloading
- JSON response parsing

### Selenium Handler (`selenium_handler/browser.py`)
- `SeleniumHandler` class for browser automation
- User profile scraping
- Upload automation
- Login management

### Upload Module (`upload/uploader.py`)
- `TikTokUploader` class for upload operations
- Bulk upload functionality
- Caption processing
- Upload status tracking

### Utils Module (`utils/helpers.py`)
- Utility functions used across modules
- File naming and sanitization
- Caption processing
- BMP character filtering

### Config Module (`config/settings.py`)
- Centralized configuration
- Browser options
- API endpoints
- CSS selectors

## 🚨 Troubleshooting

### Common Issues

1. **Chrome Driver Issues**
   ```bash
   # Update webdriver-manager
   pip install --upgrade webdriver-manager
   ```

2. **Import Errors**
   ```bash
   # Reinstall package
   pip uninstall tiktok-reup
   pip install -e .
   ```

3. **Upload Issues**
   - Ensure Chrome browser is installed
   - Check TikTok login status
   - Verify internet connection

### Getting Help

- 📱 **Telegram**: [t.me/xuancuong2006](https://t.me/xuancuong2006)
- 🐛 **Issues**: [GitHub Issues](https://github.com/xuancuong2006/tiktok-reup/issues)
- 📖 **Documentation**: See source code comments

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational purposes only. Please respect TikTok's Terms of Service and applicable laws when using this software. The authors are not responsible for any misuse of this software.

## 👨‍💻 Author

Created by **xuancuong2006**
- 📱 Telegram: [t.me/xuancuong2006](https://t.me/xuancuong2006)
- 🐙 GitHub: [xuancuong2006](https://github.com/xuancuong2006)

---

⭐ **Star this repository if you find it helpful!**
