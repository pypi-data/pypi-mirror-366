"""
TikTok Video Reup
Main entry point for the application
Copyright t.me/xuancuong2006
"""
import warnings
import logging
from colorama import init, Fore

from core.downloader import TikTokDownloader
from upload.uploader import TikTokUploader
from selenium_handler.browser import SeleniumHandler
from config.settings import DEFAULT_DOWNLOAD_FOLDER

# Suppress warnings and set logging level
warnings.filterwarnings("ignore")
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)
logging.getLogger('WDM').setLevel(logging.ERROR)

# Initialize colorama for colored output
init(autoreset=True)


def main():
    """Main function"""
    print(f"{Fore.CYAN}TikTok Video Reup - Copyright t.me/xuancuong2006")
    print(f"{Fore.CYAN}{'='*60}")
    
    # Ask user what they want to do
    print(f"{Fore.YELLOW}What would you like to do?")
    print(f"{Fore.YELLOW}1. Download videos from TikTok user")
    print(f"{Fore.YELLOW}2. Download single TikTok video by URL")
    print(f"{Fore.YELLOW}3. Upload downloaded videos to TikTok")
    print(f"{Fore.YELLOW}4. Download and then upload videos")
    
    choice = input(f"{Fore.YELLOW}Enter your choice (1-4): ").strip()
    
    # Get download folder (optional)
    download_folder = input(f"{Fore.YELLOW}Download folder (press Enter for 'downloads'): ").strip()
    if not download_folder:
        download_folder = DEFAULT_DOWNLOAD_FOLDER
    
    try:
        # Create downloader instance
        downloader = TikTokDownloader(download_folder)
        
        # Create selenium handler and uploader instances
        selenium_handler = SeleniumHandler()
        uploader = TikTokUploader(selenium_handler)
        
        if choice == "1":
            # Download from user
            username = input(f"{Fore.YELLOW}Enter TikTok username (without @): ").strip()
            if not username:
                print(f"{Fore.RED}Username cannot be empty!")
                return
            
            # Get max videos (optional)
            max_videos_input = input(f"{Fore.YELLOW}Max videos to download (press Enter for all): ").strip()
            max_videos = None
            if max_videos_input.isdigit():
                max_videos = int(max_videos_input)
            
            downloader.download_user_videos(username, max_videos)
            
        elif choice == "2":
            # Download single video
            video_url = input(f"{Fore.YELLOW}Enter TikTok video URL: ").strip()
            if not video_url:
                print(f"{Fore.RED}Video URL cannot be empty!")
                return
            
            if "tiktok.com" not in video_url:
                print(f"{Fore.RED}Invalid TikTok URL!")
                return
            
            custom_filename = input(f"{Fore.YELLOW}Custom filename (optional, press Enter to skip): ").strip()
            if not custom_filename:
                custom_filename = None
            
            success = downloader.download_single_video(video_url, custom_filename)
            if success:
                print(f"{Fore.GREEN}✓ Video downloaded successfully!")
            else:
                print(f"{Fore.RED}✗ Failed to download video")
            
        elif choice == "3":
            # Upload only
            username = input(f"{Fore.YELLOW}Enter username folder to upload from: ").strip()
            if not username:
                print(f"{Fore.RED}Username cannot be empty!")
                return
            
            # Get upload limit (optional)
            upload_limit_input = input(f"{Fore.YELLOW}Max videos to upload (press Enter for all): ").strip()
            upload_limit = None
            if upload_limit_input.isdigit():
                upload_limit = int(upload_limit_input)
            
            # Create user folder path
            import os
            user_folder = os.path.join(download_folder, username)
            uploader.bulk_upload_videos(user_folder, upload_limit)
            
        elif choice == "4":
            # Download and upload
            username = input(f"{Fore.YELLOW}Enter TikTok username (without @): ").strip()
            if not username:
                print(f"{Fore.RED}Username cannot be empty!")
                return
            
            # Get max videos (optional)
            max_videos_input = input(f"{Fore.YELLOW}Max videos to download (press Enter for all): ").strip()
            max_videos = None
            if max_videos_input.isdigit():
                max_videos = int(max_videos_input)
            
            # Download first
            print(f"{Fore.MAGENTA}Step 1: Downloading videos...")
            downloader.download_user_videos(username, max_videos)
            
            # Ask if user wants to upload
            upload_choice = input(f"{Fore.YELLOW}Download complete. Upload videos now? (y/n): ").lower()
            if upload_choice in ['y', 'yes']:
                print(f"{Fore.MAGENTA}Step 2: Uploading videos...")
                import os
                user_folder = os.path.join(download_folder, username)
                uploader.bulk_upload_videos(user_folder, max_videos)
        
        else:
            print(f"{Fore.RED}Invalid choice!")
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}")
        import traceback
        print(f"{Fore.RED}Traceback: {traceback.format_exc()}")
    finally:
        # Clean up
        try:
            if 'downloader' in locals():
                downloader.close_browser()
            if 'uploader' in locals():
                uploader.close_browser()
        except:
            pass


if __name__ == "__main__":
    main()
