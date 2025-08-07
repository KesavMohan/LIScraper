#!/usr/bin/env python3
"""
Simple Authenticated LinkedIn Profile Scraper
Uses requests-html for better compatibility
"""

import time
import random
import re
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from airtable_client import AirtableClient
from datetime import datetime
import os
from dotenv import load_dotenv

class SimpleAuthLinkedInScraper:
    def __init__(self):
        """Initialize the simple authenticated scraper"""
        self.session = HTMLSession()
        self.setup_session()
        
    def setup_session(self):
        """Setup the session with proper headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        print("✅ Session initialized successfully")
    
    def manual_login_instructions(self):
        """Provide instructions for manual login"""
        print("🔐 MANUAL LOGIN REQUIRED")
        print("=" * 40)
        print("Since LinkedIn has strong anti-bot protection, we need to:")
        print("1. Log in to LinkedIn manually in your browser")
        print("2. Copy your session cookies")
        print("3. Paste them here for authenticated scraping")
        print("\n📋 HOW TO GET COOKIES:")
        print("1. Open LinkedIn in Chrome")
        print("2. Log in normally")
        print("3. Press F12 to open Developer Tools")
        print("4. Go to Application tab > Cookies > https://www.linkedin.com")
        print("5. Copy the 'li_at' cookie value")
        print("\n🔑 Enter your li_at cookie value below:")
        
        li_at = input("li_at cookie: ").strip()
        if li_at:
            self.session.cookies.set('li_at', li_at, domain='.linkedin.com')
            print("✅ Cookie set successfully!")
            return True
        else:
            print("❌ No cookie provided")
            return False
    
    def scrape_profile_simple(self, profile_url):
        """
        Scrape a LinkedIn profile with session cookies
        
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
            # Add random delay
            time.sleep(random.uniform(2, 4))
            
            # Fetch the profile page
            response = self.session.get(profile_url)
            
            if response.status_code != 200:
                print(f"❌ HTTP {response.status_code} - Could not fetch profile")
                return person_data
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract name from page title or meta tags
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                # LinkedIn profile titles usually start with the person's name
                if ' | ' in title_text:
                    person_data['name'] = title_text.split(' | ')[0].strip()
                elif ' - ' in title_text:
                    person_data['name'] = title_text.split(' - ')[0].strip()
            
            # Try to extract from meta tags
            if not person_data['name']:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    person_data['name'] = meta_title.get('content', '').strip()
            
            # Extract profile photo from meta tags
            meta_image = soup.find('meta', property='og:image')
            if meta_image:
                person_data['profile_photo'] = meta_image.get('content', '')
            
            # Extract description (usually contains job info)
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc:
                desc_text = meta_desc.get('content', '')
                # Try to extract job title and company from description
                if ' at ' in desc_text:
                    parts = desc_text.split(' at ', 1)
                    person_data['current_job_title'] = parts[0].strip()
                    # Extract company (everything after 'at' but before other info)
                    company_part = parts[1].split('.')[0].split('|')[0].strip()
                    person_data['current_company'] = company_part
            
            # Look for structured data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if data.get('@type') == 'Person':
                            if not person_data['name'] and data.get('name'):
                                person_data['name'] = data['name']
                            if data.get('jobTitle'):
                                person_data['current_job_title'] = data['jobTitle']
                            if data.get('worksFor') and isinstance(data['worksFor'], dict):
                                person_data['current_company'] = data['worksFor'].get('name', '')
                except:
                    continue
            
            # Basic extraction report
            found_fields = []
            if person_data['name']: found_fields.append('Name')
            if person_data['profile_photo']: found_fields.append('Photo')
            if person_data['current_job_title']: found_fields.append('Job Title')
            if person_data['current_company']: found_fields.append('Company')
            if person_data['location']: found_fields.append('Location')
            
            print(f"✅ Extracted: {', '.join(found_fields) if found_fields else 'URL only'}")
            
        except Exception as e:
            print(f"❌ Error scraping profile: {e}")
        
        return person_data
    
    def batch_scrape_simple(self, profile_urls, upload_to_airtable=True):
        """
        Scrape multiple profiles with simple method
        
        Args:
            profile_urls (list): List of LinkedIn profile URLs
            upload_to_airtable (bool): Whether to upload to Airtable
            
        Returns:
            list: List of scraped profile data
        """
        print(f"\n🚀 Starting simple batch scrape of {len(profile_urls)} profiles")
        print("=" * 60)
        
        all_profile_data = []
        successful_uploads = 0
        
        # Initialize Airtable if needed
        airtable = None
        if upload_to_airtable:
            try:
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
            profile_data = self.scrape_profile_simple(profile_url)
            all_profile_data.append(profile_data)
            
            # Upload to Airtable if enabled and we have a name
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
            
            # Delay between profiles
            if i < len(profile_urls):
                delay = random.uniform(8, 15)  # Longer delays for simple method
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

def main():
    """Main function for testing simple scraper"""
    
    # Test profile URLs
    test_profiles = [
        "https://www.linkedin.com/in/karen-travers-16a0395/",
        # Add more profiles here
    ]
    
    print("🚀 Simple LinkedIn Authenticated Scraper")
    print("=" * 50)
    print("⚠️ This method requires manual cookie setup")
    print(f"Ready to test with {len(test_profiles)} profile(s)")
    
    response = input("\n▶️ Continue? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    try:
        # Initialize scraper
        scraper = SimpleAuthLinkedInScraper()
        
        # Get cookies manually
        if not scraper.manual_login_instructions():
            print("❌ Cookie setup failed - cannot continue")
            return
        
        # Scrape profiles
        profile_data = scraper.batch_scrape_simple(test_profiles, upload_to_airtable=True)
        
        print(f"\n✅ Simple scraping completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()