#!/usr/bin/env python3
"""
Quick test script for when you're already logged into LinkedIn
Bypasses the slow feed loading issue
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time

def test_logged_in_browser():
    """Test scraping when you're already logged in"""
    
    print("🔧 Quick LinkedIn Test (Already Logged In)")
    print("=" * 50)
    print("This will:")
    print("1. Open a new Chrome window")
    print("2. Try to access LinkedIn directly")
    print("3. Test if we can scrape a profile")
    
    response = input("\nAre you currently logged into LinkedIn in another tab? (y/n): ").lower()
    if response != 'y':
        print("Please log into LinkedIn first, then run this script")
        return
    
    try:
        # Setup Chrome with same settings
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
        chrome_options.add_experimental_option("detach", True)
        
        # Use same user data directory to share login session
        chrome_options.add_argument("--user-data-dir=/tmp/linkedin-chrome-profile")
        
        service = Service('/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome opened with shared session")
        
        # Test with Karen's profile directly
        test_url = "https://www.linkedin.com/in/karen-travers-16a0395/"
        print(f"🔍 Testing with: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)
        
        # Check if we can see the profile content
        try:
            # Look for profile elements
            name_elem = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            if name_elem:
                print(f"✅ Profile loaded successfully!")
                print(f"Page title: {driver.title}")
                
                # Check if we're getting full profile access
                if "Sign in" in driver.title or "login" in driver.current_url.lower():
                    print("❌ Not logged in - redirected to login page")
                    print("Please log into LinkedIn manually first")
                else:
                    print("✅ Logged in successfully - can access profiles!")
                    print("✅ Ready to run the main scraper!")
            
        except Exception as e:
            print(f"⚠️ Profile loading issue: {e}")
            print("Current URL:", driver.current_url)
            print("Page title:", driver.title)
        
        input("\nPress ENTER to close browser...")
        driver.quit()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_logged_in_browser()