#!/usr/bin/env python3
"""
Scrape names and profile links from LinkedIn connections page
URL: https://www.linkedin.com/mynetwork/invite-connect/connections/
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import time
import json

def scrape_connections_page():
    """Scrape the first 10 people from LinkedIn connections page"""
    
    print("🔗 LinkedIn Connections Page Scraper")
    print("=" * 50)
    print("Target: https://www.linkedin.com/mynetwork/invite-connect/connections/")
    print("Goal: Extract first 10 names and profile links")
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36")
    chrome_options.add_experimental_option("detach", True)
    
    driver = None
    try:
        # Initialize Chrome
        service = Service('/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome browser opened")
        
        # Navigate to LinkedIn login first
        driver.get("https://www.linkedin.com/login")
        
        print("\n🔐 PLEASE LOG IN:")
        print("1. Log in to LinkedIn in the browser window")
        print("2. Navigate to: https://www.linkedin.com/mynetwork/invite-connect/connections/")
        print("3. Make sure the connections page is loaded")
        print("4. Come back here and press ENTER")
        
        input("\n⏳ Press ENTER when you're on the connections page...")
        
        # Get current URL to verify
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        if "mynetwork" not in current_url:
            print("⚠️ Navigating to connections page...")
            driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
            time.sleep(3)
        
        print("\n🔍 Scraping connections...")
        
        # Wait for page to load
        time.sleep(5)
        
        # Look for different possible selectors for connection cards
        connection_selectors = [
            # Modern LinkedIn selectors
            '[data-test-component="connections-member-item"]',
            '.connections-member-item',
            '.mn-connection-card',
            '.member-item',
            '.connection-item',
            # Fallback selectors
            '[data-testid*="connection"]',
            '[class*="connection"]',
            '[class*="member-item"]',
            # Profile link selectors
            'a[href*="/in/"]',
        ]
        
        connections_found = []
        
        for selector in connection_selectors:
            try:
                print(f"🔍 Trying selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    
                    for i, element in enumerate(elements[:10]):  # Limit to first 10
                        try:
                            # Try to find name and profile link within this element
                            name = ""
                            profile_link = ""
                            
                            # Look for name in various places
                            name_selectors = [
                                '.member-item__name',
                                '.mn-connection-card__name',
                                '.connections-member-item__name',
                                'h3',
                                'h2',
                                '[data-test="member-name"]',
                                '.member-name',
                                'span[aria-hidden="true"]'
                            ]
                            
                            for name_sel in name_selectors:
                                try:
                                    name_elem = element.find_element(By.CSS_SELECTOR, name_sel)
                                    if name_elem and name_elem.text.strip():
                                        name = name_elem.text.strip()
                                        break
                                except:
                                    continue
                            
                            # Look for profile link
                            link_selectors = [
                                'a[href*="/in/"]',
                                '.member-item__link',
                                '.mn-connection-card__link',
                                'a'
                            ]
                            
                            for link_sel in link_selectors:
                                try:
                                    link_elem = element.find_element(By.CSS_SELECTOR, link_sel)
                                    href = link_elem.get_attribute('href')
                                    if href and '/in/' in href:
                                        profile_link = href
                                        break
                                except:
                                    continue
                            
                            # If we found both name and link, add to results
                            if name and profile_link:
                                connection_data = {
                                    'name': name,
                                    'profile_link': profile_link,
                                    'position': len(connections_found) + 1
                                }
                                connections_found.append(connection_data)
                                print(f"  {len(connections_found)}. {name} -> {profile_link}")
                            
                            # Stop if we have 10
                            if len(connections_found) >= 10:
                                break
                                
                        except Exception as e:
                            print(f"    ⚠️ Error processing element {i}: {e}")
                            continue
                    
                    # If we found connections with this selector, we're done
                    if connections_found:
                        break
                        
            except Exception as e:
                print(f"    ❌ Selector {selector} failed: {e}")
                continue
        
        # Fallback: Look for any profile links on the page
        if not connections_found:
            print("\n🔄 Fallback: Looking for any LinkedIn profile links...")
            try:
                all_links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/in/"]')
                print(f"Found {len(all_links)} total profile links")
                
                for i, link in enumerate(all_links[:10]):
                    try:
                        href = link.get_attribute('href')
                        # Get text from the link or parent element
                        text = link.text.strip()
                        if not text:
                            # Try parent element
                            parent = link.find_element(By.XPATH, '..')
                            text = parent.text.strip().split('\n')[0]  # First line only
                        
                        if href and text and len(text) < 100:  # Reasonable name length
                            connection_data = {
                                'name': text,
                                'profile_link': href,
                                'position': len(connections_found) + 1
                            }
                            connections_found.append(connection_data)
                            print(f"  {len(connections_found)}. {text} -> {href}")
                            
                        if len(connections_found) >= 10:
                            break
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"❌ Fallback failed: {e}")
        
        # Results
        print(f"\n📊 SCRAPING RESULTS")
        print("=" * 30)
        print(f"✅ Found {len(connections_found)} connections")
        
        if connections_found:
            print(f"\n📋 EXTRACTED DATA:")
            for conn in connections_found:
                print(f"{conn['position']}. {conn['name']}")
                print(f"   Link: {conn['profile_link']}")
                print()
            
            # Save to file
            with open('connections_data.json', 'w') as f:
                json.dump(connections_found, f, indent=2)
            print(f"💾 Data saved to: connections_data.json")
            
            # Create a simple list for the main scraper
            profile_urls = [conn['profile_link'] for conn in connections_found]
            
            print(f"\n🎯 READY FOR MAIN SCRAPER:")
            print("Copy these URLs to your main scraper:")
            print("profile_urls = [")
            for url in profile_urls:
                print(f'    "{url}",')
            print("]")
            
        else:
            print("❌ No connections found")
            print("💡 Try:")
            print("1. Make sure you're on the connections page")
            print("2. Scroll down to load more connections")
            print("3. Check if LinkedIn layout has changed")
        
        input("\nPress ENTER to close browser...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("🔒 Browser closed")

if __name__ == "__main__":
    scrape_connections_page()