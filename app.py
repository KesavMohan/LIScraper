from flask import Flask, render_template, request, jsonify, send_file
from database import JobDatabase
from scraper import scrape_linkedin_jobs
import threading
import io
import csv
from datetime import datetime
import os

app = Flask(__name__)
db = JobDatabase()

# Global variable to track scraping status
scraping_status = {
    'is_scraping': False,
    'progress': '',
    'jobs_found': 0,
    'error': None
}

@app.route('/')
def index():
    """Main page with job scraping interface"""
    jobs_df = db.get_all_jobs()
    total_jobs = db.get_job_count()
    
    return render_template('index.html', 
                         jobs=jobs_df.to_dict('records') if not jobs_df.empty else [],
                         total_jobs=total_jobs)

@app.route('/scrape', methods=['POST'])
def scrape_jobs():
    """Start scraping jobs from LinkedIn company page"""
    global scraping_status
    
    if scraping_status['is_scraping']:
        return jsonify({'error': 'Scraping already in progress'}), 400
    
    company_url = request.json.get('company_url', '').strip()
    
    if not company_url:
        return jsonify({'error': 'Company URL is required'}), 400
    
    if 'linkedin.com/company' not in company_url:
        return jsonify({'error': 'Please provide a valid LinkedIn company URL'}), 400
    
    # Start scraping in background thread
    thread = threading.Thread(target=scrape_jobs_background, args=(company_url,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Scraping started', 'status': 'started'})

def scrape_jobs_background(company_url):
    """Background function to scrape jobs"""
    global scraping_status
    
    scraping_status = {
        'is_scraping': True,
        'progress': 'Starting scraper...',
        'jobs_found': 0,
        'error': None
    }
    
    try:
        scraping_status['progress'] = 'Initializing browser...'
        
        # Scrape jobs
        jobs = scrape_linkedin_jobs(company_url)
        
        if jobs:
            scraping_status['progress'] = f'Saving {len(jobs)} jobs to database...'
            
            # Save jobs to database
            success_count = db.insert_jobs_batch(jobs)
            
            scraping_status = {
                'is_scraping': False,
                'progress': f'Successfully scraped and saved {success_count} jobs!',
                'jobs_found': success_count,
                'error': None
            }
        else:
            scraping_status = {
                'is_scraping': False,
                'progress': 'No jobs found or unable to scrape jobs',
                'jobs_found': 0,
                'error': 'No jobs found. Please check the URL and try again.'
            }
    
    except Exception as e:
        scraping_status = {
            'is_scraping': False,
            'progress': 'Scraping failed',
            'jobs_found': 0,
            'error': f'Error: {str(e)}'
        }

@app.route('/status')
def get_status():
    """Get current scraping status"""
    return jsonify(scraping_status)

@app.route('/jobs')
def get_jobs():
    """Get all jobs as JSON"""
    jobs_df = db.get_all_jobs()
    return jsonify(jobs_df.to_dict('records') if not jobs_df.empty else [])

@app.route('/export')
def export_jobs():
    """Export jobs to CSV"""
    jobs_df = db.get_all_jobs()
    
    if jobs_df.empty:
        return jsonify({'error': 'No jobs to export'}), 400
    
    # Create CSV in memory
    output = io.StringIO()
    jobs_df.to_csv(output, index=False)
    output.seek(0)
    
    # Convert to bytes
    csv_data = io.BytesIO()
    csv_data.write(output.getvalue().encode('utf-8'))
    csv_data.seek(0)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'linkedin_jobs_{timestamp}.csv'
    
    return send_file(
        csv_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@app.route('/clear')
def clear_jobs():
    """Clear all jobs from database"""
    success = db.delete_all_jobs()
    if success:
        return jsonify({'message': 'All jobs cleared successfully'})
    else:
        return jsonify({'error': 'Failed to clear jobs'}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5009)