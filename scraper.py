"""
Web scraper module for IT KMITL staff website
Extracts professor information and Scopus IDs
"""

import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from config import IT_KMITL_STAFF_URL, STAFF_PROFILE_PATTERN


class ITKMITLScraper:
    """Scraper for IT KMITL academic staff website"""
    
    def __init__(self):
        self.base_url = "https://www.it.kmitl.ac.th"
        self.staff_url = IT_KMITL_STAFF_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.session.verify = False  # Disable SSL verification
        # Suppress SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def get_staff_list(self) -> List[Dict]:
        """
        Scrape the main staff page to get list of all academic staff
        
        Returns:
            List of dictionaries containing staff info
        """
        try:
            response = self.session.get(self.staff_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            staff_list = []
            
            # Find all staff profile links
            # Pattern: /th/staffs/s/... 
            links = soup.find_all('a', href=re.compile(STAFF_PROFILE_PATTERN))
            
            for link in links:
                staff_url = link.get('href')
                if not staff_url.startswith('http'):
                    staff_url = self.base_url + staff_url
                
                # Extract name from URL slug (more reliable than link text)
                # Example: /th/staffs/s/arit-thammano -> arit-thammano
                url_parts = staff_url.rstrip('/').split('/')
                name_slug = url_parts[-1] if url_parts else ''
                
                # Convert slug to display name (capitalize each word)
                name = name_slug.replace('-', ' ').title() if name_slug else link.get_text(strip=True)
                
                # Find associated image
                image_url = None
                img_tag = link.find('img')
                if not img_tag and link.find_parent():
                    img_tag = link.find_parent().find('img')
                
                if img_tag:
                    image_url = img_tag.get('src')
                    if image_url and not image_url.startswith('http'):
                        image_url = self.base_url + image_url
                
                staff_info = {
                    'name': name,
                    'profile_url': staff_url,
                    'image_url': image_url
                }
                
                # Avoid duplicates
                if staff_info not in staff_list:
                    staff_list.append(staff_info)
            
            return staff_list
            
        except Exception as e:
            print(f"Error scraping staff list: {e}")
            return []
    
    def extract_profile_data(self, profile_url: str) -> Dict:
        """
        Extract detailed profile data from a professor's profile page
        
        Args:
            profile_url: URL to the professor's profile page
            
        Returns:
            Dictionary with profile data including scopus_id, scopus_url, image_url, thai_name
        """
        profile_data = {
            'scopus_id': None,
            'scopus_url': None,
            'image_url': None,
            'thai_name': None
        }
        
        try:
            response = self.session.get(profile_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract Scopus link and ID
            scopus_links = soup.find_all('a', href=re.compile(r'scopus\.com'))
            for link in scopus_links:
                href = link.get('href')
                # Extract authorId from URL pattern like: authorId=6603566678
                match = re.search(r'authorId=(\d+)', href)
                if match:
                    profile_data['scopus_id'] = match.group(1)
                    profile_data['scopus_url'] = href
                    break
            
            # Extract profile image
            # Look for img tag in the profile section
            img_tags = soup.find_all('img')
            for img in img_tags:
                src = img.get('src', '')
                # Filter for profile images (usually contain specific patterns)
                if '/uploads/' in src or 'staff' in src.lower() or 'profile' in src.lower():
                    if not src.startswith('http'):
                        profile_data['image_url'] = self.base_url + src
                    else:
                        profile_data['image_url'] = src
                    break
            
            # If no specific image found, try the first large image
            if not profile_data['image_url']:
                for img in img_tags:
                    src = img.get('src', '')
                    width = img.get('width', 0)
                    height = img.get('height', 0)
                    try:
                        if (int(width) > 100 or int(height) > 100):
                            if not src.startswith('http'):
                                profile_data['image_url'] = self.base_url + src
                            else:
                                profile_data['image_url'] = src
                            break
                    except:
                        pass
            
            # Extract Thai name
            # Strategy 1: Look for Thai name in "ประวัติส่วนตัว" section
            profile_section = soup.find(string=re.compile(r'ประวัติส่วนตัว'))
            if profile_section:
                # Look for text with Thai prefix (ศ., รศ., ผศ., ดร., อาจารย์)
                parent = profile_section.find_parent()
                if parent:
                    # Search in nearby elements
                    for tag in parent.find_all_next(['p', 'div', 'span', 'h3', 'h4'], limit=5):
                        text = tag.get_text(strip=True)
                        # Match Thai academic titles
                        if re.search(r'(ศ\.|รศ\.|ผศ\.|ดร\.|อาจารย์|ผศ\s|รศ\s|ศ\s)', text):
                            # Clean up the text
                            text = re.sub(r'\s+', ' ', text).strip()
                            if any('\u0e00' <= char <= '\u0e7f' for char in text):
                                profile_data['thai_name'] = text
                                break
            
            # Strategy 2: Extract from image URL if Strategy 1 fails
            if not profile_data['thai_name'] and profile_data.get('image_url'):
                try:
                    from urllib.parse import unquote
                    img_url = profile_data['image_url']
                    # Extract name part from URL like: /อาริต-ธรรมโน-500x500.jpg
                    match = re.search(r'/([^/]+)-500x500\.jpg', img_url)
                    if match:
                        encoded_name = match.group(1)
                        decoded_name = unquote(encoded_name)
                        # Replace hyphens with spaces
                        thai_name = decoded_name.replace('-', ' ')
                        if any('\u0e00' <= char <= '\u0e7f' for char in thai_name):
                            profile_data['thai_name'] = thai_name
                except Exception as e:
                    pass
            
            # Strategy 3: Fall back to old method (h2/h3 tags) but skip common headers
            if not profile_data['thai_name']:
                name_tags = soup.find_all(['h2', 'h3', 'h4', 'p'])
                skip_patterns = [
                    'บุคลากรสายวิชาการ', 
                    'เกี่ยวกับคณะ', 
                    'รายวิชาที่สอน',
                    'ประวัติส่วนตัว',
                    'ช่องทางการติดต่อ',
                    'ผลงานเพิ่มเติม',
                    'ปริญญาตรี',
                    'ปริญญาโท',
                    'ปริญญาเอก'
                ]
                for tag in name_tags:
                    text = tag.get_text(strip=True)
                    # Skip if it's a common header
                    if any(skip in text for skip in skip_patterns):
                        continue
                    # Thai characters detection with minimum length
                    if any('\u0e00' <= char <= '\u0e7f' for char in text) and len(text) > 5:
                        profile_data['thai_name'] = text
                        break
            
            return profile_data
            
        except Exception as e:
            print(f"Error extracting profile data from {profile_url}: {e}")
            return profile_data
    
    def extract_scopus_id(self, profile_url: str) -> Optional[str]:
        """
        Extract Scopus Author ID from a professor's profile page
        (Backward compatibility wrapper)
        
        Args:
            profile_url: URL to the professor's profile page
            
        Returns:
            Scopus Author ID or None if not found
        """
        profile_data = self.extract_profile_data(profile_url)
        return profile_data.get('scopus_id')
    
    def scrape_all_professors(self, delay: float = 1.0) -> List[Dict]:
        """
        Scrape all professors data including Scopus IDs, images, and links
        
        Args:
            delay: Delay between requests (in seconds) to be polite
            
        Returns:
            List of professor data dictionaries
        """
        print("Fetching staff list...")
        staff_list = self.get_staff_list()
        print(f"Found {len(staff_list)} staff members")
        
        professors_data = []
        
        for i, staff in enumerate(staff_list, 1):
            print(f"Processing {i}/{len(staff_list)}: {staff['name']}")
            
            # Extract detailed profile data
            profile_data = self.extract_profile_data(staff['profile_url'])
            
            professor_data = {
                'name': staff['name'],
                'thai_name': profile_data.get('thai_name') or staff['name'],
                'profile_url': staff['profile_url'],
                'image_url': profile_data.get('image_url') or staff['image_url'],
                'scopus_id': profile_data.get('scopus_id'),
                'scopus_url': profile_data.get('scopus_url')
            }
            
            professors_data.append(professor_data)
            
            # Be polite with delays
            if i < len(staff_list):
                time.sleep(delay)
        
        return professors_data


# Test function
if __name__ == "__main__":
    scraper = ITKMITLScraper()
    professors = scraper.scrape_all_professors()
    
    print(f"\n✓ Scraped {len(professors)} professors")
    print(f"✓ {sum(1 for p in professors if p['scopus_id'])} have Scopus IDs")
    
    # Show sample
    if professors:
        print("\nSample data:")
        print(professors[0])
