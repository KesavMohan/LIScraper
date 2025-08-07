#!/usr/bin/env python3
"""
Setup script for the Authenticated LinkedIn Scraper
This script helps install ChromeDriver and dependencies
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error during {description}: {e}")
        return False

def install_python_requirements():
    """Install Python requirements"""
    print("\n🐍 Installing Python requirements...")
    return run_command(f"{sys.executable} -m pip install -r requirements_auth.txt", 
                      "Installing Python packages")

def install_chromedriver_mac():
    """Install ChromeDriver on macOS using Homebrew"""
    print("\n🍺 Installing ChromeDriver via Homebrew...")
    
    # Check if Homebrew is installed
    homebrew_check = subprocess.run("which brew", shell=True, capture_output=True)
    if homebrew_check.returncode != 0:
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("Visit: https://brew.sh")
        return False
    
    # Install ChromeDriver
    if run_command("brew install chromedriver", "Installing ChromeDriver"):
        # Remove quarantine (macOS security)
        run_command("xattr -d com.apple.quarantine $(which chromedriver)", 
                   "Removing quarantine from ChromeDriver")
        return True
    return False

def check_chrome_installation():
    """Check if Google Chrome is installed"""
    print("\n🌐 Checking Google Chrome installation...")
    
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Found Chrome at: {path}")
            return True
    
    print("❌ Google Chrome not found!")
    print("Please install Google Chrome from: https://www.google.com/chrome/")
    return False

def test_selenium_setup():
    """Test if Selenium can start Chrome"""
    print("\n🧪 Testing Selenium setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Setup headless Chrome for testing
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Selenium test successful! Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        print("\n💡 Common solutions:")
        print("1. Make sure ChromeDriver is in your PATH")
        print("2. Update Chrome to the latest version")
        print("3. Try: brew reinstall chromedriver")
        return False

def main():
    """Main setup function"""
    print("🚀 LinkedIn Authenticated Scraper Setup")
    print("=" * 50)
    
    system = platform.system()
    print(f"🖥️ Detected OS: {system}")
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Check Chrome
    if check_chrome_installation():
        success_count += 1
    
    # Step 2: Install Python requirements
    if install_python_requirements():
        success_count += 1
    
    # Step 3: Install ChromeDriver
    if system == "Darwin":  # macOS
        if install_chromedriver_mac():
            success_count += 1
    else:
        print(f"\n⚠️ Please install ChromeDriver manually for {system}")
        print("Visit: https://chromedriver.chromium.org/")
        success_count += 1  # Assume user will install manually
    
    # Step 4: Test setup
    if test_selenium_setup():
        success_count += 1
    
    # Summary
    print(f"\n📊 Setup Summary: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("✅ Setup completed successfully!")
        print("\n🎯 Next steps:")
        print("1. Run: python authenticated_scraper.py")
        print("2. Log in to LinkedIn manually when prompted")
        print("3. Let the scraper extract profile data")
        print("\n⚠️ Remember to respect LinkedIn's terms of service!")
    else:
        print("❌ Setup incomplete. Please resolve the issues above.")
    
    return success_count == total_steps

if __name__ == "__main__":
    main()