import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import random
import json
from requests_html import HTMLSession

class LinkedInPersonScraper:
    def __init__(self):
        self.session = HTMLSession()
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with appropriate headers"""
        # Use a more realistic browser user agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def get_page_content(self, url):
        """Get page content with error handling"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # For JavaScript-heavy pages, we might need to render
            try:
                response.html.render(timeout=20)
            except:
                # If rendering fails, continue with static content
                pass
            
            return response.html.html
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_person_data(self, profile_url):
        """Extract person data from LinkedIn profile page"""
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
            content = self.get_page_content(profile_url)
            if not content:
                print("Failed to get page content")
                return person_data
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract name - try multiple approaches
            name_selectors = [
                'h1.text-heading-xlarge',
                'h1.break-words', 
                '.pv-text-details__left-panel h1',
                '.ph5 h1',
                '[data-generated-suggestion-target] h1',
                'h1[class*="text-heading"]',
                '.top-card-layout__title',
                '.pv-top-card--photo h1'
            ]
            
            for selector in name_selectors:
                name_element = soup.select_one(selector)
                if name_element:
                    person_data['name'] = name_element.get_text(strip=True)
                    print(f"Found name: {person_data['name']}")
                    break
            
            # Alternative: Look for name in page title or meta tags
            if not person_data['name']:
                title = soup.find('title')
                if title:
                    title_text = title.get_text()
                    # LinkedIn profile titles often have format "Name | LinkedIn"
                    if '|' in title_text:
                        name_part = title_text.split('|')[0].strip()
                        if name_part and len(name_part) < 100:  # Reasonable name length
                            person_data['name'] = name_part
                            print(f"Found name from title: {person_data['name']}")
            
            # Look in meta tags
            if not person_data['name']:
                meta_name = soup.find('meta', {'property': 'profile:first_name'})
                meta_last = soup.find('meta', {'property': 'profile:last_name'})
                if meta_name and meta_last:
                    first_name = meta_name.get('content', '')
                    last_name = meta_last.get('content', '')
                    if first_name and last_name:
                        person_data['name'] = f"{first_name} {last_name}"
                        print(f"Found name from meta: {person_data['name']}")
                
                # Alternative meta tag
                if not person_data['name']:
                    meta_title = soup.find('meta', {'property': 'og:title'})
                    if meta_title:
                        og_title = meta_title.get('content', '')
                        if og_title and '|' in og_title:
                            name_part = og_title.split('|')[0].strip()
                            if name_part:
                                person_data['name'] = name_part
                                print(f"Found name from og:title: {person_data['name']}")
            
            # Extract profile photo
            photo_selectors = [
                '.pv-top-card--photo img',
                '.profile-photo-edit__preview img',
                '.pv-top-card-profile-picture__image',
                '.presence-entity__image img',
                '[data-anonymize="headshot"] img'
            ]
            
            for selector in photo_selectors:
                photo_element = soup.select_one(selector)
                if photo_element:
                    photo_src = photo_element.get('src', '')
                    if photo_src and 'http' in photo_src:
                        person_data['profile_photo'] = photo_src
                        print(f"Found profile photo: {photo_src[:50]}...")
                        break
            
            # Extract location
            location_selectors = [
                '.pv-text-details__left-panel .text-body-small',
                '.pv-top-card--list-bullet li',
                '.top-card-layout__card .text-body-small',
                '.pv-top-card-profile-picture__container + div .text-body-small'
            ]
            
            for selector in location_selectors:
                location_elements = soup.select(selector)
                for location_element in location_elements:
                    location_text = location_element.get_text(strip=True)
                    # Location typically doesn't contain numbers or @ symbols
                    if location_text and not re.search(r'[\d@]', location_text) and len(location_text) > 3:
                        person_data['location'] = location_text
                        print(f"Found location: {person_data['location']}")
                        break
                if person_data['location']:
                    break
            
            # Extract connections count
            connections_selectors = [
                '.pv-top-card--list-bullet .link-without-visited-state',
                '.pv-top-card--list-bullet a[href*="connections"]',
                '.top-card-layout__card a[href*="connections"]'
            ]
            
            for selector in connections_selectors:
                connections_element = soup.select_one(selector)
                if connections_element:
                    connections_text = connections_element.get_text(strip=True)
                    # Extract number from text like "500+ connections"
                    connections_match = re.search(r'(\d+[\+]?)', connections_text)
                    if connections_match:
                        person_data['connections_count'] = connections_match.group(1)
                        print(f"Found connections: {person_data['connections_count']}")
                        break
            
            # Extract current job title and company
            # Look for the most recent/current position
            job_selectors = [
                '.pv-text-details__left-panel .text-body-medium',
                '.ph5 .text-body-medium',
                '.pv-entity__summary-info h3',
                '.pv-entity__summary-info .pv-entity__secondary-title',
                '.experience-section .pv-entity__summary-info'
            ]
            
            # Try to find current position in experience section
            experience_sections = soup.select('.experience-section .pv-entity__summary-info, .pvs-entity, .artdeco-list__item')
            
            if experience_sections:
                # Get the first (most recent) experience
                first_experience = experience_sections[0]
                
                # Extract job title
                title_selectors = [
                    'h3',
                    '.mr1 .hoverable-link-text',
                    '.t-16 .hoverable-link-text',
                    '[data-field="experience_company_logo"] + div h3'
                ]
                
                for selector in title_selectors:
                    title_element = first_experience.select_one(selector)
                    if title_element:
                        person_data['current_job_title'] = title_element.get_text(strip=True)
                        print(f"Found job title: {person_data['current_job_title']}")
                        break
                
                # Extract company name
                company_selectors = [
                    '.pv-entity__secondary-title',
                    '.t-14 .hoverable-link-text',
                    '.pvs-entity__caption-wrapper',
                    'span[aria-hidden="true"]'
                ]
                
                for selector in company_selectors:
                    company_element = first_experience.select_one(selector)
                    if company_element:
                        company_text = company_element.get_text(strip=True)
                        # Clean up company name (remove extra text like "· Full-time")
                        company_text = re.split(r'[·•]', company_text)[0].strip()
                        if company_text and company_text != person_data['current_job_title']:
                            person_data['current_company'] = company_text
                            print(f"Found company: {person_data['current_company']}")
                            break
            
            # Alternative: Look for current position in the main header area
            if not person_data['current_job_title']:
                header_job_selectors = [
                    '.text-body-medium.break-words',
                    '.pv-text-details__left-panel .text-body-medium',
                    '.ph5 .text-body-medium',
                    '.top-card-layout__headline',
                    '.pv-top-card--headline'
                ]
                
                for selector in header_job_selectors:
                    job_element = soup.select_one(selector)
                    if job_element:
                        job_text = job_element.get_text(strip=True)
                        if ' at ' in job_text:
                            parts = job_text.split(' at ')
                            person_data['current_job_title'] = parts[0].strip()
                            person_data['current_company'] = parts[1].strip()
                        else:
                            person_data['current_job_title'] = job_text
                        break
            
            # Try to extract from meta description
            if not person_data['current_job_title'] or not person_data['current_company']:
                meta_desc = soup.find('meta', {'name': 'description'})
                if meta_desc:
                    desc_content = meta_desc.get('content', '')
                    # LinkedIn descriptions often contain job info
                    if ' at ' in desc_content:
                        parts = desc_content.split(' at ')
                        if len(parts) >= 2:
                            if not person_data['current_job_title']:
                                person_data['current_job_title'] = parts[0].strip()
                            if not person_data['current_company']:
                                company_part = parts[1].split('.')[0].strip()  # Remove extra text after period
                                person_data['current_company'] = company_part
            
            # Look in structured data for additional info
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict):
                        if 'name' in data and not person_data['name']:
                            person_data['name'] = data['name']
                        if 'jobTitle' in data and not person_data['current_job_title']:
                            person_data['current_job_title'] = data['jobTitle']
                        if 'worksFor' in data and not person_data['current_company']:
                            if isinstance(data['worksFor'], dict) and 'name' in data['worksFor']:
                                person_data['current_company'] = data['worksFor']['name']
                except:
                    continue
            
            # Extract skills
            skills_selectors = [
                '.pv-skill-category-entity__skill-wrapper .pv-skill-category-entity__name-text',
                '.skill-category-entity .pv-skill-category-entity__name span',
                '.pvs-entity .mr1.hoverable-link-text span[aria-hidden="true"]',
                '.skills-section .pv-skill-category-entity__name-text'
            ]
            
            skills_found = set()  # Use set to avoid duplicates
            for selector in skills_selectors:
                skill_elements = soup.select(selector)
                for skill_element in skill_elements:
                    skill_text = skill_element.get_text(strip=True)
                    if skill_text and len(skill_text) < 50:  # Reasonable skill name length
                        skills_found.add(skill_text)
            
            person_data['skills'] = list(skills_found)[:20]  # Limit to first 20 skills
            if person_data['skills']:
                print(f"Found {len(person_data['skills'])} skills: {', '.join(person_data['skills'][:5])}...")
            
            # Extract education information
            education_selectors = [
                '.education-section .pv-entity__summary-info',
                '.pvs-entity .t-16 .hoverable-link-text',
                '.education .pv-entity__summary-info',
                '.pvs-list .pvs-entity'
            ]
            
            education_found = []
            for selector in education_selectors:
                education_elements = soup.select(selector)
                for education_element in education_elements:
                    # Look for school names
                    school_selectors = [
                        'h3 .hoverable-link-text',
                        '.pv-entity__school-name',
                        '.t-16 .hoverable-link-text span[aria-hidden="true"]'
                    ]
                    
                    for school_selector in school_selectors:
                        school_element = education_element.select_one(school_selector)
                        if school_element:
                            school_name = school_element.get_text(strip=True)
                            
                            # Look for degree information
                            degree_selectors = [
                                '.pv-entity__degree-name .pv-entity__comma-item',
                                '.pv-entity__secondary-title',
                                '.t-14 span[aria-hidden="true"]'
                            ]
                            
                            degree_info = ''
                            for degree_selector in degree_selectors:
                                degree_element = education_element.select_one(degree_selector)
                                if degree_element:
                                    degree_info = degree_element.get_text(strip=True)
                                    break
                            
                            # Categorize as undergraduate or graduate based on degree keywords
                            education_entry = {
                                'school': school_name,
                                'degree': degree_info,
                                'type': 'unknown'
                            }
                            
                            # Determine education level
                            degree_lower = degree_info.lower()
                            if any(keyword in degree_lower for keyword in ['bachelor', 'ba', 'bs', 'undergraduate']):
                                education_entry['type'] = 'undergraduate'
                                if not person_data['undergraduate_university']:
                                    person_data['undergraduate_university'] = school_name
                                    print(f"Found undergraduate: {school_name}")
                            elif any(keyword in degree_lower for keyword in ['master', 'mba', 'ms', 'ma', 'phd', 'doctorate', 'graduate']):
                                education_entry['type'] = 'graduate'
                                person_data['graduate_schools'].append({
                                    'school': school_name,
                                    'degree': degree_info
                                })
                                print(f"Found graduate school: {school_name} ({degree_info})")
                            elif school_name:
                                # If we can't determine type but have a school name, default to undergraduate if none set
                                if not person_data['undergraduate_university']:
                                    person_data['undergraduate_university'] = school_name
                                    print(f"Found education (assumed undergraduate): {school_name}")
                            
                            education_found.append(education_entry)
                            break
            
            # Remove duplicates from graduate schools
            seen_grad_schools = set()
            unique_grad_schools = []
            for grad_school in person_data['graduate_schools']:
                school_key = (grad_school['school'], grad_school['degree'])
                if school_key not in seen_grad_schools:
                    seen_grad_schools.add(school_key)
                    unique_grad_schools.append(grad_school)
            person_data['graduate_schools'] = unique_grad_schools
            
            print(f"Extracted data: {person_data}")
            
        except Exception as e:
            print(f"Error extracting person data: {e}")
        
        return person_data
    
    def close(self):
        """Close the session"""
        if hasattr(self.session, 'close'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def scrape_linkedin_person(profile_url):
    """Convenience function to scrape a LinkedIn person profile"""
    with LinkedInPersonScraper() as scraper:
        return scraper.extract_person_data(profile_url)