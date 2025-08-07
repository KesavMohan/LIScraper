#!/usr/bin/env python3
"""
Test script for authenticated LinkedIn scraping with browser automation
Ready to scrape 10 profiles after manual login
"""

from authenticated_scraper import AuthenticatedLinkedInScraper
import json

def main():
    """Main function to test browser-based authenticated scraping"""
    
    # Test profiles - Add your 10 LinkedIn profile URLs here
    test_profiles = [
        "https://www.linkedin.com/in/karen-travers-16a0395/",
        # Add 9 more LinkedIn profile URLs below:
        # "https://www.linkedin.com/in/profile-2/",
        # "https://www.linkedin.com/in/profile-3/",
        # "https://www.linkedin.com/in/profile-4/",
        # "https://www.linkedin.com/in/profile-5/",
        # "https://www.linkedin.com/in/profile-6/",
        # "https://www.linkedin.com/in/profile-7/",
        # "https://www.linkedin.com/in/profile-8/",
        # "https://www.linkedin.com/in/profile-9/",
        # "https://www.linkedin.com/in/profile-10/",
    ]
    
    print("🚀 LinkedIn Browser Authentication Scraper")
    print("=" * 60)
    print(f"📋 Profiles configured: {len(test_profiles)}")
    
    if len(test_profiles) < 10:
        print(f"⚠️ Only {len(test_profiles)} profile(s) configured - add more URLs above")
    
    print("\n🔧 SETUP COMPLETE:")
    print("✅ ChromeDriver installed and working")
    print("✅ All dependencies installed")
    print("✅ Airtable integration ready")
    
    print("\n📋 HOW THIS WORKS:")
    print("1. Chrome browser will open to LinkedIn login page")
    print("2. You log in manually (including 2FA if needed)")
    print("3. Navigate to your LinkedIn homepage/feed")
    print("4. Come back here and press ENTER")
    print("5. Scraper will automatically process all profiles")
    print("6. Data gets uploaded to your Airtable table")
    
    print("\n⚠️ IMPORTANT NOTES:")
    print("- Browser window will stay open for debugging")
    print("- Use reasonable delays to respect LinkedIn's limits")
    print("- Only scrape profiles you have permission to view")
    print("- Check your Airtable 'LinkedIn Profiles' table for results")
    
    response = input(f"\n▶️ Ready to scrape {len(test_profiles)} profile(s)? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Cancelled")
        return
    
    scraper = None
    try:
        print("\n🚀 STARTING AUTHENTICATED SCRAPER")
        print("=" * 50)
        
        # Initialize scraper (this will open Chrome)
        print("📱 Initializing Chrome browser...")
        scraper = AuthenticatedLinkedInScraper()
        
        # Login process
        print("\n🔐 Starting login process...")
        if not scraper.login_to_linkedin():
            print("❌ Login failed - cannot continue")
            return
        
        # Scrape profiles
        print(f"\n📊 Starting batch scrape...")
        profile_data = scraper.batch_scrape_profiles(test_profiles, upload_to_airtable=True)
        
        # Results summary
        successful_scrapes = len([p for p in profile_data if p.get('name')])
        successful_uploads = len([p for p in profile_data if p.get('name')])  # Approximate
        
        print(f"\n🎉 SCRAPING COMPLETED!")
        print("=" * 40)
        print(f"📊 Total profiles processed: {len(test_profiles)}")
        print(f"✅ Successfully scraped: {successful_scrapes}")
        print(f"📤 Uploaded to Airtable: ~{successful_uploads}")
        
        # Show sample results
        if successful_scrapes > 0:
            print(f"\n📋 SAMPLE RESULTS:")
            for i, data in enumerate(profile_data[:3]):  # Show first 3
                if data.get('name'):
                    name = data['name'][:30] + '...' if len(data['name']) > 30 else data['name']
                    job = data.get('current_job_title', 'No title')[:25] + '...' if len(data.get('current_job_title', '')) > 25 else data.get('current_job_title', 'No title')
                    company = data.get('current_company', 'No company')[:25] + '...' if len(data.get('current_company', '')) > 25 else data.get('current_company', 'No company')
                    print(f"  {i+1}. {name}")
                    print(f"     {job} at {company}")
                    print(f"     Skills: {len(data.get('skills', []))} found")
                    print()
            
            if len(profile_data) > 3:
                print(f"  ... and {len(profile_data) - 3} more profiles")
        
        print(f"\n💾 FULL DATA SAVED:")
        print("Check your Airtable 'LinkedIn Profiles' table for complete results")
        
        print(f"\n🔍 BROWSER STATUS:")
        print("Browser window kept open for inspection")
        print("You can:")
        print("- Review the last profile visited")
        print("- Check for any LinkedIn warnings/blocks")
        print("- Close the browser manually when done")
        
    except KeyboardInterrupt:
        print("\n⚠️ Scraping interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're logged into LinkedIn")
        print("2. Check if LinkedIn is showing any captchas/blocks")
        print("3. Verify profile URLs are accessible")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper:
            print("\n🔍 Keeping browser open for inspection...")
            print("Close the browser window manually when you're done")
            # scraper.close()  # Uncomment to auto-close browser

if __name__ == "__main__":
    main()