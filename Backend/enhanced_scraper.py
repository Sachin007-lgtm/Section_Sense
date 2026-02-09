"""
Enhanced Legal Section Scraper for India Code Website
Automatically scrapes and populates the Supabase database with legal sections

Features:
- Scrapes BNS, BNSS, and EVIDENCE acts
- Automatically populates Supabase PostgreSQL database
- Selenium-based scraping (handles JavaScript content)
- Batch processing with progress tracking
- Error handling and retry logic
- Detailed section parsing
"""

import os
import sys
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    sys.exit(1)


class EnhancedLegalScraper:
    """
    Enhanced scraper that:
    1. Scrapes legal sections from India Code website
    2. Parses section details
    3. Populates Supabase database
    """
    
    def __init__(self):
        """Initialize scraper with database connection"""
        self.base_url = "https://www.indiacode.nic.in"
        
        # Act configurations
        self.acts = {
            'BNS': {
                'name': 'Bharatiya Nyaya Sanhita, 2023',
                'act_id': 'AC_CEN_5_23_00048_2023-45_1719292564123',
                'start_section_id': 90366,
                'sections': 358,
                'code_prefix': 'BNS'
            },
            'BNSS': {
                'name': 'Bharatiya Nagarik Suraksha Sanhita, 2023',
                'act_id': 'AC_CEN_5_23_00049_202346_1719552320687',
                'start_section_id': 90988,
                'sections': 531,
                'code_prefix': 'BNSS'
            },
            'EVIDENCE': {
                'name': 'Bharatiya Sakshya Adhiniyam, 2023',
                'act_id': 'AC_CEN_5_23_00049_2023-47_1719292804654',
                'start_section_id': 90767,
                'sections': 170,
                'code_prefix': 'BSA'
            }
        }
        
        # Setup database
        self.setup_database()
        
        # Selenium setup
        self.driver = None
        self.selenium_available = False
        self._init_selenium()
        
        # Setup output directory for JSON files
        self.output_dir = Path(__file__).parent / "scraped_data"
        self.output_dir.mkdir(exist_ok=True)
        print(f"📁 Output directory: {self.output_dir}")
    
    def setup_database(self):
        """Setup database connection"""
        try:
            self.engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.db = SessionLocal()
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            print("✅ Database connection established")
            
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            sys.exit(1)
    
    def _init_selenium(self):
        """Initialize Selenium with Chrome"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            chrome_options = Options()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Uncomment for headless mode (faster but no visual feedback)
            # chrome_options.add_argument('--headless')
            # chrome_options.add_argument('--disable-gpu')
            
            self.chrome_options = chrome_options
            self.selenium_available = True
            print("✅ Selenium initialized")
            
        except ImportError:
            print("❌ Selenium not installed. Run: pip install selenium")
            sys.exit(1)
    
    def start_browser(self):
        """Start Chrome browser"""
        if not self.driver:
            from selenium import webdriver
            print("🌐 Starting Chrome browser...")
            self.driver = webdriver.Chrome(options=self.chrome_options)
            print("✅ Browser started")
    
    def close_browser(self):
        """Close browser"""
        if self.driver:
            print("🔒 Closing browser...")
            self.driver.quit()
            self.driver = None
            print("✅ Browser closed")
    
    def generate_section_url(self, act_type: str, section_number: int) -> str:
        """Generate URL for a specific section"""
        act_config = self.acts[act_type]
        section_id = act_config['start_section_id'] + (section_number - 1)
        
        url = (
            f"{self.base_url}/show-data?"
            f"abv=CEN&"
            f"statehandle=123456789/1362&"
            f"actid={act_config['act_id']}&"
            f"sectionId={section_id}&"
            f"sectionno={section_number}&"
            f"orderno={section_number}&"
            f"orgactid={act_config['act_id']}"
        )
        return url
    
    def scrape_section_details(self, act_type: str, section_number: int) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed information for a specific section
        
        Args:
            act_type: Act type (BNS, BNSS, EVIDENCE)
            section_number: Section number to scrape
        
        Returns:
            Dictionary with section details or None if failed
        """
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        url = self.generate_section_url(act_type, section_number)
        act_config = self.acts[act_type]
        
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for content to load
            
            # Extract section title
            title = ""
            try:
                title_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h3, .section-title, .title"))
                )
                title = title_element.text.strip()
            except:
                title = f"Section {section_number}"
            
            # Extract section content/description
            description = ""
            try:
                # Try multiple selectors for content
                selectors = [
                    ".section-content",
                    ".content",
                    "#section-text",
                    "div[class*='section']",
                    "p"
                ]
                
                for selector in selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        description = "\n".join([el.text.strip() for el in elements if el.text.strip()])
                        if description:
                            break
                
                # If no description found, get page text
                if not description:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    description = body.text.strip()
                
            except Exception as e:
                print(f"  ⚠️  Could not extract description: {e}")
                description = f"Content for section {section_number}"
            
            # Determine category from section number ranges (BNS specific)
            category = self._determine_category(act_type, section_number, title, description)
            
            # Parse punishment details (basic extraction)
            punishment = self._extract_punishment(description)
            
            section_data = {
                'section_code': f"{act_config['code_prefix']} {section_number}",
                'section_number': str(section_number),
                'title': title,
                'description': description[:5000],  # Limit length
                'category': category,
                'punishment': punishment,
                'source': url,
                'act_name': act_config['name']
            }
            
            return section_data
            
        except Exception as e:
            print(f"  ❌ Error scraping section {section_number}: {e}")
            return None
    
    def _determine_category(self, act_type: str, section_number: int, title: str, description: str) -> str:
        """Determine category based on section number and content"""
        
        # For BNS - based on IPC structure
        if act_type == 'BNS':
            if 1 <= section_number <= 5:
                return "General Provisions"
            elif 6 <= section_number <= 52:
                return "General Explanations"
            elif 53 <= section_number <= 75:
                return "Punishments"
            elif 76 <= section_number <= 106:
                return "General Exceptions"
            elif 107 <= section_number <= 120:
                return "Abetment"
            elif 121 <= section_number <= 130:
                return "Criminal Conspiracy"
            elif 131 <= section_number <= 171:
                return "Offences Against the State"
            elif 172 <= section_number <= 190:
                return "Offences Against Public Tranquility"
            elif 191 <= section_number <= 229:
                return "Offences by or Relating to Public Servants"
            elif 230 <= section_number <= 263:
                return "Offences Relating to Elections"
            elif 264 <= section_number <= 267:
                return "Offences Relating to Coin and Government Stamps"
            elif 268 <= section_number <= 294:
                return "Offences Affecting the Human Body"
            else:
                return "Other Offences"
        
        # For BNSS - procedural law
        elif act_type == 'BNSS':
            if section_number <= 35:
                return "Preliminary"
            elif section_number <= 100:
                return "Constitution of Criminal Courts"
            elif section_number <= 200:
                return "Powers of Courts"
            elif section_number <= 300:
                return "Arrest"
            elif section_number <= 400:
                return "Processes to Compel Appearance"
            else:
                return "Other Procedures"
        
        # For EVIDENCE - evidence law
        elif act_type == 'EVIDENCE':
            if section_number <= 5:
                return "Preliminary"
            elif section_number <= 55:
                return "Relevancy of Facts"
            elif section_number <= 100:
                return "Admission and Confession"
            elif section_number <= 165:
                return "Witnesses"
            else:
                return "Documentary Evidence"
        
        return "Uncategorized"
    
    def _extract_punishment(self, text: str) -> Optional[str]:
        """Extract punishment details from section text"""
        # Look for common punishment patterns
        patterns = [
            r'punish(?:ed|able).*?(?:imprisonment|fine|death|life)',
            r'imprisonment.*?(?:years?|months?|life)',
            r'fine.*?(?:rupees|extend)',
            r'death.*?penalty',
        ]
        
        punishment_texts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            punishment_texts.extend(matches)
        
        if punishment_texts:
            return " | ".join(punishment_texts[:3])  # Limit to first 3 matches
        return None
    
    def save_to_json(self, act_type: str, sections_data: List[Dict[str, Any]]) -> str:
        """Save scraped sections to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{act_type}_sections_{timestamp}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sections_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved to: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"❌ Error saving JSON: {e}")
            return ""
    
    def insert_section(self, section_data: Dict[str, Any]) -> bool:
        """Insert section into database"""
        try:
            # Check if section already exists
            check_query = text("""
                SELECT id FROM law_sections 
                WHERE section_code = :section_code
            """)
            existing = self.db.execute(check_query, {"section_code": section_data['section_code']}).fetchone()
            
            if existing:
                print(f"  ℹ️  Section {section_data['section_code']} already exists, skipping")
                return True
            
            # Insert new section
            insert_query = text("""
                INSERT INTO law_sections 
                (section_code, section_number, title, description, category, punishment, source, created_at, last_updated)
                VALUES 
                (:section_code, :section_number, :title, :description, :category, :punishment, :source, NOW(), NOW())
            """)
            
            self.db.execute(insert_query, section_data)
            self.db.commit()
            
            print(f"  ✅ Inserted: {section_data['section_code']} - {section_data['title'][:50]}")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"  ❌ Database error: {e}")
            return False
    
    def scrape_act(self, act_type: str, start_section: int = 1, end_section: Optional[int] = None, save_to_db: bool = True, save_to_file: bool = True):
        """
        Scrape all sections for an act
        
        Args:
            act_type: Act type (BNS, BNSS, EVIDENCE)
            start_section: Starting section number
            end_section: Ending section number (None = all sections)
            save_to_db: Whether to save to database
            save_to_file: Whether to save to JSON file
        """
        act_config = self.acts[act_type]
        
        if end_section is None:
            end_section = act_config['sections']
        
        print(f"\n{'='*70}")
        print(f"📖 Scraping: {act_config['name']}")
        print(f"📋 Sections: {start_section} to {end_section}")
        print(f"💾 Save to DB: {save_to_db} | Save to File: {save_to_file}")
        print(f"{'='*70}\n")
        
        self.start_browser()
        
        success_count = 0
        fail_count = 0
        scraped_sections = []
        
        for section_num in range(start_section, end_section + 1):
            print(f"[{section_num}/{end_section}] Scraping section {section_num}...")
            
            section_data = self.scrape_section_details(act_type, section_num)
            
            if section_data:
                scraped_sections.append(section_data)
                
                if save_to_db:
                    if self.insert_section(section_data):
                        success_count += 1
                    else:
                        fail_count += 1
                else:
                    success_count += 1
                    print(f"  ✅ Scraped: {section_data['section_code']} - {section_data['title'][:50]}")
            else:
                fail_count += 1
            
            # Rate limiting
            time.sleep(1)
        
        # Save to JSON file
        if save_to_file and scraped_sections:
            self.save_to_json(act_type, scraped_sections)
        
        print(f"\n{'='*70}")
        print(f"✅ Completed: {success_count} sections scraped successfully")
        print(f"❌ Failed: {fail_count} sections")
        print(f"{'='*70}\n")
    
    def scrape_all_acts(self):
        """Scrape all configured acts"""
        print("\n🚀 Starting comprehensive scraping of all acts...\n")
        
        for act_type in self.acts.keys():
            try:
                self.scrape_act(act_type)
            except Exception as e:
                print(f"❌ Error scraping {act_type}: {e}")
                continue
        
        self.close_browser()
        print("\n🎉 All acts scraped successfully!")
    
    def cleanup(self):
        """Cleanup resources"""
        self.close_browser()
        if self.db:
            self.db.close()
            print("✅ Database connection closed")


def main():
    """Main function with interactive menu"""
    print("="*70)
    print("🔍 Enhanced Legal Section Scraper - India Code → Supabase")
    print("="*70)
    print()
    
    scraper = EnhancedLegalScraper()
    
    try:
        print("Select an option:")
        print("1. Scrape all acts (BNS + BNSS + EVIDENCE) → Database + File")
        print("2. Scrape specific act → Database + File")
        print("3. Scrape specific sections of an act → Database + File")
        print("4. Test scraping (first 5 sections of BNS) → Database + File")
        print("5. Scrape to LOCAL FILES ONLY (no database)")
        print("0. Exit")
        print()
        
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            confirm = input("\n⚠️  This will scrape 1000+ sections. Continue? (y/n): ")
            if confirm.lower() == 'y':
                scraper.scrape_all_acts()
        
        elif choice == '2':
            print("\nAvailable acts:")
            for act_type, config in scraper.acts.items():
                print(f"  {act_type}: {config['name']} ({config['sections']} sections)")
            
            act_type = input("\nEnter act type (BNS/BNSS/EVIDENCE): ").upper()
            if act_type in scraper.acts:
                scraper.scrape_act(act_type)
            else:
                print("❌ Invalid act type")
        
        elif choice == '3':
            print("\nAvailable acts:")
            for act_type, config in scraper.acts.items():
                print(f"  {act_type}: {config['name']} ({config['sections']} sections)")
            
            act_type = input("\nEnter act type (BNS/BNSS/EVIDENCE): ").upper()
            if act_type not in scraper.acts:
                print("❌ Invalid act type")
            else:
                start = int(input(f"Enter start section (1-{scraper.acts[act_type]['sections']}): "))
                end = int(input(f"Enter end section ({start}-{scraper.acts[act_type]['sections']}): "))
                scraper.scrape_act(act_type, start, end)
        
        elif choice == '4':
            print("\n🧪 Testing with first 5 sections of BNS...")
            scraper.scrape_act('BNS', 1, 5)
        
        elif choice == '5':
            print("\n📁 SCRAPE TO LOCAL FILES ONLY (No Database)")
            print("\nAvailable acts:")
            for act_type, config in scraper.acts.items():
                print(f"  {act_type}: {config['name']} ({config['sections']} sections)")
            
            act_type = input("\nEnter act type (BNS/BNSS/EVIDENCE): ").upper()
            if act_type not in scraper.acts:
                print("❌ Invalid act type")
            else:
                start = int(input(f"Enter start section (1-{scraper.acts[act_type]['sections']}): "))
                end = int(input(f"Enter end section ({start}-{scraper.acts[act_type]['sections']}): "))
                print("\n💾 Scraping to local files only...")
                scraper.scrape_act(act_type, start, end, save_to_db=False, save_to_file=True)
        
        else:
            print("Exiting...")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
