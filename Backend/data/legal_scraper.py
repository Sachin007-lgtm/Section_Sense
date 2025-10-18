"""
Unified Legal Section Scraper for India Code Website

This scraper supports two modes:
1. BeautifulSoup (for static pages) - Fast but limited
2. Selenium (for JavaScript pages) - Slower but works with dynamic content

NOTE: India Code website (indiacode.nic.in) uses JavaScript to load content,
so Selenium mode is recommended for actual scraping.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class UnifiedLegalScraper:
    """
    Unified scraper for Indian legal code sections
    Supports both BeautifulSoup and Selenium modes
    """
    
    def __init__(self, mode: str = 'beautifulsoup'):
        """
        Initialize scraper
        
        Args:
            mode: 'beautifulsoup' for static pages or 'selenium' for JavaScript pages
        """
        self.mode = mode.lower()
        self.base_url = "https://www.indiacode.nic.in"
        
        # Act IDs for different legal codes (updated as of 2024)
        self.act_ids = {
            'BNS': 'AC_CEN_5_23_00048_2023-45_1719292564123',      # Bharatiya Nyaya Sanhita
            'BNSS': 'AC_CEN_5_23_00049_202346_1719552320687',      # Bharatiya Nagarik Suraksha Sanhita
            'EVIDENCE': 'AC_CEN_5_23_00049_2023-47_1719292804654'  # Bharatiya Sakshya Adhiniyam
        }
        
        # Starting section IDs for each act (for URL generation)
        self.start_section_ids = {
            'BNS': 90366,
            'BNSS': 90988,
            'EVIDENCE': 90767
        }
        
        if self.mode == 'beautifulsoup':
            self._init_beautifulsoup()
        elif self.mode == 'selenium':
            self._init_selenium()
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'beautifulsoup' or 'selenium'")
    
    def _init_beautifulsoup(self):
        """Initialize BeautifulSoup mode"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        print("✓ BeautifulSoup mode initialized")
    
    def _init_selenium(self):
        """Initialize Selenium mode"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            self.selenium_available = True
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self.chrome_options = chrome_options
            self.driver = None
            print("✓ Selenium mode initialized")
            
        except ImportError:
            print("✗ Selenium not installed. Install with: pip install selenium")
            self.selenium_available = False
    
    def generate_section_url(self, act_type: str, section_number: int) -> str:
        """
        Generate India Code URL for a specific section
        
        Args:
            act_type: Act type (BNS, BNSS, EVIDENCE)
            section_number: Section number
        
        Returns:
            Complete URL with all required parameters
        """
        if act_type not in self.act_ids:
            raise ValueError(f"Invalid act type: {act_type}. Use: {list(self.act_ids.keys())}")
        
        actid = self.act_ids[act_type]
        section_id = self.start_section_ids[act_type] + (section_number - 1)
        
        url = (
            f"{self.base_url}/show-data?"
            f"abv=CEN&"
            f"statehandle=123456789/1362&"
            f"actid={actid}&"
            f"sectionId={section_id}&"
            f"sectionno={section_number}&"
            f"orderno={section_number}&"
            f"orgactid={actid}"
        )
        
        return url
    
    def test_connection(self) -> bool:
        """Test if the India Code website is accessible"""
        try:
            if self.mode == 'beautifulsoup':
                response = self.session.get(self.base_url, timeout=10)
                return response.status_code == 200
            else:
                # Selenium connection test would require starting browser
                return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def export_from_database(self, db_path: str = "../criminal_law_kb.db", 
                           output_file: str = "exported_sections.json") -> Optional[List[Dict]]:
        """
        Export data from existing database to JSON
        This is more reliable than scraping
        
        Args:
            db_path: Path to SQLite database
            output_file: Output JSON file name
        
        Returns:
            List of section dictionaries or None on error
        """
        import sqlite3
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT section_code, section_number, title, description, 
                       category, punishment, source
                FROM law_sections
                ORDER BY section_number
            """)
            
            sections = []
            for row in cursor.fetchall():
                sections.append({
                    'section_code': row[0],
                    'section_number': row[1],
                    'title': row[2],
                    'description': row[3],
                    'category': row[4],
                    'punishment': row[5],
                    'source': row[6]
                })
            
            output_path = Path(__file__).parent / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sections, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Exported {len(sections)} sections to {output_path}")
            conn.close()
            return sections
            
        except Exception as e:
            print(f"Export failed: {e}")
            return None
    
    def scrape_with_selenium(self, act_type: str, wait_time: int = 30) -> List[Dict[str, Any]]:
        """
        Scrape section links using Selenium (for JavaScript pages)
        
        Args:
            act_type: Act type (BNS, BNSS, EVIDENCE)
            wait_time: Time to wait for page load (seconds)
        
        Returns:
            List of section link dictionaries
        """
        if not self.selenium_available:
            print("✗ Selenium mode not available")
            return []
        
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        if act_type not in self.act_ids:
            raise ValueError(f"Invalid act type: {act_type}")
        
        # Start browser
        if not self.driver:
            print("Starting Chrome browser...")
            self.driver = webdriver.Chrome(options=self.chrome_options)
            print("✓ Browser started")
        
        act_id = self.act_ids[act_type]
        url = f"{self.base_url}/show-data?actid={act_id}"
        
        print(f"\nScraping {act_type} from: {url}")
        
        try:
            self.driver.get(url)
            print(f"Waiting up to {wait_time} seconds for content to load...")
            time.sleep(5)
            
            # Try multiple selectors
            selectors = [
                'a.title[target="_blank"]',
                'a[target="_blank"]',
                '#secaccordion a[target="_blank"]'
            ]
            
            section_elements = []
            for selector in selectors:
                try:
                    wait = WebDriverWait(self.driver, wait_time)
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    section_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if section_elements:
                        print(f"✓ Found {len(section_elements)} elements")
                        break
                except:
                    continue
            
            if not section_elements:
                print("✗ No section links found")
                return []
            
            section_links = []
            for element in section_elements:
                try:
                    href = element.get_attribute('href')
                    if not href or 'sectionno=' not in href:
                        continue
                    
                    text = element.text.strip()
                    section_match = re.search(r'sectionno=(\d+)', href)
                    id_match = re.search(r'sectionId=(\d+)', href)
                    
                    if section_match and id_match:
                        section_links.append({
                            'act_type': act_type,
                            'section_number': section_match.group(1),
                            'section_id': id_match.group(1),
                            'title': text,
                            'href': href
                        })
                except:
                    continue
            
            print(f"✓ Extracted {len(section_links)} section links")
            return section_links
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return []
    
    def close(self):
        """Close browser if using Selenium"""
        if self.mode == 'selenium' and hasattr(self, 'driver') and self.driver:
            print("Closing browser...")
            self.driver.quit()
            print("✓ Browser closed")


