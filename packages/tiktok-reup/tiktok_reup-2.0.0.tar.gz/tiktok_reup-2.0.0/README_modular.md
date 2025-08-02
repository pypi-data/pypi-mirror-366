# TikTok Video Reup - Modular Version

A modular Python application for downloading and uploading TikTok videos with enhanced organization and maintainability.

## Features

- **Modular Architecture**: Clean separation of concerns with organized modules
- **Download TikTok Videos**: Download videos from any TikTok user profile
- **Single Video Download**: Download individual videos by URL
- **Automated Upload**: Upload downloaded videos back to TikTok with captions
- **Bulk Operations**: Handle multiple videos efficiently
- **Multiple Download Methods**: API scraping and Selenium fallback
- **Caption Management**: Automatic caption extraction and upload
- **Progress Tracking**: Visual progress bars and status updates

## Project Structure

```
├── api/                    # TikTok API handling
│   ├── __init__.py
│   └── tiktok_api.py
├── config/                 # Configuration settings
│   ├── __init__.py
│   └── settings.py
├── core/                   # Core downloader functionality
│   ├── __init__.py
│   └── downloader.py
├── selenium_handler/       # Browser automation
│   ├── __init__.py
│   └── browser.py
├── upload/                 # Upload functionality
│   ├── __init__.py
│   └── uploader.py
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── helpers.py
├── main_modular.py         # Main entry point (modular version)
├── main.py                 # Original monolithic version
├── requirements.txt        # Dependencies
└── README_modular.md       # This file
```

## Installation

1. **Clone or download the project**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the modular version**:
   ```bash
   python main_modular.py
   ```

## Usage

Run the modular version:
```bash
python main_modular.py
```

The application will present you with options:
1. **Download videos from TikTok user** - Download all videos from a specific user
2. **Download single TikTok video by URL** - Download one specific video
3. **Upload downloaded videos to TikTok** - Upload previously downloaded videos
4. **Download and then upload videos** - Complete workflow

## Module Descriptions

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

## Key Improvements in Modular Version

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to modify and extend individual components
3. **Reusability**: Modules can be imported and used independently
4. **Testability**: Individual modules can be unit tested
5. **Readability**: Smaller, focused files are easier to understand
6. **Configuration Management**: Centralized settings in config module

## Configuration

You can modify settings in `config/settings.py`:
- Browser options
- API endpoints
- CSS selectors
- Timeouts and delays
- File naming patterns

## Requirements

- Python 3.8+
- Chrome browser (for Selenium)
- All packages listed in `requirements.txt`

## Notes

- The original monolithic version (`main.py`) is preserved for reference
- All functionality from the original version is maintained
- The modular version provides the same user interface
- Browser automation requires manual login for security

## Author

Created by xuancuong2006 (t.me/xuancuong2006)

## License

This project is for educational purposes. Please respect TikTok's terms of service.
