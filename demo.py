#!/usr/bin/env python3
"""
Demo script to test the LinkedIn job scraper
"""

from database import JobDatabase
from scraper import scrape_linkedin_jobs
import time

def demo_scraper():
    """Demonstrate the scraper functionality"""
    print("🎬 LinkedIn Job Scraper Demo")
    print("=" * 50)
    
    # Initialize database
    print("📊 Initializing database...")
    db = JobDatabase()
    
    # Example company URLs to test
    example_urls = [
        "https://www.linkedin.com/company/microsoft/jobs/",
        "https://www.linkedin.com/company/google/jobs/",
        "https://www.linkedin.com/company/apple/jobs/"
    ]
    
    print(f"\n📋 Current job count in database: {db.get_job_count()}")
    
    print("\n🔍 Example LinkedIn company URLs you can try:")
    for i, url in enumerate(example_urls, 1):
        print(f"  {i}. {url}")
    
    print("\n💡 Tips for using the scraper:")
    print("  • Use company page URLs ending with /jobs/")
    print("  • The scraper will extract job titles, locations, and posting dates")
    print("  • Results are stored in SQLite database")
    print("  • View results in the web interface at http://localhost:5009")
    
    print("\n🚀 To start the web application:")
    print("  python app.py")
    print("  or")
    print("  python run.py")
    
    # Test database functionality
    print("\n🧪 Testing database functionality...")
    
    test_job = {
        'company_name': 'Test Company',
        'job_title': 'Test Developer',
        'job_location': 'Remote',
        'job_type': 'Full-time',
        'job_description': 'This is a test job',
        'job_url': 'https://example.com/job/123',
        'posted_date': '2024-01-01',
        'salary_range': '$80k-$120k',
        'experience_level': 'Mid-level',
        'department': 'Engineering'
    }
    
    success = db.insert_job(test_job)
    if success:
        print("✅ Test job inserted successfully")
        
        # Retrieve and display
        jobs_df = db.get_all_jobs()
        print(f"📈 Total jobs in database: {len(jobs_df)}")
        
        if not jobs_df.empty:
            print("\n📝 Recent jobs:")
            for _, job in jobs_df.head(3).iterrows():
                print(f"  • {job['company_name']}: {job['job_title']} ({job['job_location']})")
    else:
        print("❌ Failed to insert test job")
    
    print("\n" + "=" * 50)
    print("🎉 Demo completed! Ready to scrape LinkedIn jobs!")

if __name__ == "__main__":
    demo_scraper()