import requests
from bs4 import BeautifulSoup
import json

def debug_linkedin_page():
    """Debug what's on the LinkedIn jobs search page"""
    url = "https://www.linkedin.com/jobs/search-results/?keywords=amazon&origin=BLENDED_SEARCH_RESULT_NAVIGATION_SEE_ALL&originToLandingJobPostings=4213179388%2C4225750824%2C4213180373"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Page title: {soup.title.string if soup.title else 'No title'}")
        print(f"Response status: {response.status_code}")
        print(f"Content length: {len(response.content)}")
        
        # Check if we're redirected to login
        if 'login' in response.url.lower() or 'signin' in response.url.lower():
            print("REDIRECTED TO LOGIN PAGE")
            return
        
        # Look for common job-related elements
        print("\n=== Checking for job-related elements ===")
        
        # Check for job cards with different selectors
        selectors_to_try = [
            'div[class*="base-card"]',
            'li[class*="result-card"]',
            'div[data-job-id]',
            'div[class*="job-card"]',
            'div[class*="search-result"]',
            'li[class*="job-result"]',
            'div[class*="job-search-card"]'
        ]
        
        for selector in selectors_to_try:
            elements = soup.select(selector)
            print(f"Selector '{selector}': {len(elements)} elements found")
            if elements:
                print(f"  First element classes: {elements[0].get('class', [])}")
                print(f"  First element text preview: {elements[0].get_text()[:100]}...")
        
        # Check for any divs with job-related classes
        all_divs = soup.find_all('div')
        job_related_divs = []
        for div in all_divs:
            classes = div.get('class', [])
            if any('job' in str(cls).lower() or 'card' in str(cls).lower() or 'search' in str(cls).lower() for cls in classes):
                job_related_divs.append(div)
        
        print(f"\nFound {len(job_related_divs)} divs with job-related classes")
        
        # Check for any content that might indicate we need authentication
        page_text = soup.get_text().lower()
        auth_indicators = ['sign in', 'log in', 'login', 'signin', 'authentication', 'please sign in']
        for indicator in auth_indicators:
            if indicator in page_text:
                print(f"Found authentication indicator: '{indicator}'")
        
        # Save the HTML for inspection
        with open('linkedin_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        print("\nSaved HTML to linkedin_debug.html for inspection")
        
        # Look for any JSON data in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('window' in script.string or 'INITIAL_STATE' in script.string):
                print(f"\nFound script with potential data: {script.string[:200]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_linkedin_page()
