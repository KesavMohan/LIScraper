#!/usr/bin/env python3
"""
Test script to scrape 10 LinkedIn profiles with authentication
"""

from authenticated_scraper import AuthenticatedLinkedInScraper

def main():
    """Main function to test scraping 10 profiles"""
    
    # Test profiles - replace these with actual LinkedIn profile URLs
    test_profiles = [
        "https://www.linkedin.com/in/karen-travers-16a0395/",
        # Add 9 more LinkedIn profile URLs here
        # "https://www.linkedin.com/in/profile1/",
        # "https://www.linkedin.com/in/profile2/",
        # "https://www.linkedin.com/in/profile3/",
        # "https://www.linkedin.com/in/profile4/",
        # "https://www.linkedin.com/in/profile5/",
        # "https://www.linkedin.com/in/profile6/",
        # "https://www.linkedin.com/in/profile7/",
        # "https://www.linkedin.com/in/profile8/",
        # "https://www.linkedin.com/in/profile9/",
    ]
    
    print("🧪 Testing Authenticated LinkedIn Scraper")
    print("=" * 50)
    print(f"📋 Profiles to scrape: {len(test_profiles)}")
    print("\n📝 INSTRUCTIONS:")
    print("1. Make sure you have Chrome and ChromeDriver installed")
    print("2. Run: python setup_authenticated_scraper.py (if not done)")
    print("3. The scraper will open a browser window")
    print("4. Log in to LinkedIn manually when prompted")
    print("5. The scraper will automatically process all profiles")
    print("6. Data will be uploaded to your Airtable table")
    
    if len(test_profiles) < 10:
        print(f"\n⚠️ Only {len(test_profiles)} profile(s) configured")
        print("Add more LinkedIn profile URLs to the test_profiles list")
    
    # Confirm before proceeding
    print("\n🔐 IMPORTANT NOTES:")
    print("- This will use your LinkedIn login session")
    print("- Respect LinkedIn's rate limits and terms of service")
    print("- Use reasonable delays between profiles")
    print("- Only scrape profiles you have permission to view")
    
    response = input(f"\n▶️ Proceed with scraping {len(test_profiles)} profile(s)? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    scraper = None
    try:
        # Initialize scraper
        print("\n🚀 Initializing authenticated scraper...")
        scraper = AuthenticatedLinkedInScraper()
        
        # Login process
        print("\n🔐 Starting login process...")
        if not scraper.login_to_linkedin():
            print("❌ Login failed - cannot continue")
            return
        
        # Scrape profiles
        print(f"\n📊 Starting batch scrape of {len(test_profiles)} profiles...")
        profile_data = scraper.batch_scrape_profiles(test_profiles, upload_to_airtable=True)
        
        # Results summary
        successful_scrapes = len([p for p in profile_data if p.get('name')])
        
        print(f"\n🎉 SCRAPING COMPLETED!")
        print("=" * 30)
        print(f"📊 Total profiles processed: {len(test_profiles)}")
        print(f"✅ Successfully scraped: {successful_scrapes}")
        print(f"📤 Check your Airtable 'LinkedIn Profiles' table for the data")
        
        if successful_scrapes > 0:
            print(f"\n📋 Sample of extracted data:")
            for i, data in enumerate(profile_data[:3]):  # Show first 3
                if data.get('name'):
                    print(f"  {i+1}. {data['name']} - {data.get('current_job_title', 'No title')} at {data.get('current_company', 'No company')}")
        
        print(f"\n💡 Browser window kept open for inspection")
        print("Close it manually when you're done reviewing")
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Keep browser open for inspection
        if scraper:
            print("\n🔍 Keeping browser open for debugging...")
            # scraper.close()  # Uncomment to auto-close browser

if __name__ == "__main__":
    main()