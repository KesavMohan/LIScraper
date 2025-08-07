#!/usr/bin/env python3
"""
Authenticated LinkedIn Profile Scraper
This script logs into LinkedIn and scrapes profile data with authentication
"""

import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from airtable_client import AirtableClient
from datetime import datetime
import os
from dotenv import load_dotenv

class AuthenticatedLinkedInScraper:
    def __init__(self):
        """Initialize the authenticated scraper"""
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Keep browser open for debugging
        chrome_options.add_experimental_option("detach", True)
        
        try:
            # Try multiple approaches to initialize ChromeDriver
            driver_paths = [
                '/usr/local/bin/chromedriver',  # Manual installation
                ChromeDriverManager().install(),  # webdriver-manager
            ]
            
            for driver_path in driver_paths:
                try:
                    service = Service(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                    print(f"✅ Chrome driver initialized successfully with: {driver_path}")
                    return
                except Exception as path_error:
                    print(f"⚠️ Failed with {driver_path}: {path_error}")
                    continue
            
            raise Exception("Could not initialize ChromeDriver with any available path")
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            print("💡 Troubleshooting:")
            print("1. Make sure Google Chrome is installed")
            print("2. Try: pip install webdriver-manager --upgrade")
            print("3. Check Chrome version matches ChromeDriver")
            raise
    
    def login_to_linkedin(self):
        """
        Manual login process - opens LinkedIn login page
        User needs to manually log in through the browser
        """
        print("🔐 Starting LinkedIn login process...")
        print("=" * 50)
        
        try:
            # Navigate to LinkedIn login
            self.driver.get("https://www.linkedin.com/login")
            
            print("📋 MANUAL LOGIN REQUIRED:")
            print("1. The browser window has opened to LinkedIn login page")
            print("2. Please log in manually with your LinkedIn credentials")
            print("3. Complete any 2FA/security challenges if prompted")
            print("4. DON'T navigate to the feed - just stay logged in")
            print("5. Come back here and press ENTER when you're logged in")
            print("\n💡 TIP: Avoid the feed page - it's slow and not needed!")
            
            # Wait for user to confirm they're logged in
            input("\n⏳ Press ENTER after you've successfully logged in to LinkedIn...")
            
            # Verify we're logged in by checking for simpler logged-in elements
            try:
                print("🔍 Verifying login status...")
                
                # Try to go to a simpler page first (your own profile)
                try:
                    self.driver.get("https://www.linkedin.com/in/me/")
                    time.sleep(3)
                except:
                    pass
                
                # Wait for a logged-in indicator with longer timeout and simpler selectors
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "nav")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-global-nav-me]")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-photo")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "header")),
                    )
                )
                
                print("✅ Login verification successful!")
                print("🎯 Ready to start scraping profiles...")
                return True
                
            except TimeoutException:
                print("⚠️ Could not verify login status, but proceeding anyway...")
                print("Make sure you're logged in before continuing")
                return True
                
        except Exception as e:
            print(f"❌ Error during login process: {e}")
            return False
    
    def scrape_profile_authenticated(self, profile_url):
        """
        Scrape a LinkedIn profile with authentication
        
        Args:
            profile_url (str): LinkedIn profile URL
            
        Returns:
            dict: Extracted profile data
        """
        print(f"\n🔍 Scraping: {profile_url}")
        
        person_data = {
            'name': '',
            'profile_photo': '',
            'current_job_title': '',
            'current_company': '',
            'location': '',
            'skills': [],
            'linkedin_url': profile_url,
            'connections_count': '',
            'undergraduate_university': '',
            'graduate_schools': []
        }
        
        try:
            # Navigate to profile
            self.driver.get(profile_url)
            
            # Random delay to avoid detection
            time.sleep(random.uniform(3, 6))
            
            # Wait for profile to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract name
            name_selectors = [
                'h1.text-heading-xlarge',
                'h1.break-words',
                '.pv-text-details__left-panel h1',
                '.ph5 h1',
                'h1[class*="text-heading"]',
                '.top-card-layout__title',
                '.pv-top-card--photo h1'
            ]
            
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem and name_elem.get_text(strip=True):
                    person_data['name'] = name_elem.get_text(strip=True)
                    break
            
            # Extract profile photo
            photo_selectors = [
                '.pv-top-card--photo img',
                '.profile-photo-edit__preview img',
                '.presence-entity__image img',
                '.pv-top-card-profile-picture__image img',
                'img[data-delayed-url*="profile"]'
            ]
            
            for selector in photo_selectors:
                photo_elem = soup.select_one(selector)
                if photo_elem and photo_elem.get('src'):
                    person_data['profile_photo'] = photo_elem.get('src')
                    break
            
            # Extract current job title and company
            job_selectors = [
                '.text-body-medium.break-words',
                '.pv-text-details__left-panel .text-body-medium',
                '.top-card-layout__headline',
                '.pv-top-card--list-bullet li:first-child'
            ]
            
            for selector in job_selectors:
                job_elem = soup.select_one(selector)
                if job_elem:
                    job_text = job_elem.get_text(strip=True)
                    if ' at ' in job_text:
                        parts = job_text.split(' at ', 1)
                        person_data['current_job_title'] = parts[0].strip()
                        person_data['current_company'] = parts[1].strip()
                    else:
                        person_data['current_job_title'] = job_text
                    break
            
            # Extract location
            location_selectors = [
                '.text-body-small.inline.t-black--light.break-words',
                '.pv-text-details__left-panel .text-body-small',
                '.top-card-layout__first-subline',
                '.pv-top-card--list-bullet li:nth-child(2)'
            ]
            
            for selector in location_selectors:
                location_elem = soup.select_one(selector)
                if location_elem:
                    location_text = location_elem.get_text(strip=True)
                    # Filter out non-location text
                    if not any(keyword in location_text.lower() for keyword in ['connection', 'follower', 'contact', 'message']):
                        person_data['location'] = location_text
                        break
            
            # Extract connections count
            connections_selectors = [
                'span:contains("connection")',
                '.top-card-layout__first-subline',
                '.pv-top-card--list-bullet'
            ]
            
            # This is tricky with BeautifulSoup, so we'll try to find it in the page text
            page_text = soup.get_text()
            import re
            
            # Look for patterns like "500+ connections" or "1,234 connections"
            connection_patterns = [
                r'(\d{1,3}(?:,\d{3})*|\d+)\+?\s+connections?',
                r'(\d{1,3}(?:,\d{3})*|\d+)\s+connections?'
            ]
            
            for pattern in connection_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    person_data['connections_count'] = match.group(0)
                    break
            
            # Try to scroll to load more content (skills, education)
            try:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)
                
                # Look for skills section
                skills_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.skill-card-name, .hoverable-link-text')
                for skill_btn in skills_buttons[:10]:  # Limit to first 10 skills
                    skill_text = skill_btn.get_attribute('textContent')
                    if skill_text and skill_text.strip():
                        person_data['skills'].append(skill_text.strip())
                
            except Exception as e:
                print(f"⚠️ Could not extract skills: {e}")
            
            # Extract basic info about data found
            found_fields = []
            if person_data['name']: found_fields.append('Name')
            if person_data['profile_photo']: found_fields.append('Photo')
            if person_data['current_job_title']: found_fields.append('Job Title')
            if person_data['current_company']: found_fields.append('Company')
            if person_data['location']: found_fields.append('Location')
            if person_data['skills']: found_fields.append(f'Skills({len(person_data["skills"])})')
            if person_data['connections_count']: found_fields.append('Connections')
            
            print(f"✅ Extracted: {', '.join(found_fields) if found_fields else 'URL only'}")
            
        except TimeoutException:
            print("⚠️ Profile loading timed out")
        except Exception as e:
            print(f"❌ Error scraping profile: {e}")
        
        return person_data
    
    def batch_scrape_profiles(self, profile_urls, upload_to_airtable=True):
        """
        Scrape multiple profiles in batch
        
        Args:
            profile_urls (list): List of LinkedIn profile URLs
            upload_to_airtable (bool): Whether to upload to Airtable
            
        Returns:
            list: List of scraped profile data
        """
        print(f"\n🚀 Starting batch scrape of {len(profile_urls)} profiles")
        print("=" * 60)
        
        all_profile_data = []
        successful_uploads = 0
        
        # Initialize Airtable if needed
        airtable = None
        if upload_to_airtable:
            try:
                load_dotenv()
                api_key = 'pat4Bm2KpOoZoxZJL.937f55e41e029315ed0540e91c00770e3f9c6cdc00e7a5d7d3e6a01bb7806fe3'
                base_id = 'appCv9G4AvrS18inO'
                table_name = 'LinkedIn Profiles'
                airtable = AirtableClient(api_key, base_id, table_name)
                print("✅ Airtable client initialized")
            except Exception as e:
                print(f"⚠️ Airtable initialization failed: {e}")
                upload_to_airtable = False
        
        for i, profile_url in enumerate(profile_urls, 1):
            print(f"\n📊 Profile {i}/{len(profile_urls)}")
            
            # Scrape profile
            profile_data = self.scrape_profile_authenticated(profile_url)
            all_profile_data.append(profile_data)
            
            # Upload to Airtable if enabled
            if upload_to_airtable and airtable and profile_data.get('name'):
                try:
                    result = airtable.create_record(profile_data)
                    if result.get('success'):
                        successful_uploads += 1
                        print(f"✅ Uploaded to Airtable (ID: {result.get('record_id', 'Unknown')})")
                    else:
                        print(f"❌ Airtable upload failed: {result.get('error', 'Unknown')}")
                except Exception as e:
                    print(f"❌ Airtable upload error: {e}")
            
            # Delay between profiles to be respectful
            if i < len(profile_urls):
                delay = random.uniform(5, 10)
                print(f"⏳ Waiting {delay:.1f}s before next profile...")
                time.sleep(delay)
        
        # Summary
        print(f"\n📈 BATCH SCRAPING COMPLETE")
        print("=" * 40)
        print(f"📊 Total profiles: {len(profile_urls)}")
        print(f"✅ Successfully scraped: {len([p for p in all_profile_data if p.get('name')])}")
        if upload_to_airtable:
            print(f"📤 Uploaded to Airtable: {successful_uploads}")
        
        return all_profile_data
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("🔒 Browser closed")

