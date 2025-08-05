#!/usr/bin/env python3
"""
Test script for LinkedIn Person Profile Scraper
"""

from person_scraper import scrape_linkedin_person
from airtable_client import AirtableClient
import os
from dotenv import load_dotenv

def test_person_scraper():
    """Test the person scraper with Elizabeth Korchin's profile"""
    
    print("🧪 Testing LinkedIn Person Profile Scraper")
    print("=" * 50)
    
    # Test profile URL
    test_profile = "https://www.linkedin.com/in/elizabeth-korchin/"
    
    print(f"📍 Testing with profile: {test_profile}")
    
    try:
        # Scrape the profile
        person_data = scrape_linkedin_person(test_profile)
        
        print("\n📋 Scraped Data:")
        print("-" * 20)
        print(f"Name: {person_data['name']}")
        print(f"Current Job Title: {person_data['current_job_title']}")
        print(f"Current Company: {person_data['current_company']}")
        print(f"LinkedIn URL: {person_data['linkedin_url']}")
        
        return person_data
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_airtable_integration(person_data):
    """Test Airtable integration (requires environment variables)"""
    
    print("\n🔗 Testing Airtable Integration")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_name = os.getenv('AIRTABLE_TABLE_NAME', 'LinkedIn Profiles')
    
    if not api_key or not base_id:
        print("⚠️ Airtable credentials not found in environment variables")
        print("To test Airtable integration, create a .env file with:")
        print("AIRTABLE_API_KEY=your_api_key_here")
        print("AIRTABLE_BASE_ID=your_base_id_here")
        print("AIRTABLE_TABLE_NAME=LinkedIn Profiles")
        return False
    
    try:
        # Initialize Airtable client
        airtable = AirtableClient(api_key, base_id, table_name)
        
        # Test connection
        if airtable.test_connection():
            print("✅ Airtable connection successful!")
            
            # Create record
            if person_data:
                result = airtable.create_record(person_data)
                if result['success']:
                    print(f"✅ Record created successfully! Record ID: {result['record_id']}")
                    return True
                else:
                    print(f"❌ Failed to create record: {result['error']}")
                    return False
            else:
                print("❌ No person data to upload")
                return False
        else:
            print("❌ Airtable connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Airtable: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 LinkedIn Person Profile Scraper Test")
    print("=" * 60)
    
    # Test the scraper
    person_data = test_person_scraper()
    
    if person_data:
        print("\n✅ Scraper test completed successfully!")
        
        # Test Airtable integration if credentials are available
        airtable_success = test_airtable_integration(person_data)
        
        if airtable_success:
            print("\n🎉 All tests passed! Ready for production use.")
        else:
            print("\n⚠️ Scraper works, but Airtable integration needs setup.")
    else:
        print("\n❌ Scraper test failed.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()