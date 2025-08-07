import requests
from bs4 import BeautifulSoup
import time
import re
from database import Database
from urllib.parse import urljoin, urlparse
import random

class AmazonJobsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.db = Database()
        
    def scrape_amazon_jobs(self, search_url):
        """Scrape all Amazon jobs from the LinkedIn search results page"""
        print(f"Starting to scrape Amazon jobs from: {search_url}")
        
        try:
            # Get the search results page
            response = self.session.get(search_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all job cards on the page
            job_cards = soup.find_all('div', class_='base-card')
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all('li', class_='result-card')
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-job-id': True})
            
            print(f"Found {len(job_cards)} job cards on the page")
            
            scraped_jobs = []
            
            for i, card in enumerate(job_cards):
                try:
                    job_data = self.extract_job_data(card)
                    if job_data:
                        # Insert into database
                        if self.db.insert_job(job_data):
                            scraped_jobs.append(job_data)
                            print(f"Scraped job {i+1}: {job_data.get('job_title', 'Unknown')} at {job_data.get('company_name', 'Unknown')}")
                        else:
                            print(f"Failed to insert job {i+1}")
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 3))
                    
                except Exception as e:
                    print(f"Error scraping job {i+1}: {e}")
                    continue
            
            print(f"Successfully scraped {len(scraped_jobs)} jobs")
            return scraped_jobs
            
        except Exception as e:
            print(f"Error scraping Amazon jobs: {e}")
            return []
    
    def extract_job_data(self, card):
        """Extract job data from a job card"""
        try:
            job_data = {
                'company_name': '',
                'job_title': '',
                'job_location': '',
                'job_type': '',
                'job_description': '',
                'job_url': '',
                'posted_date': '',
                'salary_range': '',
                'experience_level': '',
                'department': '',
                'is_remote': 'Unknown'
            }
            
            # Extract job title
            title_elem = card.find('h3', class_='base-search-card__title') or \
                        card.find('a', class_='result-card__full-card-link') or \
                        card.find('h3') or \
                        card.find('a', href=True)
            
            if title_elem:
                job_data['job_title'] = title_elem.get_text(strip=True)
                # Extract job URL
                if title_elem.name == 'a' and title_elem.get('href'):
                    job_data['job_url'] = urljoin('https://www.linkedin.com', title_elem['href'])
            
            # Extract company name
            company_elem = card.find('h4', class_='base-search-card__subtitle') or \
                          card.find('span', class_='result-card__company-name') or \
                          card.find('a', class_='result-card__company-name')
            
            if company_elem:
                job_data['company_name'] = company_elem.get_text(strip=True)
            
            # Extract location
            location_elem = card.find('span', class_='job-search-card__location') or \
                           card.find('span', class_='result-card__location') or \
                           card.find('span', class_='base-search-card__metadata')
            
            if location_elem:
                job_data['job_location'] = location_elem.get_text(strip=True)
            
            # Extract posted date
            date_elem = card.find('time') or \
                       card.find('span', class_='job-search-card__listdate') or \
                       card.find('span', class_='result-card__job-meta')
            
            if date_elem:
                job_data['posted_date'] = date_elem.get_text(strip=True)
            
            # Extract salary range (if available)
            salary_elem = card.find('span', class_='job-search-card__salary-info') or \
                         card.find('span', class_='result-card__salary')
            
            if salary_elem:
                job_data['salary_range'] = salary_elem.get_text(strip=True)
            
            # Check for remote indicators
            all_text = card.get_text().lower()
            if any(remote_keyword in all_text for remote_keyword in ['remote', 'work from home', 'telecommute', 'distributed', 'anywhere']):
                job_data['is_remote'] = 'Yes'
            
            # Extract job type (Full-time, Part-time, etc.)
            type_elem = card.find('span', class_='job-search-card__job-type') or \
                       card.find('span', class_='result-card__job-type')
            
            if type_elem:
                job_data['job_type'] = type_elem.get_text(strip=True)
            
            # If we have a job URL, try to get more details
            if job_data['job_url']:
                job_data = self.enhance_job_data(job_data)
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def enhance_job_data(self, job_data):
        """Enhance job data by scraping the individual job page"""
        try:
            # Add delay before scraping individual job page
            time.sleep(random.uniform(2, 4))
            
            response = self.session.get(job_data['job_url'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract job description
            desc_elem = soup.find('div', class_='show-more-less-html') or \
                       soup.find('div', class_='description__text') or \
                       soup.find('div', class_='job-description')
            
            if desc_elem:
                job_data['job_description'] = desc_elem.get_text(strip=True)[:1000]  # Limit to 1000 chars
            
            # Extract salary information from job page
            salary_selectors = [
                'span[class*="salary"]',
                'div[class*="salary"]',
                'span[class*="compensation"]',
                'div[class*="compensation"]'
            ]
            
            for selector in salary_selectors:
                salary_elem = soup.select_one(selector)
                if salary_elem:
                    salary_text = salary_elem.get_text(strip=True)
                    if salary_text and not job_data['salary_range']:
                        job_data['salary_range'] = salary_text
                    break
            
            # Extract experience level
            exp_selectors = [
                'span[class*="experience"]',
                'div[class*="experience"]',
                'span[class*="level"]',
                'div[class*="level"]'
            ]
            
            for selector in exp_selectors:
                exp_elem = soup.select_one(selector)
                if exp_elem:
                    exp_text = exp_elem.get_text(strip=True)
                    if exp_text:
                        job_data['experience_level'] = exp_text
                    break
            
            # Extract department
            dept_selectors = [
                'span[class*="department"]',
                'div[class*="department"]',
                'span[class*="team"]',
                'div[class*="team"]'
            ]
            
            for selector in dept_selectors:
                dept_elem = soup.select_one(selector)
                if dept_elem:
                    dept_text = dept_elem.get_text(strip=True)
                    if dept_text:
                        job_data['department'] = dept_text
                    break
            
            # Check for remote indicators in job description
            if job_data['job_description']:
                desc_lower = job_data['job_description'].lower()
                if any(remote_keyword in desc_lower for remote_keyword in ['remote', 'work from home', 'telecommute', 'distributed', 'anywhere']):
                    job_data['is_remote'] = 'Yes'
                elif any(office_keyword in desc_lower for office_keyword in ['on-site', 'office', 'in-person']):
                    job_data['is_remote'] = 'No'
            
        except Exception as e:
            print(f"Error enhancing job data: {e}")
        
        return job_data

def main():
    """Main function to run the Amazon jobs scraper"""
    scraper = AmazonJobsScraper()
    
    # Clear existing jobs
    scraper.db.clear_all_jobs()
    
    # Amazon jobs search URL
    search_url = "https://www.linkedin.com/jobs/search-results/?keywords=amazon&origin=BLENDED_SEARCH_RESULT_NAVIGATION_SEE_ALL&originToLandingJobPostings=4213179388%2C4225750824%2C4213180373"
    
    # Scrape jobs
    scraped_jobs = scraper.scrape_amazon_jobs(search_url)
    
    print(f"\nScraping completed!")
    print(f"Total jobs scraped: {len(scraped_jobs)}")
    print(f"Total jobs in database: {scraper.db.get_jobs_count()}")

if __name__ == "__main__":
    main()
