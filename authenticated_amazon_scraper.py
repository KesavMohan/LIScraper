from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
from database import Database
from urllib.parse import urljoin
import os

class AuthenticatedAmazonScraper:
    def __init__(self):
        self.db = Database()
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            # Try to use webdriver-manager first
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"webdriver-manager failed: {e}")
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Chrome driver setup successful")
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Please ensure Chrome is installed and ChromeDriver is available")
            raise
    
    def login_to_linkedin(self):
        """Manual login to LinkedIn - user will need to log in manually"""
        if not self.driver:
            print("Chrome driver not initialized")
            return False
            
        print("Opening LinkedIn login page...")
        self.driver.get("https://www.linkedin.com/login")
        
        print("Please log in to LinkedIn manually in the browser window.")
        print("The browser will wait for you to complete the login process.")
        
        # Wait for user to log in by checking for authenticated page
        try:
            # Wait for either the feed page or profile page to load (indicating successful login)
            WebDriverWait(self.driver, 300).until(
                EC.any_of(
                    EC.url_contains("/feed/"),
                    EC.url_contains("/in/me/"),
                    EC.url_contains("/mynetwork/"),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "nav")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-control-name='nav.settings']"))
                )
            )
            print("Login successful!")
            return True
        except TimeoutException:
            print("Login timeout. Please try again.")
            return False
        except Exception as e:
            print(f"Error during login verification: {e}")
            return False
    
    def scrape_amazon_jobs(self, search_url):
        """Scrape Amazon jobs from the authenticated LinkedIn session"""
        print(f"Navigating to Amazon jobs search: {search_url}")
        
        try:
            self.driver.get(search_url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            
            # Add some delay for dynamic content to load
            time.sleep(5)
            
            # Scroll to load more jobs
            self.scroll_to_load_jobs()
            
            # Get the page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find job cards
            job_cards = self.find_job_cards(soup)
            
            print(f"Found {len(job_cards)} job cards")
            
            scraped_jobs = []
            
            for i, card in enumerate(job_cards):
                try:
                    job_data = self.extract_job_data_from_card(card)
                    if job_data:
                        # Insert into database
                        if self.db.insert_job(job_data):
                            scraped_jobs.append(job_data)
                            print(f"Scraped job {i+1}: {job_data.get('job_title', 'Unknown')} at {job_data.get('company_name', 'Unknown')}")
                        else:
                            print(f"Failed to insert job {i+1}")
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    print(f"Error scraping job {i+1}: {e}")
                    continue
            
            print(f"Successfully scraped {len(scraped_jobs)} jobs")
            return scraped_jobs
            
        except Exception as e:
            print(f"Error scraping Amazon jobs: {e}")
            return []
    
    def scroll_to_load_jobs(self):
        """Scroll down to load more job cards"""
        print("Scrolling to load more jobs...")
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(3):  # Scroll 3 times
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(3)
            
            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            last_height = new_height
    
    def find_job_cards(self, soup):
        """Find job cards using various selectors"""
        selectors = [
            'div[class*="base-card"]',
            'li[class*="result-card"]',
            'div[data-job-id]',
            'div[class*="job-card"]',
            'div[class*="search-result"]',
            'li[class*="job-result"]',
            'div[class*="job-search-card"]',
            'div[class*="ember-view"]'
        ]
        
        job_cards = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                print(f"Found {len(cards)} cards with selector: {selector}")
                job_cards = cards
                break
        
        return job_cards
    
    def extract_job_data_from_card(self, card):
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
            
            # Extract job title and URL
            title_selectors = [
                'h3[class*="base-search-card__title"]',
                'a[class*="result-card__full-card-link"]',
                'h3',
                'a[href*="/jobs/"]'
            ]
            
            for selector in title_selectors:
                title_elem = card.select_one(selector)
                if title_elem:
                    job_data['job_title'] = title_elem.get_text(strip=True)
                    if title_elem.name == 'a' and title_elem.get('href'):
                        job_data['job_url'] = urljoin('https://www.linkedin.com', title_elem['href'])
                    break
            
            # Extract company name
            company_selectors = [
                'h4[class*="base-search-card__subtitle"]',
                'span[class*="result-card__company-name"]',
                'a[class*="result-card__company-name"]'
            ]
            
            for selector in company_selectors:
                company_elem = card.select_one(selector)
                if company_elem:
                    job_data['company_name'] = company_elem.get_text(strip=True)
                    break
            
            # Extract location
            location_selectors = [
                'span[class*="job-search-card__location"]',
                'span[class*="result-card__location"]',
                'span[class*="base-search-card__metadata"]'
            ]
            
            for selector in location_selectors:
                location_elem = card.select_one(selector)
                if location_elem:
                    job_data['job_location'] = location_elem.get_text(strip=True)
                    break
            
            # Extract posted date
            date_selectors = [
                'time',
                'span[class*="job-search-card__listdate"]',
                'span[class*="result-card__job-meta"]'
            ]
            
            for selector in date_selectors:
                date_elem = card.select_one(selector)
                if date_elem:
                    job_data['posted_date'] = date_elem.get_text(strip=True)
                    break
            
            # Extract salary range
            salary_selectors = [
                'span[class*="job-search-card__salary-info"]',
                'span[class*="result-card__salary"]'
            ]
            
            for selector in salary_selectors:
                salary_elem = card.select_one(selector)
                if salary_elem:
                    job_data['salary_range'] = salary_elem.get_text(strip=True)
                    break
            
            # Check for remote indicators
            all_text = card.get_text().lower()
            if any(remote_keyword in all_text for remote_keyword in ['remote', 'work from home', 'telecommute', 'distributed', 'anywhere']):
                job_data['is_remote'] = 'Yes'
            
            # Extract job type
            type_selectors = [
                'span[class*="job-search-card__job-type"]',
                'span[class*="result-card__job-type"]'
            ]
            
            for selector in type_selectors:
                type_elem = card.select_one(selector)
                if type_elem:
                    job_data['job_type'] = type_elem.get_text(strip=True)
                    break
            
            # If we have a job URL, try to get more details
            if job_data['job_url']:
                job_data = self.enhance_job_data(job_data)
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def enhance_job_data(self, job_data):
        """Enhance job data by visiting the individual job page"""
        try:
            # Navigate to job page
            self.driver.get(job_data['job_url'])
            time.sleep(3)
            
            # Get page source and parse
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract job description
            desc_selectors = [
                'div[class*="show-more-less-html"]',
                'div[class*="description__text"]',
                'div[class*="job-description"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    job_data['job_description'] = desc_elem.get_text(strip=True)[:1000]
                    break
            
            # Extract salary information
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
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to run the authenticated Amazon jobs scraper"""
    scraper = AuthenticatedAmazonScraper()
    
    try:
        # Login to LinkedIn
        if not scraper.login_to_linkedin():
            print("Failed to login to LinkedIn")
            return
        
        # Clear existing jobs
        scraper.db.clear_all_jobs()
        
        # Amazon jobs search URL
        search_url = "https://www.linkedin.com/jobs/search-results/?keywords=amazon&origin=BLENDED_SEARCH_RESULT_NAVIGATION_SEE_ALL&originToLandingJobPostings=4213179388%2C4225750824%2C4213180373"
        
        # Scrape jobs
        scraped_jobs = scraper.scrape_amazon_jobs(search_url)
        
        print(f"\nScraping completed!")
        print(f"Total jobs scraped: {len(scraped_jobs)}")
        print(f"Total jobs in database: {scraper.db.get_jobs_count()}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
