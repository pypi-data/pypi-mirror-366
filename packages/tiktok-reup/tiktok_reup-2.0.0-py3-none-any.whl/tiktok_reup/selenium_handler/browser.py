"""
Selenium browser automation for TikTok operations
"""
import time
import warnings
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from colorama import Fore

from ..config.settings import (
    CHROME_OPTIONS_HEADLESS, 
    CHROME_OPTIONS_UPLOAD, 
    MAX_SCROLLS, 
    SELECTORS,
    PUBLISH_BUTTON_TEXTS,
    UPLOAD_SUCCESS_INDICATORS,
    UPLOAD_TIMEOUT
)
from ..utils.helpers import filter_bmp_characters

# Suppress warnings and set logging level
warnings.filterwarnings("ignore")
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('WDM').setLevel(logging.ERROR)


class SeleniumHandler:
    def __init__(self):
        self.upload_driver = None
        self.is_logged_in = False

    def get_user_videos_selenium(self, username):
        """
        Get user videos using Selenium (fallback method)
        
        Args:
            username (str): TikTok username (without @)
            
        Returns:
            list: List of video URLs
        """
        print(f"{Fore.YELLOW}Trying Selenium approach for @{username}...")
        
        # Setup Chrome options for headless browsing
        chrome_options = Options()
        for option in CHROME_OPTIONS_HEADLESS:
            chrome_options.add_argument(option)
        
        # Suppress additional Chrome logs
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            # Initialize webdriver with suppressed logging
            service = Service(ChromeDriverManager().install())
            service.creation_flags = 0x08000000  # CREATE_NO_WINDOW flag for Windows
            
            # Suppress WebDriver logs
            logging.getLogger('selenium').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Navigate to user profile
            profile_url = f"https://www.tiktok.com/@{username}"
            driver.get(profile_url)
            
            # Wait for page to load
            time.sleep(8)
            
            video_urls = set()
            scroll_count = 0
            
            while scroll_count < MAX_SCROLLS:
                # Find video links with multiple selectors
                for selector in SELECTORS['video_links']:
                    try:
                        video_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in video_elements:
                            href = element.get_attribute('href')
                            if href and '/video/' in href:
                                video_urls.add(href)
                    except:
                        continue
                
                # Scroll down to load more videos
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(4)
                scroll_count += 1
                
                print(f"{Fore.YELLOW}Found {len(video_urls)} videos so far... (scroll {scroll_count}/{MAX_SCROLLS})")
            
            driver.quit()
            
            video_list = list(video_urls)
            print(f"{Fore.GREEN}Total videos found: {len(video_list)}")
            return video_list
            
        except Exception as e:
            print(f"{Fore.RED}Error scanning user profile: {str(e)}")
            if 'driver' in locals():
                driver.quit()
            return []

    def setup_upload_driver(self):
        """Setup Chrome driver for TikTok upload (with visible browser)"""
        try:
            chrome_options = Options()
            # Don't use headless mode for upload to avoid detection
            for option in CHROME_OPTIONS_UPLOAD:
                chrome_options.add_argument(option)
            
            # Anti-detection measures
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            # Prefs to avoid save password popup and other distractions
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            service = Service(ChromeDriverManager().install())
            self.upload_driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute scripts to remove automation indicators
            self.upload_driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.upload_driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            self.upload_driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            # Set implicit wait for better element handling
            self.upload_driver.implicitly_wait(10)
            
            print(f"{Fore.GREEN}Upload browser initialized successfully")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Failed to setup upload driver: {str(e)}")
            return False

    def login_to_tiktok(self):
        """
        Log into TikTok account using browser-based manual login only
        
        Returns:
            bool: Login success status
        """
        try:
            if not self.upload_driver:
                if not self.setup_upload_driver():
                    return False
            
            print(f"{Fore.CYAN}Opening TikTok login page...")
            print(f"{Fore.YELLOW}⚠️  You will need to login manually in the browser window that opens.")
            
            self.upload_driver.get("https://www.tiktok.com/login")
            
            # Wait for page to load
            time.sleep(3)
            
            print(f"{Fore.CYAN}Please complete the following steps in the browser:")
            print(f"{Fore.YELLOW}1. Choose your login method (email, phone, QR code, etc.)")
            print(f"{Fore.YELLOW}2. Enter your credentials")
            print(f"{Fore.YELLOW}3. Complete any 2FA or captcha if required")
            print(f"{Fore.YELLOW}4. Wait to be redirected to the main TikTok page")
            print(f"{Fore.CYAN}Then return here and press Enter...")
            
            # Wait for manual login completion
            input(f"{Fore.GREEN}Press Enter after you've successfully logged in...")
            
            # Verify login by checking current URL and page elements
            print(f"{Fore.YELLOW}Verifying login status...")
            
            try:
                current_url = self.upload_driver.current_url
                print(f"{Fore.CYAN}Current URL: {current_url}")
                
                # Check multiple indicators of successful login
                login_indicators = [
                    # URL-based checks
                    "login" not in current_url.lower(),
                    "tiktok.com" in current_url.lower() and "/login" not in current_url.lower(),
                    
                    # Element-based checks
                    bool(self.upload_driver.find_elements(By.CSS_SELECTOR, "[data-e2e='nav-upload']")),
                    bool(self.upload_driver.find_elements(By.CSS_SELECTOR, "[data-e2e='upload-icon']")),
                    bool(self.upload_driver.find_elements(By.CSS_SELECTOR, "a[href*='/upload']")),
                    bool(self.upload_driver.find_elements(By.CSS_SELECTOR, "[aria-label*='Upload']")),
                    bool(self.upload_driver.find_elements(By.CSS_SELECTOR, "[data-e2e='profile-icon']")),
                    bool(self.upload_driver.find_elements(By.CSS_SELECTOR, "[data-e2e='nav-profile']")),
                ]
                
                # If any indicator shows we're logged in
                if any(login_indicators):
                    self.is_logged_in = True
                    print(f"{Fore.GREEN}✅ Login verification successful!")
                    print(f"{Fore.GREEN}✅ You are now logged into TikTok!")
                    return True
                else:
                    print(f"{Fore.RED}❌ Login verification failed.")
                    print(f"{Fore.YELLOW}⚠️  It looks like you might not be logged in yet.")
                    
                    # Give user another chance
                    retry = input(f"{Fore.YELLOW}Try verification again? (y/n): ").strip().lower()
                    if retry in ['y', 'yes']:
                        # Wait a bit more and try again
                        time.sleep(5)
                        current_url = self.upload_driver.current_url
                        if "login" not in current_url.lower() and "tiktok.com" in current_url.lower():
                            self.is_logged_in = True
                            print(f"{Fore.GREEN}✅ Login verified on retry!")
                            return True
                    
                    print(f"{Fore.RED}❌ Login not confirmed. Please try logging in again.")
                    return False
                    
            except Exception as e:
                print(f"{Fore.RED}Error during login verification: {str(e)}")
                print(f"{Fore.YELLOW}You may still be logged in. Try using upload features to test.")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Login process failed: {str(e)}")
            return False

    def upload_video(self, video_path, caption_text):
        """
        Upload a video to TikTok with its caption (fully automated)
        
        Args:
            video_path (str): Path to video file
            caption_text (str): Caption text to use
            
        Returns:
            bool: Upload success status
        """
        try:
            if not self.is_logged_in:
                print(f"{Fore.RED}Not logged in to TikTok. Please login first.")
                return False
            
            import os
            
            print(f"{Fore.CYAN}Uploading: {os.path.basename(video_path)}")
            print(f"{Fore.CYAN}Caption: {caption_text[:100]}{'...' if len(caption_text) > 100 else ''}")
            
            # Navigate to upload page
            self.upload_driver.get("https://www.tiktok.com/upload")
            time.sleep(3)
            
            # Find file input and upload video
            try:
                file_input = WebDriverWait(self.upload_driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS['upload_file_input']))
                )
                file_input.send_keys(os.path.abspath(video_path))
                
                print(f"{Fore.YELLOW}Video uploading... Please wait...")
                
                # Wait for video to upload successfully by checking for "Uploaded" text
                upload_success = False
                max_wait_time = UPLOAD_TIMEOUT  # Maximum wait time in seconds
                check_interval = 2   # Check every 2 seconds
                
                for i in range(0, max_wait_time, check_interval):
                    try:
                        # Check for upload success indicator
                        for xpath in UPLOAD_SUCCESS_INDICATORS:
                            elements = self.upload_driver.find_elements(By.XPATH, xpath)
                            for element in elements:
                                if element.is_displayed() and "Uploaded" in element.text:
                                    print(f"{Fore.GREEN}✓ Upload completed: {element.text}")
                                    upload_success = True
                                    break
                            if upload_success:
                                break
                        
                        if upload_success:
                            break
                            
                        # Also check if we can already see caption input (backup check)
                        caption_ready = False
                        for selector in SELECTORS['caption_input']:
                            try:
                                element = self.upload_driver.find_element(By.CSS_SELECTOR, selector)
                                if element.is_displayed() and element.is_enabled():
                                    caption_ready = True
                                    break
                            except:
                                continue
                        
                        if caption_ready:
                            print(f"{Fore.GREEN}✓ Caption input ready (backup detection)")
                            upload_success = True
                            break
                            
                    except Exception as e:
                        pass  # Continue checking
                    
                    time.sleep(check_interval)
                    if i % 10 == 0:  # Print status every 10 seconds
                        print(f"{Fore.YELLOW}Still uploading... ({i}/{max_wait_time}s)")
                
                if not upload_success:
                    print(f"{Fore.RED}Upload timeout - video may still be processing")
                    return False
                
                # Additional small wait for UI to stabilize
                time.sleep(2)
                
                # Find caption textarea
                caption_element = None
                for selector in SELECTORS['caption_input']:
                    try:
                        caption_element = self.upload_driver.find_element(By.CSS_SELECTOR, selector)
                        if caption_element.is_displayed() and caption_element.is_enabled():
                            break
                    except:
                        continue
                
                if not caption_element:
                    print(f"{Fore.RED}Could not find caption input field")
                    return False
                
                # Clear and enter caption
                caption_element.click()
                time.sleep(1)
                
                # Clear existing text
                caption_element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.5)
                caption_element.send_keys(Keys.DELETE)
                time.sleep(1)
                
                # Type the caption using safe method
                self.safe_send_keys(caption_element, caption_text, "caption")
                
                # Look for publish/post button and click it automatically
                print(f"{Fore.YELLOW}Looking for publish button...")
                
                publish_clicked = False
                publish_button = None
                
                # Try direct selectors first
                for selector in SELECTORS['publish_button']:
                    try:
                        elements = self.upload_driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                publish_button = element
                                print(f"{Fore.GREEN}Found publish button using selector: {selector}")
                                break
                        if publish_button:
                            break
                    except Exception as e:
                        continue
                
                # If no button found, try text-based selectors
                if not publish_button:
                    for text, tag in PUBLISH_BUTTON_TEXTS:
                        try:
                            # Try standard text search
                            xpath = f"//{tag}[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
                            elements = self.upload_driver.find_elements(By.XPATH, xpath)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    publish_button = element
                                    print(f"{Fore.GREEN}Found publish button using text: {text}")
                                    break
                            if publish_button:
                                break
                        except:
                            continue
                
                # Additional search for buttons with nested text content
                if not publish_button:
                    try:
                        nested_selectors = [
                            "button:has(div:contains('Post'))",
                            "button[role='button']:has(div:contains('Post'))",
                            "button .Button__content:contains('Post')",
                            "//button[.//div[contains(text(), 'Post')]]",
                            "//button[@role='button'][.//div[contains(translate(text(), 'POST', 'post'), 'post')]]",
                            "//button[@data-e2e='post_video_button']",
                            "//button[contains(@class, 'Button__root')][.//div[contains(text(), 'Post')]]"
                        ]
                        
                        for selector in nested_selectors:
                            try:
                                if selector.startswith("//"):
                                    # XPath selector
                                    elements = self.upload_driver.find_elements(By.XPATH, selector)
                                else:
                                    # CSS selector (may not work for :has() in all browsers)
                                    try:
                                        elements = self.upload_driver.find_elements(By.CSS_SELECTOR, selector)
                                    except:
                                        continue
                                
                                for element in elements:
                                    if element.is_displayed() and element.is_enabled():
                                        publish_button = element
                                        print(f"{Fore.GREEN}Found publish button using nested selector: {selector}")
                                        break
                                if publish_button:
                                    break
                            except:
                                continue
                    except Exception as e:
                        print(f"{Fore.YELLOW}Error in nested button search: {str(e)}")
                
                # Try to click the publish button
                if publish_button:
                    try:
                        # Scroll to button to ensure it's visible
                        self.upload_driver.execute_script("arguments[0].scrollIntoView(true);", publish_button)
                        time.sleep(1)
                        
                        # Try regular click first
                        publish_button.click()
                        publish_clicked = True
                        print(f"{Fore.GREEN}✓ Publish button clicked successfully")
                    except Exception as e:
                        try:
                            # Fallback to JavaScript click
                            self.upload_driver.execute_script("arguments[0].click();", publish_button)
                            publish_clicked = True
                            print(f"{Fore.GREEN}✓ Publish button clicked using JavaScript")
                        except Exception as e2:
                            print(f"{Fore.RED}Failed to click publish button: {str(e2)}")
                else:
                    print(f"{Fore.RED}Could not find any publish button")
                
                if publish_clicked:
                    print(f"{Fore.GREEN}✓ Publish button clicked successfully!")
                    print(f"{Fore.GREEN}✓ Upload submitted - continuing to next video...")
                    return True
                
                else:
                    print(f"{Fore.RED}❌ Could not find or click publish button")
                    print(f"{Fore.YELLOW}Manual intervention may be required")
                    print(f"{Fore.YELLOW}The video has been uploaded but may need manual publishing")
                    
                    # Wait a bit and return false to indicate manual intervention needed
                    time.sleep(5)
                    return False
                
            except Exception as e:
                print(f"{Fore.RED}Upload process failed: {str(e)}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Upload failed: {str(e)}")
            return False

    def safe_send_keys(self, element, text, description="text"):
        """
        Safely send keys to an element with proper error handling for encoding issues
        
        Args:
            element: WebDriver element
            text (str): Text to send
            description (str): Description for logging
            
        Returns:
            bool: Success status
        """
        try:
            # First filter the text
            filtered_text = filter_bmp_characters(text)
            
            # Try to send the text
            element.send_keys(filtered_text)
            print(f"{Fore.GREEN}✓ {description} entered successfully")
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"{Fore.YELLOW}Warning: Error entering {description}: {error_msg}")
            
            # Handle specific ChromeDriver BMP error
            if "BMP" in error_msg or "characters" in error_msg:
                print(f"{Fore.YELLOW}Detected character encoding issue, trying ASCII-only text...")
                try:
                    # Try with ASCII-only text
                    ascii_text = text.encode('ascii', 'ignore').decode('ascii')
                    if ascii_text.strip():
                        element.send_keys(ascii_text)
                        print(f"{Fore.GREEN}✓ {description} entered with ASCII fallback")
                        return True
                    else:
                        # Use default text if ASCII conversion results in empty string
                        element.send_keys("Repost")
                        print(f"{Fore.GREEN}✓ Default {description} entered")
                        return True
                except Exception as e2:
                    print(f"{Fore.RED}ASCII fallback also failed: {str(e2)}")
            
            # Final fallback
            try:
                element.send_keys("Repost")
                print(f"{Fore.GREEN}✓ Fallback {description} entered")
                return True
            except:
                print(f"{Fore.RED}All {description} entry methods failed")
                return False

    def close_upload_driver(self):
        """Close the upload browser driver"""
        try:
            if self.upload_driver:
                self.upload_driver.quit()
                self.upload_driver = None
                self.is_logged_in = False
                print(f"{Fore.GREEN}Upload browser closed")
        except:
            pass
