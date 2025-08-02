"""
Upload functionality for TikTok videos
"""
import os
import time
from colorama import Fore
from ..config.settings import DEFAULT_UPLOAD_DELAY
from ..utils.helpers import parse_caption_from_file, wait_with_countdown


class TikTokUploader:
    def __init__(self, selenium_handler):
        self.selenium_handler = selenium_handler

    def upload_video(self, video_path, caption_path, custom_caption=None):
        """
        Upload a video to TikTok with its caption (fully automated)
        
        Args:
            video_path (str): Path to video file
            caption_path (str): Path to caption file
            custom_caption (str): Optional custom caption override
            
        Returns:
            bool: Upload success status
        """
        try:
            # Parse caption text
            if custom_caption:
                caption_text = custom_caption
            else:
                caption_text = parse_caption_from_file(caption_path)
            
            # Use selenium handler to upload
            return self.selenium_handler.upload_video(video_path, caption_text)
            
        except Exception as e:
            print(f"{Fore.RED}Upload failed: {str(e)}")
            return False

    def bulk_upload_videos(self, user_folder, upload_limit=None):
        """
        Upload all downloaded videos from a user folder (fully automated)
        
        Args:
            user_folder (str): Path to user folder containing videos
            upload_limit (int): Maximum number of videos to upload (None for all)
        """
        try:
            if not os.path.exists(user_folder):
                print(f"{Fore.RED}User folder not found: {user_folder}")
                return
            
            # Get all video files
            video_files = [f for f in os.listdir(user_folder) if f.endswith(('.mp4', '.webm', '.mov'))]
            video_files.sort()  # Sort for consistent order
            
            if not video_files:
                print(f"{Fore.RED}No video files found in {user_folder}")
                return
            
            # Limit videos if specified
            if upload_limit and upload_limit < len(video_files):
                video_files = video_files[:upload_limit]
                print(f"{Fore.YELLOW}Limited to {upload_limit} videos")
            
            print(f"{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.MAGENTA}TikTok Automated Bulk Upload")
            print(f"{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.CYAN}Found {len(video_files)} videos to upload")
            print(f"{Fore.CYAN}User folder: {user_folder}")
            print(f"{Fore.YELLOW}Upload will be fully automated!")
            
            # Ensure logged in
            if not self.selenium_handler.is_logged_in:
                print(f"{Fore.YELLOW}Please login to TikTok first...")
                if not self.selenium_handler.login_to_tiktok():
                    print(f"{Fore.RED}Failed to login. Cannot proceed with upload.")
                    return
            
            success_count = 0
            failed_count = 0
            
            for i, video_file in enumerate(video_files, 1):
                print(f"\n{Fore.BLUE}[{i}/{len(video_files)}] Processing: {video_file}")
                
                video_path = os.path.join(user_folder, video_file)
                
                # Find corresponding caption file
                base_name = os.path.splitext(video_file)[0]
                caption_file = f"{base_name}_caption.txt"
                caption_path = os.path.join(user_folder, caption_file)
                
                # Upload video automatically
                try:
                    if self.upload_video(video_path, caption_path):
                        success_count += 1
                        print(f"{Fore.GREEN}✓ Upload completed successfully")
                    else:
                        failed_count += 1
                        print(f"{Fore.RED}✗ Upload failed")
                except Exception as e:
                    failed_count += 1
                    print(f"{Fore.RED}✗ Upload failed: {str(e)}")
                
                # Add delay between uploads with countdown
                if i < len(video_files):
                    wait_with_countdown(DEFAULT_UPLOAD_DELAY, "Waiting before next upload")
            
            # Summary
            print(f"\n{Fore.MAGENTA}{'='*50}")
            print(f"{Fore.GREEN}Automated Upload Summary:")
            print(f"{Fore.GREEN}Successful: {success_count}")
            print(f"{Fore.RED}Failed: {failed_count}")
            print(f"{Fore.CYAN}Total processed: {success_count + failed_count}")
            print(f"{Fore.MAGENTA}{'='*50}")
            
        except Exception as e:
            print(f"{Fore.RED}Bulk upload failed: {str(e)}")

    def login_to_tiktok(self):
        """Login to TikTok using selenium handler"""
        return self.selenium_handler.login_to_tiktok()

    def close_browser(self):
        """Close the upload browser"""
        self.selenium_handler.close_upload_driver()
