#!/usr/bin/env python3
"""
Simple Airtable connection test script
"""

from airtable_client import AirtableClient

def test_connection():
    """Test basic Airtable connection"""
    
    print("🔗 Testing Airtable Connection")
    print("=" * 40)
    
    # Configuration
    api_key = 'pat4Bm2KpOoZoxZJL.937f55e41e029315ed0540e91c00770e3f9c6cdc00e7a5d7d3e6a01bb7806fe3'
    base_id = 'appCv9G4AvrS18inO'
    table_name = 'LinkedIn Profiles'
    
    print(f"📊 Base ID: {base_id}")
    print(f"📋 Table: {table_name}")
    print(f"🔑 API Key: {api_key[:20]}...")
    
    try:
        # Initialize client
        airtable = AirtableClient(api_key, base_id, table_name)
        
        print("\n🧪 Testing connection...")
        
        # Test connection
        if airtable.test_connection():
            print("✅ Connection successful!")
            
            # Try to get existing records
            print("\n📋 Checking existing records...")
            records = airtable.get_records(max_records=3)
            print(f"📊 Found {len(records)} existing records")
            
            if records:
                print("\n📝 Sample record structure:")
                for i, record in enumerate(records[:1], 1):
                    print(f"Record {i}:")
                    for field, value in record.get('fields', {}).items():
                        print(f"  {field}: {str(value)[:50]}...")
            
            # Test with sample data
            print("\n🧪 Testing with sample data...")
            sample_data = {
                'name': 'Test User',
                'profile_photo': 'https://example.com/photo.jpg',
                'current_job_title': 'Test Engineer',
                'current_company': 'Test Company',
                'location': 'Test City',
                'skills': ['Python', 'Testing'],
                'linkedin_url': 'https://linkedin.com/in/test',
                'connections_count': '500+',
                'undergraduate_university': 'Test University',
                'graduate_schools': [{'school': 'Test Grad School', 'degree': 'MS Test'}]
            }
            
            result = airtable.create_record(sample_data)
            if result['success']:
                print(f"✅ Test record created: {result['record_id']}")
                print("\n🎉 Full integration working!")
            else:
                print(f"❌ Test record failed: {result['error']}")
                
        else:
            print("❌ Connection failed")
            print("\n💡 Common issues:")
            print("  1. Table 'LinkedIn Profiles' doesn't exist")
            print("  2. API token lacks permissions for this base")
            print("  3. Column names don't match exactly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        
        print("\n🔧 Setup checklist:")
        print("  □ Created table named 'LinkedIn Profiles'")
        print("  □ Added all required columns with exact names")
        print("  □ API token has access to base appCv9G4AvrS18inO")
        print("  □ Token has data.records:read and data.records:write scopes")
        print("\n📋 Required field names (case-sensitive):")
        print("  - Name")
        print("  - Profile Photo")
        print("  - Current Job Title")
        print("  - Current Company")
        print("  - Location")
        print("  - Skills")
        print("  - LinkedIn URL")
        print("  - Connections Count")
        print("  - Undergraduate University")
        print("  - Graduate Schools")
        print("  - Scraped Date")

if __name__ == "__main__":
    test_connection()