#!/usr/bin/env python3
"""
Simple runner script for LinkedIn Job Scraper
"""

import os
import sys

def main():
    print("🚀 Starting LinkedIn Job Scraper...")
    print("=" * 50)
    
    # Check if running from correct directory
    if not os.path.exists('app.py'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Import and run the Flask app
    try:
        from app import app
        print("✅ Application loaded successfully")
        print("\n🌐 Starting web server...")
        print("📍 Open your browser and go to: http://localhost:5009")
        print("🛑 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=5009)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()