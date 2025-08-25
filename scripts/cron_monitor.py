#!/usr/bin/env python3
"""
Cron-friendly monitoring script for training jobs
Add to crontab: */30 * * * * cd /path/to/medlitbot && python scripts/cron_monitor.py
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta


def log_message(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def main():
    """
    Cron-friendly monitoring with minimal output unless issues found
    """
    # Change to project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    os.chdir(project_dir)
    
    db_path = 'db.sqlite3'
    
    if not os.path.exists(db_path):
        log_message("❌ Database file not found!")
        sys.exit(1)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Find stuck jobs (older than 3 hours)
        timeout_threshold = (datetime.now() - timedelta(hours=3)).isoformat()
        
        cursor.execute("""
            SELECT 
                tj.id, m.name, tj.created_at, tj.progress_percentage
            FROM classification_trainingjob tj
            JOIN classification_mlmodel m ON tj.model_id = m.id
            WHERE tj.status IN ('running', 'pending')
            AND tj.created_at < ?
        """, (timeout_threshold,))
        
        stuck_jobs = cursor.fetchall()
        
        if not stuck_jobs:
            # Only log success every 6 hours to avoid spam
            current_hour = datetime.now().hour
            if current_hour % 6 == 0:
                log_message("✅ No stuck training jobs found")
            conn.close()
            return
        
        # Found stuck jobs - log and fix them
        log_message(f"🚨 ALERT: Found {len(stuck_jobs)} stuck training jobs")
        
        for job in stuck_jobs:
            job_id, model_name, created_at, progress = job
            age_hours = (datetime.now() - datetime.fromisoformat(created_at)).total_seconds() / 3600
            log_message(f"  - Job {job_id}: {model_name} ({progress}%, {age_hours:.1f}h old)")
        
        # Auto-cleanup
        log_message("🧹 Auto-fixing stuck jobs...")
        
        current_time = datetime.now().isoformat()
        fixed_count = 0
        
        for job in stuck_jobs:
            job_id, model_name, _, _ = job
            
            # Get model ID for this job
            cursor.execute("SELECT model_id FROM classification_trainingjob WHERE id = ?", (job_id,))
            model_id = cursor.fetchone()[0]
            
            try:
                # Update training job
                cursor.execute("""
                    UPDATE classification_trainingjob 
                    SET status = 'failed',
                        error_message = 'Training job stuck - auto-cleanup by cron monitor',
                        completed_at = ?
                    WHERE id = ?
                """, (current_time, job_id))
                
                # Update model
                cursor.execute("""
                    UPDATE classification_mlmodel 
                    SET status = 'failed'
                    WHERE id = ?
                """, (model_id,))
                
                fixed_count += 1
                
            except Exception as e:
                log_message(f"❌ Failed to fix job {job_id}: {e}")
        
        conn.commit()
        conn.close()
        
        log_message(f"✅ Successfully auto-fixed {fixed_count} stuck training jobs")
        log_message("💡 Users can now retry training from the frontend")
        
        # Exit with error code to alert monitoring systems
        if fixed_count > 0:
            sys.exit(2)  # Non-zero exit indicates issues were found and fixed
            
    except Exception as e:
        log_message(f"❌ Monitor script error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