def main():
    """Main function with interactive menu"""
    print("="*70)
    print("Unified Legal Section Scraper - India Code")
    print("="*70)
    print()
    print("IMPORTANT NOTE:")
    print("India Code website uses JavaScript to load content.")
    print("BeautifulSoup mode won't work - use Selenium mode for scraping.")
    print()
    print("RECOMMENDATIONS:")
    print("1. Use existing database (criminal_law_kb.db)")
    print("2. Export data from database (Option 1)")
    print("3. Generate section URLs using the pattern (Option 2)")
    print("="*70)
    print()
    
    print("Select scraper mode:")
    print("1. BeautifulSoup (Fast, limited - for utility functions)")
    print("2. Selenium (Slower, works with JavaScript - for actual scraping)")
    print()
    
    mode_choice = input("Enter mode (1 or 2): ")
    mode = 'beautifulsoup' if mode_choice == '1' else 'selenium'
    
    scraper = UnifiedLegalScraper(mode=mode)
    
    try:
        print("\nOptions:")
        print("1. Export data from existing database")
        print("2. Generate section URL")
        print("3. Test connection")
        if mode == 'selenium':
            print("4. Scrape sections with Selenium")
        print("0. Exit")
        print()
        
        choice = input("Select an option: ")
        
        if choice == '1':
            print("\nExporting data from database...")
            sections = scraper.export_from_database()
            if sections:
                print(f"✓ Exported {len(sections)} sections")
        
        elif choice == '2':
            print("\nAvailable acts: BNS, BNSS, EVIDENCE")
            act = input("Enter act type: ").upper()
            section_num = input("Enter section number: ")
            try:
                url = scraper.generate_section_url(act, int(section_num))
                print(f"\nGenerated URL:\n{url}")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            print("\nTesting connection...")
            if scraper.test_connection():
                print("✓ Website is accessible!")
            else:
                print("✗ Cannot connect")
        
        elif choice == '4' and mode == 'selenium':
            print("\nAvailable acts: BNS, BNSS, EVIDENCE")
            act = input("Enter act type: ").upper()
            if act in scraper.act_ids:
                links = scraper.scrape_with_selenium(act)
                if links:
                    output_file = Path(__file__).parent / f"{act}_scraped_links.json"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(links, f, indent=2, ensure_ascii=False)
                    print(f"\n✓ Saved {len(links)} links to {output_file}")
        
        else:
            print("\nExiting...")
        
    finally:
        scraper.close()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
