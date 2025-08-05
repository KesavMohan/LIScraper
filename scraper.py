import requests
try:
    from bs4 import BeautifulSoup
except ImportError:
    try:
        from beautifulsoup4 import BeautifulSoup
    except ImportError:
        # Fallback - install and import
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
        from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import random
import json
from requests_html import HTMLSession

class LinkedInJobScraper:
    def __init__(self):
        self.session = HTMLSession()
        self.setup_session()
    
    def setup_session(self):
        """Setup requests session with appropriate headers"""
        ua = UserAgent()
        self.session.headers.update({
            'User-Agent': ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_company_name_from_url(self, url):
        """Extract company name from LinkedIn company URL"""
        try:
            # Pattern to match LinkedIn company URLs
            pattern = r'linkedin\.com/company/([^/]+)'
            match = re.search(pattern, url)
            if match:
                return match.group(1).replace('-', ' ').title()
            return "Unknown Company"
        except:
            return "Unknown Company"
    
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
    
    def parse_job_from_element(self, job_element, company_name, base_url):
        """Parse job details from a BeautifulSoup element"""
        job_data = {
            'company_name': company_name,
            'job_title': '',
            'job_location': '',
            'job_type': '',
            'job_description': '',
            'job_url': '',
            'posted_date': '',
            'salary_range': '',
            'experience_level': '',
            'department': ''
        }
        
        try:
            # Job Title and URL
            title_selectors = [
                'h3 a',
                '.job-card-list__title a',
                '[data-job-id] h3 a',
                '.base-search-card__title a',
                '.job-card-container__link',
                'a[data-tracking-control-name="public_jobs_jserp-result_search-card"]'
            ]
            
            title_element = None
            for selector in title_selectors:
                title_element = job_element.select_one(selector)
                if title_element:
                    break
            
            if title_element:
                job_data['job_title'] = title_element.get_text(strip=True)
                href = title_element.get('href', '')
                if href:
                    job_data['job_url'] = urljoin(base_url, href)
        except Exception as e:
            print(f"Error parsing job title: {e}")
        
        try:
            # Job Location
            location_selectors = [
                '.job-card-container__metadata-item',
                '.job-card-list__metadata',
                '.base-search-card__metadata',
                '.job-search-card__location'
            ]
            
            for selector in location_selectors:
                location_element = job_element.select_one(selector)
                if location_element:
                    job_data['job_location'] = location_element.get_text(strip=True)
                    break
        except Exception as e:
            print(f"Error parsing job location: {e}")
        
        try:
            # Posted Date
            date_selectors = [
                'time',
                '.job-card-container__listed-time',
                '.job-search-card__listdate'
            ]
            
            for selector in date_selectors:
                date_element = job_element.select_one(selector)
                if date_element:
                    job_data['posted_date'] = date_element.get('datetime', '') or date_element.get_text(strip=True)
                    break
        except Exception as e:
            print(f"Error parsing posted date: {e}")
        
        try:
            # Job Type/Additional Info
            metadata_elements = job_element.select('.job-card-container__metadata-wrapper span, .base-search-card__metadata span')
            job_types = []
            for elem in metadata_elements:
                text = elem.get_text(strip=True)
                if text and text != job_data['job_location']:
                    job_types.append(text)
            
            if job_types:
                job_data['job_type'] = ' • '.join(job_types)
        except Exception as e:
            print(f"Error parsing job type: {e}")
        
        return job_data
    
    def scrape_linkedin_public_jobs(self, company_url):
        """Scrape jobs from LinkedIn public jobs page (no authentication required)"""
        jobs = []
        
        try:
            # Extract company name
            company_name = self.extract_company_name_from_url(company_url)
            
            # Build the public jobs search URL
            company_id = None
            if '/company/' in company_url:
                company_slug = company_url.split('/company/')[-1].split('/')[0]
                
                # Try to get company page first to extract company ID
                company_page_url = f"https://www.linkedin.com/company/{company_slug}"
                content = self.get_page_content(company_page_url)
                
                if content:
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Look for company ID in various places
                    scripts = soup.find_all('script', type='application/ld+json')
                    for script in scripts:
                        try:
                            data = json.loads(script.string)
                            if isinstance(data, dict) and 'url' in data:
                                # Extract company ID from structured data
                                pass
                        except:
                            continue
                
                # Use public jobs search with company name
                search_url = f"https://www.linkedin.com/jobs/search?keywords=&location=&company={company_slug}&trk=public_jobs_jobs-search-bar_search-submit"
                
            else:
                search_url = company_url
            
            print(f"Searching jobs at: {search_url}")
            content = self.get_page_content(search_url)
            
            if not content:
                print("Failed to get page content")
                return jobs
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find job cards using various selectors
            job_selectors = [
                '.job-search-card',
                '.base-card',
                '.base-search-card',
                '[data-job-id]',
                '.job-card-container'
            ]
            
            job_elements = []
            for selector in job_selectors:
                elements = soup.select(selector)
                if elements:
                    job_elements = elements
                    print(f"Found {len(job_elements)} job elements using selector: {selector}")
                    break
            
            if not job_elements:
                print("No job elements found. Trying alternative approach...")
                
                # Alternative: look for any links that might be job postings
                job_links = soup.select('a[href*="/jobs/view/"]')
                if job_links:
                    print(f"Found {len(job_links)} job links as fallback")
                    # Create minimal job data from links
                    for link in job_links[:20]:  # Limit to first 20
                        job_data = {
                            'company_name': company_name,
                            'job_title': link.get_text(strip=True),
                            'job_url': urljoin(search_url, link.get('href', '')),
                            'job_location': 'Not specified',
                            'job_type': 'Not specified',
                            'job_description': '',
                            'posted_date': '',
                            'salary_range': '',
                            'experience_level': '',
                            'department': ''
                        }
                        if job_data['job_title']:
                            jobs.append(job_data)
                
                return jobs
            
            # Parse job details
            print(f"Parsing {len(job_elements)} job postings...")
            for i, job_element in enumerate(job_elements):
                try:
                    job_data = self.parse_job_from_element(job_element, company_name, search_url)
                    
                    if job_data['job_title']:
                        jobs.append(job_data)
                        print(f"Scraped job {i+1}: {job_data['job_title']}")
                    
                    # Add delay to be respectful
                    time.sleep(random.uniform(0.5, 1.0))
                    
                except Exception as e:
                    print(f"Error parsing job {i+1}: {e}")
                    continue
            
            print(f"Successfully scraped {len(jobs)} jobs from {company_name}")
            
        except Exception as e:
            print(f"Error scraping company jobs: {e}")
        
        return jobs
    
    def scrape_company_jobs(self, company_url):
        """Main method to scrape jobs from a LinkedIn company page"""
        return self.scrape_linkedin_public_jobs(company_url)
    
    def close(self):
        """Close the session"""
        if hasattr(self.session, 'close'):
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def scrape_linkedin_jobs(company_url):
    """Convenience function to scrape jobs from a LinkedIn company page"""
    with LinkedInJobScraper() as scraper:
        return scraper.scrape_company_jobs(company_url)