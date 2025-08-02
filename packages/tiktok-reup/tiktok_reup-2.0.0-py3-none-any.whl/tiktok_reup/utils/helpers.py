"""
Utility functions for TikTok downloader/uploader
"""
import os
import re
import time
from colorama import Fore
from ..config.settings import MAX_CAPTION_LENGTH


def sanitize_filename(filename):
    """
    Sanitize filename for Windows compatibility
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for Windows
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename


def filter_bmp_characters(text):
    """
    Filter and replace non-BMP characters that ChromeDriver can't handle
    
    Args:
        text (str): Input text that may contain non-BMP characters
        
    Returns:
        str: Filtered text with BMP character replacements
    """
    try:
        # Common non-BMP character replacements
        replacements = {
            # More emojis and symbols
            '😃': ':)',
            '😄': ':D',
            '😁': ':D',
            '😆': 'XD',
            '😅': ':)',
            '🤣': 'LOL',
            '☺️': ':)',
            '😊': ':)',
            '😇': ':)',
            '🙂': ':)',
            '😉': ';)',
            '😌': ':)',
            '😋': ':P',
            '😛': ':P',
            '😜': ';P',
            '😝': 'XP',
            '🤑': '$$$',
            '🤗': '*hug*',
            '🤔': '*thinking*',
            '🤐': '*silent*',
            '😶': '*silent*',
            '😏': '*smirk*',
            '😒': '*unimpressed*',
            '🙄': '*eyeroll*',
            '😬': '*grimace*',
            '😓': '*sweat*',
            '😔': '*sad*',
            '😪': '*sleepy*',
            '🤤': '*drool*',
            '😴': '*zzz*',
            '🤒': '*sick*',
            '🤕': '*hurt*',
            '🤢': '*sick*',
            '🤮': '*sick*',
            '🤧': '*sneeze*',
            '😎': 'B)',
            '🤓': '*nerd*',
            '🧐': '*monocle*',
            '😭': '*cry*',
            '😱': '*scream*',
            '😤': '*angry*',
            '😡': '*angry*',
            '🤬': '*angry*',
            '😈': '*devil*',
            '👿': '*devil*',
            '👻': '*ghost*',
            '💀': '*skull*',
            '☠️': '*skull*',
            '👽': '*alien*',
            '🤖': '*robot*',
            
            # Animals
            '🐶': '*dog*',
            '🐱': '*cat*',
            '🐭': '*mouse*',
            '🐹': '*hamster*',
            '🐰': '*rabbit*',
            '🦊': '*fox*',
            '🐻': '*bear*',
            '🐼': '*panda*',
            '🐨': '*koala*',
            '🐯': '*tiger*',
            '🦁': '*lion*',
            '🐮': '*cow*',
            '🐷': '*pig*',
            '🐸': '*frog*',
            '🐵': '*monkey*',
            '🐔': '*chicken*',
            '🐧': '*penguin*',
            '🐦': '*bird*',
            '🐤': '*chick*',
            '🦅': '*eagle*',
            '🦆': '*duck*',
            '🦉': '*owl*',
            '🦇': '*bat*',
            '🐺': '*wolf*',
            '🐗': '*boar*',
            '🐴': '*horse*',
            '🦄': '*unicorn*',
            '🐝': '*bee*',
            '🐞': '*ladybug*',
            '🦋': '*butterfly*',
            '🐢': '*turtle*',
            '🐍': '*snake*',
            '🦎': '*lizard*',
            '🐙': '*octopus*',
            '🦑': '*squid*',
            '🦐': '*shrimp*',
            '🦞': '*lobster*',
            '🦀': '*crab*',
            '🐠': '*fish*',
            '🐟': '*fish*',
            '🐡': '*fish*',
            '🐬': '*dolphin*',
            '🐳': '*whale*',
            '🐋': '*whale*',
            '🦈': '*shark*',
            
            # Food
            '🍎': '*apple*',
            '🍐': '*pear*',
            '🍊': '*orange*',
            '🍋': '*lemon*',
            '🍌': '*banana*',
            '🍉': '*watermelon*',
            '🍇': '*grapes*',
            '🍓': '*strawberry*',
            '🍈': '*melon*',
            '🍒': '*cherries*',
            '🍑': '*peach*',
            '🥭': '*mango*',
            '🍍': '*pineapple*',
            '🥥': '*coconut*',
            '🥝': '*kiwi*',
            '🍅': '*tomato*',
            '🥑': '*avocado*',
            '🍆': '*eggplant*',
            '🥦': '*broccoli*',
            '🥕': '*carrot*',
            '🌽': '*corn*',
            '🌶️': '*pepper*',
            '🥔': '*potato*',
            '🍞': '*bread*',
            '🥐': '*croissant*',
            '🥯': '*bagel*',
            '🥖': '*baguette*',
            '🥨': '*pretzel*',
            '🧀': '*cheese*',
            '🥚': '*egg*',
            '🍳': '*cooking*',
            '🥓': '*bacon*',
            '🥩': '*meat*',
            '🍗': '*chicken*',
            '🍖': '*meat*',
            '🌭': '*hotdog*',
            '🍔': '*burger*',
            '🍟': '*fries*',
            '🍕': '*pizza*',
            '🥪': '*sandwich*',
            '🥙': '*wrap*',
            '🌮': '*taco*',
            '🌯': '*burrito*',
            '🥗': '*salad*',
            '🥘': '*paella*',
            '🍝': '*pasta*',
            '🍜': '*noodles*',
            '🍲': '*stew*',
            '🍛': '*curry*',
            '🍣': '*sushi*',
            '🍤': '*shrimp*',
            '🍙': '*rice ball*',
            '🍚': '*rice*',
            '🍘': '*rice cracker*',
            '🍥': '*fish cake*',
            '🥮': '*mooncake*',
            '🍦': '*ice cream*',
            '🍧': '*shaved ice*',
            '🍨': '*ice cream*',
            '🍩': '*donut*',
            '🍪': '*cookie*',
            '🎂': '*cake*',
            '🍰': '*cake*',
            '🧁': '*cupcake*',
            '🥧': '*pie*',
            '🍫': '*chocolate*',
            '🍬': '*candy*',
            '🍭': '*lollipop*',
            '🍮': '*custard*',
            '🍯': '*honey*',
            '🍼': '*milk*',
            '🥛': '*milk*',
            '☕': '*coffee*',
            '🍵': '*tea*',
            '🍶': '*sake*',
            '🍾': '*champagne*',
            '🍷': '*wine*',
            '🍸': '*cocktail*',
            '🍹': '*tropical drink*',
            '🍺': '*beer*',
            '🍻': '*beers*',
            # Math and currency symbols
            '₹': 'Rs',
            '€': 'EUR',
            '£': 'GBP',
            '¥': 'YEN',
            '₽': 'RUB',
            '₩': 'KRW',
            '₡': 'CRC',
            '₦': 'NGN',
            '₨': 'Rs',
            '₪': 'ILS',
            '₫': 'VND',
            '₭': 'LAK',
            '₮': 'MNT',
            '₯': 'GRD',
            '₰': 'PF',
            '₱': 'PHP',
            '₲': 'PYG',
            '₳': 'ARA',
            '₴': 'UAH',
            '₵': 'GHS',
            '₶': 'LVL',
            '₷': 'SPL',
            '₸': 'KZT',
            '₹': 'INR',
            '₺': 'TRY',
            
            # Special quotes and dashes
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',
            '—': '-',
            '…': '...',
            
            # Mathematical symbols
            '∞': 'infinity',
            '±': '+/-',
            '≤': '<=',
            '≥': '>=',
            '≠': '!=',
            '÷': '/',
            '×': 'x',
            '√': 'sqrt',
            '∑': 'sum',
            '∆': 'delta',
            '∏': 'product',
            '∫': 'integral',
            '∂': 'partial',
            '∇': 'nabla',
            
            # Arrows
            '→': '->',
            '←': '<-',
            '↑': '^',
            '↓': 'v',
            '↔': '<->',
            '⇒': '=>',
            '⇐': '<=',
            '⇔': '<=>',
            
            # Other common symbols
            '©': '(c)',
            '®': '(R)',
            '™': '(TM)',
            '°': 'deg',
            'µ': 'micro',
            '§': 'section',
            '¶': 'paragraph',
            '†': '+',
            '‡': '++',
            '•': '*',
            '◦': 'o',
            '‰': 'per mille',
            '‱': 'per ten thousand',
        }
        
        # First, apply direct replacements
        filtered_text = text
        for old_char, new_char in replacements.items():
            filtered_text = filtered_text.replace(old_char, new_char)
        
        # Then filter remaining non-BMP characters
        filtered_chars = []
        for char in filtered_text:
            # Check if character is in BMP range
            if ord(char) <= 0xFFFF:
                filtered_chars.append(char)
            else:
                # For any remaining non-BMP characters, try to find a similar replacement
                char_code = ord(char)
                
                # Handle emoji ranges by replacing with descriptive text
                if 0x1F600 <= char_code <= 0x1F64F:  # Emoticons
                    filtered_chars.append(':)')
                elif 0x1F300 <= char_code <= 0x1F5FF:  # Misc Symbols and Pictographs
                    filtered_chars.append('*symbol*')
                elif 0x1F680 <= char_code <= 0x1F6FF:  # Transport and Map
                    filtered_chars.append('*transport*')
                elif 0x1F700 <= char_code <= 0x1F77F:  # Alchemical Symbols
                    filtered_chars.append('*symbol*')
                elif 0x1F780 <= char_code <= 0x1F7FF:  # Geometric Shapes Extended
                    filtered_chars.append('*shape*')
                elif 0x1F800 <= char_code <= 0x1F8FF:  # Supplemental Arrows-C
                    filtered_chars.append('->')
                elif 0x1F900 <= char_code <= 0x1F9FF:  # Supplemental Symbols and Pictographs
                    filtered_chars.append('*symbol*')
                elif 0x20000 <= char_code <= 0x2A6DF:  # CJK Extension B
                    filtered_chars.append('[CJK]')
                elif 0x2A700 <= char_code <= 0x2B73F:  # CJK Extension C
                    filtered_chars.append('[CJK]')
                elif 0x2B740 <= char_code <= 0x2B81F:  # CJK Extension D
                    filtered_chars.append('[CJK]')
                elif 0x2B820 <= char_code <= 0x2CEAF:  # CJK Extension E
                    filtered_chars.append('[CJK]')
                else:
                    # For any other non-BMP character, replace with space
                    filtered_chars.append(' ')
        
        filtered_text = ''.join(filtered_chars)
        
        # Clean up extra spaces and normalize whitespace
        filtered_text = ' '.join(filtered_text.split())
        
        return filtered_text
        
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Error filtering text: {str(e)}")
        # Fallback: try to encode/decode to remove problematic characters
        try:
            return text.encode('utf-16', 'ignore').decode('utf-16')
        except:
            return "Repost"  # Ultimate fallback


def save_video_caption(video_info, filename, user_folder):
    """
    Save video caption/description to a text file
    
    Args:
        video_info (dict): Video information from yt-dlp
        filename (str): Base filename (without extension)
        user_folder (str): User-specific folder path
    """
    try:
        caption_file = os.path.join(user_folder, f"{filename}_caption.txt")
        
        # Extract relevant information
        title = video_info.get('title', 'No title')
        description = video_info.get('description', 'No description')
        uploader = video_info.get('uploader', 'Unknown')
        upload_date = video_info.get('upload_date', 'Unknown')
        view_count = video_info.get('view_count', 0)
        like_count = video_info.get('like_count', 0)
        comment_count = video_info.get('comment_count', 0)
        duration = video_info.get('duration', 0)
        video_url = video_info.get('webpage_url', 'Unknown')
        
        # Format the caption content
        caption_content = f"""TikTok Video Information
