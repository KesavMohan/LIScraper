import sqlite3
import pandas as pd
from datetime import datetime
import os

class JobDatabase:
    def __init__(self, db_path="jobs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the jobs table"""
        conn = sqlite3.connect(self.db_path)
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
                department TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_job(self, job_data):
        """Insert a single job into the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO jobs 
                (company_name, job_title, job_location, job_type, job_description, 
                 job_url, posted_date, salary_range, experience_level, department)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                job_data.get('department', '')
            ))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
        finally:
            conn.close()
    
    def insert_jobs_batch(self, jobs_list):
        """Insert multiple jobs into the database"""
        success_count = 0
        for job in jobs_list:
            if self.insert_job(job):
                success_count += 1
        return success_count
    
    def get_all_jobs(self):
        """Get all jobs from the database"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query("SELECT * FROM jobs ORDER BY scraped_date DESC", conn)
            return df
        except Exception as e:
            print(f"Error fetching jobs: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def get_jobs_by_company(self, company_name):
        """Get jobs for a specific company"""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(
                "SELECT * FROM jobs WHERE company_name LIKE ? ORDER BY scraped_date DESC", 
                conn, 
                params=[f"%{company_name}%"]
            )
            return df
        except Exception as e:
            print(f"Error fetching jobs for company: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def delete_all_jobs(self):
        """Delete all jobs from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM jobs")
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting jobs: {e}")
            return False
        finally:
            conn.close()
    
    def get_job_count(self):
        """Get total number of jobs in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM jobs")
            count = cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            print(f"Error getting job count: {e}")
            return 0
        finally:
            conn.close()