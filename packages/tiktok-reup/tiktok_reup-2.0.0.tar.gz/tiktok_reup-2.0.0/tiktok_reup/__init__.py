"""
TikTok Reup Package
A modular Python package for downloading and uploading TikTok videos.

Author: xuancuong2006 (t.me/xuancuong2006)
Version: 2.0.0
"""

__version__ = "2.0.0"
__author__ = "xuancuong2006"
__email__ = "t.me/xuancuong2006"
__description__ = "A modular Python package for downloading and uploading TikTok videos"

# Import main classes for easy access
from .core.downloader import TikTokDownloader
from .upload.uploader import TikTokUploader
from .selenium_handler.browser import SeleniumHandler
from .api.tiktok_api import TikTokAPI

# Import configuration
from .config import settings

# Define what gets imported with "from tiktok_reup import *"
__all__ = [
    'TikTokDownloader',
    'TikTokUploader', 
    'SeleniumHandler',
    'TikTokAPI',
    'settings'
]

def get_version():
    """Return the version of the package"""
    return __version__

def get_info():
    """Return package information"""
    return {
        'name': 'tiktok-reup',
        'version': __version__,
        'author': __author__,
        'description': __description__,
        'contact': __email__
    }
