#!/usr/bin/env python3
"""
Batch LinkedIn Person Profile Scraper with Airtable Integration
"""

from person_scraper import scrape_linkedin_person
from airtable_client import AirtableClient
import time
import random
import os

def batch_scrape_profiles(profile_urls, airtable_config=None, delay_range=(2, 5)):
    """
    Scrape multiple LinkedIn profiles and optionally save to Airtable
    
    Args:
        profile_urls (list): List of LinkedIn profile URLs
        airtable_config (dict): Airtable configuration with api_key, base_id, table_name
        delay_range (tuple): Min and max delay between requests (seconds)
    
    Returns:
        dict: Results summary
    """
    
    print(f"🚀 Starting batch scrape of {len(profile_urls)} profiles")
    print("=" * 60)
    
    results = {
        'total_profiles': len(profile_urls),
        'successful_scrapes': 0,
        'failed_scrapes': 0,
        'airtable_uploads': 0,
        'airtable_failures': 0,
        'scraped_data': []
    }
    
    # Initialize Airtable client if config provided
    airtable_client = None
    if airtable_config:
        try:
            airtable_client = AirtableClient(
                airtable_config['api_key'],
                airtable_config['base_id'],
                airtable_config['table_name']
            )
            
            if airtable_client.test_connection():
                print("✅ Airtable connection verified")
            else:
                print("❌ Airtable connection failed - will save data locally only")
                airtable_client = None
        except Exception as e:
            print(f"❌ Airtable setup failed: {e}")
            airtable_client = None
    
    # Process each profile
    for i, profile_url in enumerate(profile_urls, 1):
        print(f"\n📍 Processing profile {i}/{len(profile_urls)}")
        print(f"🔗 URL: {profile_url}")
        
        try:
            # Scrape the profile
            person_data = scrape_linkedin_person(profile_url)
            
            if person_data['name'] or person_data['current_job_title'] or person_data['current_company']:
                results['successful_scrapes'] += 1
                results['scraped_data'].append(person_data)
                
                print(f"✅ Scraped: {person_data['name'] or 'Unknown Name'}")
                print(f"   Title: {person_data['current_job_title'] or 'Not found'}")
                print(f"   Company: {person_data['current_company'] or 'Not found'}")
                
                # Upload to Airtable if configured
                if airtable_client:
                    try:
                        result = airtable_client.create_record(person_data)
                        if result['success']:
                            results['airtable_uploads'] += 1
                            print(f"✅ Uploaded to Airtable: {result['record_id']}")
                        else:
                            results['airtable_failures'] += 1
                            print(f"❌ Airtable upload failed: {result['error']}")
                    except Exception as e:
                        results['airtable_failures'] += 1
                        print(f"❌ Airtable upload error: {e}")
                
            else:
                results['failed_scrapes'] += 1
                print("⚠️ No data extracted from profile")
                
        except Exception as e:
            results['failed_scrapes'] += 1
            print(f"❌ Scraping failed: {e}")
        
        # Rate limiting delay
        if i < len(profile_urls):  # Don't delay after the last profile
            delay = random.uniform(delay_range[0], delay_range[1])
            print(f"⏳ Waiting {delay:.1f} seconds before next profile...")
            time.sleep(delay)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 BATCH SCRAPING SUMMARY")
    print("=" * 60)
    print(f"📈 Total Profiles: {results['total_profiles']}")
    print(f"✅ Successful Scrapes: {results['successful_scrapes']}")
    print(f"❌ Failed Scrapes: {results['failed_scrapes']}")
    
    if airtable_client:
        print(f"📤 Airtable Uploads: {results['airtable_uploads']}")
        print(f"🚫 Airtable Failures: {results['airtable_failures']}")
    
    success_rate = (results['successful_scrapes'] / results['total_profiles']) * 100
    print(f"📊 Success Rate: {success_rate:.1f}%")
    
    return results

def main():
    """Example usage of batch scraper"""
    
    # Example profile URLs - replace with your target profiles
    example_profiles = [
        "https://www.linkedin.com/in/elizabeth-korchin/",
        # Add more profile URLs here
    ]
    
    # Airtable configuration - set these environment variables
    airtable_config = None
    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_name = os.getenv('AIRTABLE_TABLE_NAME', 'LinkedIn Profiles')
    
    if api_key and base_id:
        airtable_config = {
            'api_key': api_key,
            'base_id': base_id,
            'table_name': table_name
        }
        print("🔗 Airtable integration enabled")
    else:
        print("⚠️ Airtable not configured - data will be scraped but not uploaded")
        print("   Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID environment variables")
    
    # Run batch scrape
    results = batch_scrape_profiles(
        example_profiles,
        airtable_config=airtable_config,
        delay_range=(3, 7)  # 3-7 second delays between requests
    )
    
    # Save results locally as backup
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'scraping_results_{timestamp}.json'
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    main()