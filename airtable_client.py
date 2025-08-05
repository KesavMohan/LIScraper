import requests
import json
from datetime import datetime

class AirtableClient:
    def __init__(self, api_key, base_id, table_name):
        """
        Initialize Airtable client
        
        Args:
            api_key (str): Your Airtable API key (starts with 'pat')
            base_id (str): Your Airtable base ID (starts with 'app')
            table_name (str): Name of your table (e.g., 'LinkedIn Profiles')
        """
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_record(self, person_data):
        """
        Create a new record in Airtable
        
        Args:
            person_data (dict): Dictionary with person data
                - name: Person's full name
                - profile_photo: URL to profile photo
                - current_job_title: Current job title
                - current_company: Current company
                - location: Geographic location
                - skills: List of skills
                - linkedin_url: LinkedIn profile URL
                - connections_count: Number of LinkedIn connections
                - undergraduate_university: Undergraduate school
                - graduate_schools: List of graduate schools with degrees
        
        Returns:
            dict: Airtable response or error info
        """
        try:
            # Prepare data for Airtable
            # Convert skills list to comma-separated string
            skills_str = ', '.join(person_data.get('skills', [])) if person_data.get('skills') else ''
            
            # Convert graduate schools list to formatted string
            grad_schools_str = ''
            if person_data.get('graduate_schools'):
                grad_schools_list = []
                for school in person_data['graduate_schools']:
                    if school.get('degree'):
                        grad_schools_list.append(f"{school['school']} ({school['degree']})")
                    else:
                        grad_schools_list.append(school['school'])
                grad_schools_str = '; '.join(grad_schools_list)
            
            record_data = {
                "records": [
                    {
                        "fields": {
                            "Full Name": person_data.get('name', ''),
                            "Profile Photo": person_data.get('profile_photo', ''),
                            "Current Job Title": person_data.get('current_job_title', ''),
                            "Current Company": person_data.get('current_company', ''),
                            "Location": person_data.get('location', ''),
                            "Skills": skills_str,
                            "LinkedIn URL": person_data.get('linkedin_url', ''),
                            "Number of Connections": person_data.get('connections_count', ''),
                            "Scraped Date": datetime.now().isoformat()
                        }
                    }
                ]
            }
            
            print(f"Sending to Airtable: {record_data}")
            
            response = requests.post(
                self.base_url,
                headers=self.headers,
                data=json.dumps(record_data)
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully created record: {result['records'][0]['id']}")
                return {"success": True, "record_id": result['records'][0]['id'], "data": result}
            else:
                print(f"❌ Error creating record: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text, "status_code": response.status_code}
                
        except Exception as e:
            print(f"❌ Exception creating record: {e}")
            return {"success": False, "error": str(e)}
    
    def create_records_batch(self, people_data_list):
        """
        Create multiple records in Airtable (batch operation)
        
        Args:
            people_data_list (list): List of person data dictionaries
        
        Returns:
            dict: Summary of batch operation
        """
        success_count = 0
        failed_count = 0
        results = []
        
        # Airtable allows max 10 records per request
        batch_size = 10
        
        for i in range(0, len(people_data_list), batch_size):
            batch = people_data_list[i:i + batch_size]
            
            try:
                records = []
                for person_data in batch:
                    # Convert skills list to comma-separated string
                    skills_str = ', '.join(person_data.get('skills', [])) if person_data.get('skills') else ''
                    
                    # Convert graduate schools list to formatted string
                    grad_schools_str = ''
                    if person_data.get('graduate_schools'):
                        grad_schools_list = []
                        for school in person_data['graduate_schools']:
                            if school.get('degree'):
                                grad_schools_list.append(f"{school['school']} ({school['degree']})")
                            else:
                                grad_schools_list.append(school['school'])
                        grad_schools_str = '; '.join(grad_schools_list)
                    
                    records.append({
                        "fields": {
                            "Full Name": person_data.get('name', ''),
                            "Profile Photo": person_data.get('profile_photo', ''),
                            "Current Job Title": person_data.get('current_job_title', ''),
                            "Current Company": person_data.get('current_company', ''),
                            "Location": person_data.get('location', ''),
                            "Skills": skills_str,
                            "LinkedIn URL": person_data.get('linkedin_url', ''),
                            "Number of Connections": person_data.get('connections_count', ''),
                            "Scraped Date": datetime.now().isoformat()
                        }
                    })
                
                batch_data = {"records": records}
                
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    data=json.dumps(batch_data)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    success_count += len(result['records'])
                    results.extend(result['records'])
                    print(f"✅ Batch {i//batch_size + 1}: Created {len(result['records'])} records")
                else:
                    failed_count += len(batch)
                    print(f"❌ Batch {i//batch_size + 1} failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                failed_count += len(batch)
                print(f"❌ Batch {i//batch_size + 1} exception: {e}")
        
        return {
            "success_count": success_count,
            "failed_count": failed_count,
            "total_processed": len(people_data_list),
            "results": results
        }
    
    def get_records(self, max_records=100):
        """
        Get records from Airtable
        
        Args:
            max_records (int): Maximum number of records to retrieve
            
        Returns:
            list: List of records from Airtable
        """
        try:
            params = {"maxRecords": max_records}
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('records', [])
            else:
                print(f"❌ Error getting records: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Exception getting records: {e}")
            return []
    
    def test_connection(self):
        """Test the connection to Airtable"""
        try:
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params={"maxRecords": 1}
            )
            
            if response.status_code == 200:
                print("✅ Airtable connection successful!")
                return True
            else:
                print(f"❌ Airtable connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Airtable connection exception: {e}")
            return False