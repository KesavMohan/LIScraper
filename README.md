# LinkedIn Job Scraper

A web service that scrapes job postings from LinkedIn company pages and stores them in a database with a web interface for viewing.

## Features

- Scrape all job postings from a LinkedIn company page
- Store job data in SQLite database
- Web interface to view jobs in a table format
- Export functionality for job data

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python app.py
```

3. Open your browser and go to `http://localhost:5009`

## Usage

1. Enter a LinkedIn company page URL (e.g., `https://www.linkedin.com/company/example-company/jobs/`)
1. Click "Scrape Jobs" to start the scraping process
1. View the scraped jobs in the table below
1. Export data as needed

## Important Notes

- This tool is for educational purposes only
- Respect LinkedIn's terms of service and rate limits
- Use responsibly and ethically
- Consider using LinkedIn's official API for production use