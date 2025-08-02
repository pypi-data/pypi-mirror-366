"""
TikTok API handling functions
"""
import requests
from colorama import Fore
from ..config.settings import API_ENDPOINTS, DOWNLOAD_API_ENDPOINTS, REQUEST_HEADERS


class TikTokAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)

    def get_user_videos_api(self, username):
        """
        Get user videos using TikTok API (faster and more reliable)
        
        Args:
            username (str): TikTok username (without @)
            
        Returns:
            list: List of video URLs
        """
        try:
            print(f"{Fore.YELLOW}Trying API approach for @{username}...")
            
            # Try different API endpoints to get user videos
            api_endpoints = [endpoint.format(username=username) for endpoint in API_ENDPOINTS]
            
            for endpoint in api_endpoints:
                try:
                    response = self.session.get(
                        endpoint,
                        timeout=30,
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                            'Accept': 'application/json, text/plain, */*',
                            'Accept-Language': 'en-US,en;q=0.9',
                            'Referer': 'https://tikwm.com/',
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        video_urls = []
                        
                        # Handle different API response formats
                        if 'data' in data and 'aweme_list' in data['data']:
                            for video in data['data']['aweme_list']:
                                if 'video' in video and 'play_addr' in video['video']:
                                    video_id = video.get('aweme_id', '')
                                    if video_id:
                                        video_urls.append(f"https://www.tiktok.com/@{username}/video/{video_id}")
                        
                        elif 'data' in data and 'videos' in data['data']:
                            for video in data['data']['videos']:
                                video_id = video.get('video_id', video.get('id', ''))
                                if video_id:
                                    video_urls.append(f"https://www.tiktok.com/@{username}/video/{video_id}")
                        
                        if video_urls:
                            print(f"{Fore.GREEN}Found {len(video_urls)} videos via API")
                            return video_urls
                            
                except Exception as e:
                    print(f"{Fore.YELLOW}API endpoint {endpoint} failed: {str(e)}")
                    continue
            
            return []
            
        except Exception as e:
            print(f"{Fore.YELLOW}API approach failed: {str(e)}")
            return []

    def download_video_api(self, video_url, filename, user_folder, download_from_url_func):
        """
        Download video using TikTok API scraping (fallback method)
        
        Args:
            video_url (str): TikTok video URL
            filename (str): Output filename
            user_folder (str): User-specific folder path
            download_from_url_func: Function to download from direct URL
            
        Returns:
            bool: Success status
        """
        try:
            # Updated API endpoints that are more likely to work
            api_endpoints = []
            for endpoint_config in DOWNLOAD_API_ENDPOINTS:
                endpoint = {
                    'url': endpoint_config['url'],
                    'params': {}
                }
                for key, value in endpoint_config['params'].items():
                    endpoint['params'][key] = value.format(video_url=video_url)
                api_endpoints.append(endpoint)
            
            for endpoint in api_endpoints:
                try:
                    print(f"{Fore.YELLOW}Trying API: {endpoint['url']}")
                    
                    # Try both GET and POST methods
                    for method in ['GET', 'POST']:
                        try:
                            if method == 'GET':
                                response = self.session.get(
                                    endpoint['url'], 
                                    params=endpoint['params'], 
                                    timeout=30,
                                    headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                        'Accept': 'application/json, text/plain, */*',
                                        'Accept-Language': 'en-US,en;q=0.9',
                                        'Referer': 'https://tikwm.com/',
                                    }
                                )
                            else:
                                response = self.session.post(
                                    endpoint['url'], 
                                    data=endpoint['params'], 
                                    timeout=30,
                                    headers={
                                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                        'Accept': 'application/json, text/plain, */*',
                                        'Accept-Language': 'en-US,en;q=0.9',
                                        'Referer': 'https://tikwm.com/',
                                        'Content-Type': 'application/x-www-form-urlencoded'
                                    }
                                )
                            
                            if response.status_code == 200:
                                try:
                                    data = response.json()
                                except:
                                    continue
                                
                                # Handle different API response formats
                                download_url = None
                                
                                # tikwm.com format
                                if 'data' in data:
                                    if 'hdplay' in data['data']:
                                        download_url = data['data']['hdplay']
                                    elif 'play' in data['data']:
                                        download_url = data['data']['play']
                                    elif 'wmplay' in data['data']:
                                        download_url = data['data']['wmplay']
                                
                                # Other formats
                                if not download_url:
                                    for key in ['video', 'url', 'download_url', 'video_url']:
                                        if key in data and data[key]:
                                            download_url = data[key]
                                            break
                                
                                # Check nested structures
                                if not download_url and 'result' in data:
                                    result = data['result']
                                    for key in ['video', 'url', 'download_url', 'video_url']:
                                        if key in result and result[key]:
                                            download_url = result[key]
                                            break
                                
                                if download_url:
                                    print(f"{Fore.GREEN}Found download URL via {method} {endpoint['url']}")
                                    return download_from_url_func(download_url, filename, user_folder)
                        
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    print(f"{Fore.YELLOW}API {endpoint['url']} failed: {str(e)}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"{Fore.RED}API download failed: {str(e)}")
            return False

    def download_from_url(self, download_url, filename, user_folder):
        """
        Download video from direct URL with progress bar
        
        Args:
            download_url (str): Direct video URL
            filename (str): Output filename
            user_folder (str): User-specific folder path
            
        Returns:
            bool: Success status
        """
        try:
            from tqdm import tqdm
            import os
            
            response = self.session.get(download_url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Get file extension from URL or default to mp4
            file_ext = '.mp4'
            content_type = response.headers.get('content-type', '')
            if 'video/mp4' in content_type:
                file_ext = '.mp4'
            elif 'video/webm' in content_type:
                file_ext = '.webm'
            
            filepath = os.path.join(user_folder, f"{filename}{file_ext}")
            
            # Get file size for progress bar
            total_size = int(response.headers.get('content-length', 0))
            
            with open(filepath, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            
            print(f"{Fore.GREEN}✓ Downloaded: {filename}{file_ext}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}Download failed: {str(e)}")
            return False