========================

Title: {title}
Author: @{uploader}
Upload Date: {upload_date}
Duration: {duration} seconds
Views: {view_count:,}
Likes: {like_count:,}
Comments: {comment_count:,}
URL: {video_url}

Description/Caption:
{description}

========================
Downloaded on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # Save to file
        with open(caption_file, 'w', encoding='utf-8') as f:
            f.write(caption_content)
            
        print(f"{Fore.GREEN}✓ Saved caption: {filename}_caption.txt")
        
    except Exception as e:
        print(f"{Fore.YELLOW}⚠ Could not save caption: {str(e)}")


def create_folder_if_not_exists(folder_path):
    """Create folder if it doesn't exist"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"{Fore.GREEN}Created folder: {folder_path}")
    return folder_path


def extract_video_info_from_url(video_url):
    """
    Extract username and video ID from TikTok URL
    
    Args:
        video_url (str): TikTok video URL
        
    Returns:
        tuple: (username, video_id) or (None, None) if not found
    """
    username_match = re.search(r'/@([^/]+)/', video_url)
    video_id_match = re.search(r'/video/(\d+)', video_url)
    
    username = username_match.group(1) if username_match else None
    video_id = video_id_match.group(1) if video_id_match else None
    
    return username, video_id


def parse_caption_from_file(caption_path):
    """
    Parse caption text from caption file
    
    Args:
        caption_path (str): Path to caption file
        
    Returns:
        str: Cleaned caption text
    """
    caption_text = ""
    
    if os.path.exists(caption_path):
        try:
            with open(caption_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract title first, if no title then use description
                if "Title:" in content:
                    title_line = content.split("Title:")[1].split("\n")[0].strip()
                    if title_line and title_line != "No title":
                        caption_text = title_line
                
                # If no valid title, use description/caption
                if not caption_text and "Description/Caption:" in content:
                    caption_text = content.split("Description/Caption:")[1].split("========================")[0].strip()
                
                # If still no caption, use title even if "No title"
                if not caption_text and "Title:" in content:
                    caption_text = content.split("Title:")[1].split("\n")[0].strip()
                
                # Final fallback
                if not caption_text:
                    caption_text = "Repost"
        except:
            caption_text = "Repost"
    else:
        caption_text = "Repost"
    
    # Clean up caption text
    caption_text = caption_text.replace("No title", "").replace("No description", "").strip()
    if not caption_text:
        caption_text = "Repost"
    
    # Filter out non-BMP characters that ChromeDriver can't handle
    caption_text = filter_bmp_characters(caption_text)
    
    # Limit caption length (TikTok has character limits)
    if len(caption_text) > MAX_CAPTION_LENGTH:
        caption_text = caption_text[:MAX_CAPTION_LENGTH] + "..."
    
    return caption_text


def wait_with_countdown(seconds, message="Waiting"):
    """
    Wait with countdown display
    
    Args:
        seconds (int): Number of seconds to wait
        message (str): Message to display during countdown
    """
    for remaining in range(seconds, 0, -1):
        print(f"{Fore.YELLOW}{message}: {remaining} seconds...  ", end="\r")
        time.sleep(1)
    print(f"{Fore.GREEN}Continuing...                ")
