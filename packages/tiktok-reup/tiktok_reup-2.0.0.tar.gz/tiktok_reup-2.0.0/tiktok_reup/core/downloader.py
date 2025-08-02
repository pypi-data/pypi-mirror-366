"""
Core TikTok downloader functionality
"""
import os
import re
import time
import yt_dlp
from colorama import Fore
from ..config.settings import YT_DLP_OPTIONS, DEFAULT_DOWNLOAD_FOLDER
from ..utils.helpers import (
    sanitize_filename, 
    save_video_caption, 
    create_folder_if_not_exists,
    extract_video_info_from_url
)
from ..api.tiktok_api import TikTokAPI
from ..selenium_handler.browser import SeleniumHandler


class TikTokDownloader:
    def __init__(self, download_folder=DEFAULT_DOWNLOAD_FOLDER):
        """
        Initialize TikTok downloader
        
        Args:
            download_folder (str): Base folder to save downloaded videos
        """
        self.base_download_folder = download_folder
        self.create_base_folder()
        self.api = TikTokAPI()
        self.selenium_handler = SeleniumHandler()
        
    def create_base_folder(self):
        """Create base download folder if it doesn't exist"""
        create_folder_if_not_exists(self.base_download_folder)
    
    def create_user_folder(self, username):
        """Create user-specific folder and return path"""
        user_folder = os.path.join(self.base_download_folder, username)
        create_folder_if_not_exists(user_folder)
        return user_folder
    
    def get_user_videos(self, username):
        """
        Get all video URLs from a TikTok user profile
        
        Args:
            username (str): TikTok username (without @)
            
        Returns:
            list: List of video URLs
        """
        print(f"{Fore.CYAN}Scanning videos from @{username}...")
        
        # First try the API approach
        api_videos = self.api.get_user_videos_api(username)
        if api_videos:
            return api_videos
        
        # Fallback to Selenium approach
        return self.selenium_handler.get_user_videos_selenium(username)
    
    def download_video_yt_dlp(self, video_url, filename, user_folder):
        """
        Download video using yt-dlp (primary method)
        
        Args:
            video_url (str): TikTok video URL
            filename (str): Output filename
            user_folder (str): User-specific folder path
            
        Returns:
            bool: Success status
        """
        try:
            # Updated yt-dlp options for TikTok
            ydl_opts = YT_DLP_OPTIONS.copy()
            ydl_opts['outtmpl'] = os.path.join(user_folder, f"{filename}.%(ext)s")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # Extract info first to get caption
                    info = ydl.extract_info(video_url, download=False)
                    
                    # Save caption before downloading
                    save_video_caption(info, filename, user_folder)
                    
                    # Now download the video
                    ydl.download([video_url])
                    print(f"{Fore.GREEN}✓ Downloaded successfully")
                    return True
                    
                except Exception as e:
                    print(f"{Fore.YELLOW}failed: {str(e)}")
                    return False
                
        except Exception as e:
            print(f"{Fore.RED}download failed: {str(e)}")
            return False
    
    def download_video_api(self, video_url, filename, user_folder):
        """
        Download video using TikTok API scraping (fallback method)
        
        Args:
            video_url (str): TikTok video URL
            filename (str): Output filename
            user_folder (str): User-specific folder path
            
        Returns:
            bool: Success status
        """
        try:
            # First try to get video info with yt-dlp for caption
            try:
                ydl_opts_info = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    save_video_caption(info, filename, user_folder)
            except:
                print(f"{Fore.YELLOW}Could not extract caption info")
            
            # Use API to download
            return self.api.download_video_api(video_url, filename, user_folder, self.api.download_from_url)
            
        except Exception as e:
            print(f"{Fore.RED}API download failed: {str(e)}")
            return False

    def list_available_formats(self, video_url):
        """
        List available formats for a TikTok video (for debugging)
        
        Args:
            video_url (str): TikTok video URL
            
        Returns:
            list: Available formats
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'listformats': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if 'formats' in info:
                    return info['formats']
                return []
                
        except Exception as e:
            print(f"{Fore.YELLOW}Could not list formats: {str(e)}")
            return []

    def download_user_videos(self, username, max_videos=None):
        """
        Download all videos from a TikTok user
        
        Args:
            username (str): TikTok username
            max_videos (int): Maximum number of videos to download (None for all)
        """
        print(f"{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.MAGENTA}TikTok Video Downloader")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        # Create user-specific folder
        user_folder = self.create_user_folder(username)
        
        print(f"{Fore.CYAN}Target User: @{username}")
        print(f"{Fore.CYAN}Download Folder: {user_folder}")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        # Get video URLs
        video_urls = self.get_user_videos(username)
        
        if not video_urls:
            print(f"{Fore.RED}No videos found for user @{username}")
            return
        
        # Limit videos if specified
        if max_videos and max_videos < len(video_urls):
            video_urls = video_urls[:max_videos]
            print(f"{Fore.YELLOW}Limited to {max_videos} videos")
        
        print(f"\n{Fore.CYAN}Starting download of {len(video_urls)} videos...")
        
        success_count = 0
        failed_count = 0
        
        for i, video_url in enumerate(video_urls, 1):
            print(f"\n{Fore.BLUE}[{i}/{len(video_urls)}] Processing: {video_url}")
            
            # Extract video ID for filename
            video_id = re.search(r'/video/(\d+)', video_url)
            if video_id:
                video_id = video_id.group(1)
                filename = sanitize_filename(f"{username}_{video_id}")
            else:
                filename = sanitize_filename(f"{username}_video_{i}")
            
            # Check if file already exists
            existing_files = [f for f in os.listdir(user_folder) 
                            if f.startswith(filename) and f.endswith(('.mp4', '.webm'))]
            existing_captions = [f for f in os.listdir(user_folder) 
                               if f.startswith(filename) and f.endswith('_caption.txt')]
            
            if existing_files:
                print(f"{Fore.YELLOW}⚠ Video already exists: {existing_files[0]}")
                # Check if caption exists, if not, try to create it
                if not existing_captions:
                    print(f"{Fore.YELLOW}Creating missing caption file...")
                    try:
                        ydl_opts_info = {'quiet': True, 'no_warnings': True}
                        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                            info = ydl.extract_info(video_url, download=False)
                            save_video_caption(info, filename, user_folder)
                    except:
                        print(f"{Fore.YELLOW}Could not create caption file")
                success_count += 1
                continue
            
            # Try downloading with different methods
            download_success = False
            
            # Method 1: yt-dlp with format fallback
            print(f"{Fore.YELLOW}Trying yt-dlp with format fallback...")
            if self.download_video_yt_dlp(video_url, filename, user_folder):
                download_success = True
            
            # Method 2: API scraping (fallback)
            if not download_success:
                print(f"{Fore.YELLOW}Trying API method...")
                if self.download_video_api(video_url, filename, user_folder):
                    download_success = True
            
            # Method 3: Last resort - try yt-dlp with any available format
            if not download_success:
                print(f"{Fore.YELLOW}Trying yt-dlp with any available format...")
                try:
                    # First try to get info for caption
                    try:
                        ydl_opts_info = {'quiet': True, 'no_warnings': True}
                        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                            info = ydl.extract_info(video_url, download=False)
                            save_video_caption(info, filename, user_folder)
                    except:
                        pass
                    
                    ydl_opts = {
                        'outtmpl': os.path.join(user_folder, f"{filename}.%(ext)s"),
                        'format': 'best/worst',  # Accept any format
                        'ignoreerrors': True,
                        'no_warnings': True,
                        'quiet': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([video_url])
                        download_success = True
                        print(f"{Fore.GREEN}✓ Downloaded with fallback format")
                except:
                    pass
            
            if download_success:
                success_count += 1
            else:
                failed_count += 1
                print(f"{Fore.RED}✗ Failed to download video {i}")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        # Summary
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.GREEN}Download Complete!")
        print(f"{Fore.GREEN}Successful: {success_count}")
        print(f"{Fore.RED}Failed: {failed_count}")
        print(f"{Fore.CYAN}Total: {len(video_urls)}")
        print(f"{Fore.CYAN}Download folder: {os.path.abspath(user_folder)}")
        print(f"{Fore.MAGENTA}{'='*50}")

    def download_single_video(self, video_url, custom_filename=None):
        """
        Download a single TikTok video by URL
        
        Args:
            video_url (str): TikTok video URL
            custom_filename (str): Custom filename (optional)
            
        Returns:
            bool: Success status
        """
        try:
            print(f"{Fore.CYAN}Downloading single video: {video_url}")
            
            # Extract username and video ID for filename
            username, video_id = extract_video_info_from_url(video_url)
            
            if username and video_id:
                # Create user folder
                user_folder = self.create_user_folder(username)
                
                # Generate filename
                if custom_filename:
                    filename = sanitize_filename(custom_filename)
                else:
                    filename = sanitize_filename(f"{username}_{video_id}")
                
                # Check if file already exists
                existing_files = [f for f in os.listdir(user_folder) 
                                if f.startswith(filename) and f.endswith(('.mp4', '.webm'))]
                
                if existing_files:
                    print(f"{Fore.YELLOW}Video already exists: {existing_files[0]}")
                    return True
                
                # Try downloading with different methods
                print(f"{Fore.YELLOW}Trying yt-dlp method...")
                if self.download_video_yt_dlp(video_url, filename, user_folder):
                    return True
                
                print(f"{Fore.YELLOW}Trying API method...")
                if self.download_video_api(video_url, filename, user_folder):
                    return True
                
                print(f"{Fore.RED}All download methods failed")
                return False
            else:
                print(f"{Fore.RED}Could not extract username/video ID from URL")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}Single video download failed: {str(e)}")
            return False

    def close_browser(self):
        """Close any open browser instances"""
        self.selenium_handler.close_upload_driver()