def main():
    """Main function for testing"""
    scraper = None
    
    try:
        # Test profile URLs (replace with actual profiles you want to scrape)
        test_profiles = [
            "https://www.linkedin.com/in/karen-travers-16a0395/",
            # Add more profile URLs here for testing
            # "https://www.linkedin.com/in/another-profile/",
        ]
        
        print("🚀 LinkedIn Authenticated Scraper")
        print("=" * 50)
        print("⚠️ IMPORTANT: This will open a browser window")
        print("You'll need to manually log in to LinkedIn")
        print(f"Ready to scrape {len(test_profiles)} test profile(s)")
        
        # Confirm before proceeding
        response = input("\n▶️ Continue? (y/n): ").lower().strip()
        if response != 'y':
            print("❌ Cancelled")
            return
        
        # Initialize scraper
        scraper = AuthenticatedLinkedInScraper()
        
        # Login process
        if not scraper.login_to_linkedin():
            print("❌ Login failed - cannot continue")
            return
        
        # Scrape profiles
        profile_data = scraper.batch_scrape_profiles(test_profiles, upload_to_airtable=True)
        
        print(f"\n✅ Scraping completed! Check your Airtable for uploaded data.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper:
            print("\n🔒 Keeping browser open for inspection...")
            print("Close the browser window manually when done")
            # scraper.close()  # Comment out to keep browser open

if __name__ == "__main__":
    main()