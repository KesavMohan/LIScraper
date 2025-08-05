#!/usr/bin/env python3
"""
Test script to upload Karen Travers' profile to Airtable
"""

from airtable_client import AirtableClient
from datetime import datetime

def test_karen_upload():
    """Test uploading Karen's profile to Airtable"""
    
    print('🔍 Testing Karen Travers Profile Upload')
    print('=' * 50)
    
    # Airtable configuration
    api_key = 'pat4Bm2KpOoZoxZJL.937f55e41e029315ed0540e91c00770e3f9c6cdc00e7a5d7d3e6a01bb7806fe3'
    base_id = 'appCv9G4AvrS18inO'
    table_name = 'LinkedIn Profiles'
    
    # Test profile
    profile_url = 'https://www.linkedin.com/in/karen-travers-16a0395/'
    print(f'📍 Profile: {profile_url}')
    
    # Create minimal person data with just the URL
    person_data = {
        'name': 'Karen Travers',
        'profile_photo': '',
        'current_job_title': '',
        'current_company': '',
        'location': '',
        'skills': [],
        'linkedin_url': profile_url,
        'connections_count': None,  # Use None instead of empty string for number field
        'undergraduate_university': '',
        'graduate_schools': []
    }
    
    try:
        # Initialize Airtable client
        airtable = AirtableClient(api_key, base_id, table_name)
        
        print('📤 Uploading to Airtable...')
        
        # Upload to Airtable
        result = airtable.create_record(person_data)
        
        if result.get('success'):
            print('✅ Successfully uploaded to Airtable!')
            print(f'📊 Record ID: {result.get("record_id", "Unknown")}')
            return True
        else:
            print('❌ Failed to upload to Airtable')
            print(f'Error: {result.get("error", "Unknown error")}')
            return False
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_karen_upload() 