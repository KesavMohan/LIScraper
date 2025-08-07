import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='jobs.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the jobs table"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                job_location TEXT,
                job_type TEXT,
                job_description TEXT,
                job_url TEXT UNIQUE,
                posted_date TEXT,
                scraped_date TEXT DEFAULT CURRENT_TIMESTAMP,
                salary_range TEXT,
                experience_level TEXT,
                department TEXT,
                is_remote TEXT DEFAULT 'Unknown'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def clear_all_jobs(self):
        """Clear all jobs from the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM jobs')
        conn.commit()
        conn.close()
        print("All jobs cleared from database")
    
    def insert_job(self, job_data):
        """Insert a job into the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (company_name, job_title, job_location, job_type, job_description, 
                 job_url, posted_date, salary_range, experience_level, department, is_remote)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job_data.get('company_name', ''),
                job_data.get('job_title', ''),
                job_data.get('job_location', ''),
                job_data.get('job_type', ''),
                job_data.get('job_description', ''),
                job_data.get('job_url', ''),
                job_data.get('posted_date', ''),
                job_data.get('salary_range', ''),
                job_data.get('experience_level', ''),
                job_data.get('department', ''),
                job_data.get('is_remote', 'Unknown')
            ))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            print(f"Error inserting job: {e}")
            return False
        finally:
            conn.close()
    
    def get_all_jobs(self):
        """Get all jobs from the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs ORDER BY scraped_date DESC')
        jobs = cursor.fetchall()
        
        conn.close()
        return jobs
    
    def get_jobs_count(self):
        """Get the total number of jobs in the database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM jobs')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
