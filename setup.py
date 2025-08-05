#!/usr/bin/env python3
"""
Setup script for LinkedIn Job Scraper
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    print("🚀 Setting up LinkedIn Job Scraper...")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    success, output = run_command("pip install -r requirements.txt")
    
    if success:
        print("✅ Dependencies installed successfully")
    else:
        print(f"❌ Failed to install dependencies: {output}")
        sys.exit(1)
    
    # Initialize database
    print("\n🗄️ Initializing database...")
    try:
        from database import JobDatabase
        db = JobDatabase()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo start the application:")
    print("  python app.py")
    print("\nThen open your browser and go to:")
    print("  http://localhost:5000")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()