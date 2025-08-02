"""
Configuration settings for TikTok downloader/uploader
"""

# Default settings
DEFAULT_DOWNLOAD_FOLDER = "downloads"
DEFAULT_UPLOAD_DELAY = 15  # seconds between uploads
MAX_CAPTION_LENGTH = 2200
MAX_SCROLLS = 5
UPLOAD_TIMEOUT = 120  # seconds

# Chrome options for headless browsing
CHROME_OPTIONS_HEADLESS = [
    "--headless",
    "--no-sandbox", 
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-features=TranslateUI",
    "--disable-ipc-flooding-protection",
    "--disable-web-security",
    "--disable-features=VizDisplayCompositor",
    "--disable-extensions",
    "--disable-plugins",
    "--window-size=1920,1080",
    "--log-level=3",
    "--silent",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Chrome options for upload (visible browser)
CHROME_OPTIONS_UPLOAD = [
    "--no-sandbox",
    "--disable-dev-shm-usage", 
    "--disable-blink-features=AutomationControlled",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--disable-features=VizDisplayCompositor",
    "--window-size=1920,1080",
    "--start-maximized",
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Request headers
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# API endpoints for video downloading
API_ENDPOINTS = [
    "https://tikwm.com/api/user/info?unique_id={username}",
    "https://www.tikwm.com/api/user/info?unique_id={username}",
    "https://api.douyin.wtf/api/user/{username}",
]

# Download API endpoints
DOWNLOAD_API_ENDPOINTS = [
    {
        'url': 'https://tikwm.com/api/',
        'params': {'url': '{video_url}', 'hd': 1}
    },
    {
        'url': 'https://www.tikwm.com/api/',
        'params': {'url': '{video_url}', 'hd': 1}
    },
    {
        'url': 'https://api.douyin.wtf/api',
        'params': {'url': '{video_url}'}
    },
    {
        'url': 'https://api.tiklydown.eu.org/api/download',
        'params': {'url': '{video_url}'}
    }
]

# yt-dlp options
YT_DLP_OPTIONS = {
    'format': 'best[ext=mp4]/best[ext=webm]/best',
    'writeinfojson': False,
    'writesubtitles': False,
    'writeautomaticsub': False,
    'ignoreerrors': True,
    'no_warnings': True,
    'quiet': True,
    'extractaudio': False,
    'embed_subs': False,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    },
    'extractor_args': {
        'tiktok': {
            'api_hostname': 'api.tiktokv.com',
            'app_version': '34.1.2',
            'device_id': None
        }
    }
}

# CSS selectors for TikTok elements
SELECTORS = {
    'video_links': [
        'a[href*="/video/"]',
        'div[data-e2e="user-post-item"] a',
        '[data-e2e="user-post-item-list"] a',
        'div.tiktok-1s50w6p-DivWrapper a'
    ],
    'upload_file_input': "input[type='file']",
    'caption_input': [
        "div[contenteditable='true']",
        "textarea",
        "[data-e2e='video-caption']",
        ".public-DraftEditor-content",
        "[placeholder*='caption']",
        "[placeholder*='describe']"
    ],
    'publish_button': [
        "button[data-e2e='post_video_button']",
        "button[data-e2e='post_video_button'][role='button']",
        "[data-e2e='post_video_button']",
        "button:has(.Button__content:contains('Post'))",
        "button .Button__content:contains('Post')",
        ".Button__content:contains('Post')",
        "button.Button__root--type-primary",
        "button[class*='Button__root'][class*='primary']",
        "button[class*='Button__root--type-primary']",
        "[data-e2e='publish-button']",
        "button[data-e2e='publish-button']",
        "[data-e2e='post-button']",
        "button[data-e2e='post-button']",
        "[aria-label='Post']",
        "[aria-label='Publish']",
        "button[type='submit']",
        ".publish-button",
        ".post-button",
        "button.publish-button",
        "button.post-button",
        "button[class*='publish']",
        "button[class*='post']",
        "div[class*='publish'] button",
        "div[class*='post'] button"
    ]
}

# Text selectors for publish button
PUBLISH_BUTTON_TEXTS = [
    ("Post", "button"),
    ("Publish", "button"),
    ("发布", "button"),  # Chinese
    ("Publicar", "button"),  # Spanish
    ("Publier", "button"),  # French
    ("Veröffentlichen", "button")  # German
]

# Upload success indicators
UPLOAD_SUCCESS_INDICATORS = [
    "//span[contains(text(), 'Uploaded')]",
    "//span[contains(text(), 'uploaded')]",
    "//*[contains(text(), 'Uploaded') and contains(text(), 'KB')]",
    "//*[contains(text(), 'Uploaded') and contains(text(), 'MB')]",
    "//span[@class='TUXText TUXText--tiktok-sans' and contains(text(), 'Uploaded')]"
]
