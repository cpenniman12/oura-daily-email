#!/usr/bin/env python3
"""
Oura Ring Daily Email Service
Fetches Oura Ring data and emails it daily at a scheduled time
"""

import os
import sys
import time
import json
import schedule
from datetime import datetime
from dotenv import load_dotenv

from oura_client import OuraClient
from email_service import EmailService


def load_config():
    """Load configuration from environment variables"""
    load_dotenv()
    
    config = {
        "oura_token": os.getenv("OURA_ACCESS_TOKEN"),
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "sender_password": os.getenv("SENDER_PASSWORD"),
        "recipient_email": os.getenv("RECIPIENT_EMAIL", "cooperpenniman@gmail.com"),
        "schedule_time": os.getenv("SCHEDULE_TIME", "10:00")
    }
    
    # Validate required config
    missing = []
    if not config["oura_token"]:
        missing.append("OURA_ACCESS_TOKEN")
    if not config["sender_email"]:
        missing.append("SENDER_EMAIL")
    if not config["sender_password"]:
        missing.append("SENDER_PASSWORD")
    
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}")
        print("Please update your .env file")
        sys.exit(1)
    
    return config


def send_daily_report(config: dict):
    """Fetch Oura data and send email report"""
    print(f"[{datetime.now()}] Starting daily report...")
    
    # Initialize clients
    oura = OuraClient(config["oura_token"])
    email = EmailService(
        smtp_server=config["smtp_server"],
        smtp_port=config["smtp_port"],
        sender_email=config["sender_email"],
        sender_password=config["sender_password"]
    )
    
    # Fetch data
    print("Fetching Oura data...")
    data = oura.get_todays_data()
    
    # Send email
    print(f"Sending email to {config['recipient_email']}...")
    success = email.send_oura_data(config["recipient_email"], data)
    
    if success:
        print(f"[{datetime.now()}] Email sent successfully!")
    else:
        print(f"[{datetime.now()}] Failed to send email")
    
    return success


def run_scheduler(config: dict):
    """Run the scheduler to send daily emails"""
    schedule_time = config["schedule_time"]
    
    print(f"Oura Ring Daily Email Service")
    print(f"==============================")
    print(f"Scheduled time: {schedule_time}")
    print(f"Recipient: {config['recipient_email']}")
    print(f"Press Ctrl+C to stop\n")
    
    # Schedule the job
    schedule.every().day.at(schedule_time).do(send_daily_report, config)
    
    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def run_once(config: dict):
    """Run immediately without scheduling"""
    return send_daily_report(config)


def test_oura_connection(config: dict):
    """Test the Oura API connection and print data"""
    print("Testing Oura API connection...")
    oura = OuraClient(config["oura_token"])
    
    try:
        data = oura.get_todays_data()
        print("\n✅ Successfully connected to Oura API!")
        print("\nData preview:")
        print(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"\n❌ Failed to connect: {e}")
        return False


if __name__ == "__main__":
    config = load_config()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            # Test the Oura API connection
            test_oura_connection(config)
        elif command == "now":
            # Send email immediately
            run_once(config)
        elif command == "schedule":
            # Run with scheduler
            run_scheduler(config)
        else:
            print(f"Unknown command: {command}")
            print("Usage: python main.py [test|now|schedule]")
            print("  test     - Test Oura API connection")
            print("  now      - Send email immediately")
            print("  schedule - Run scheduler for daily emails")
    else:
        # Default: run scheduler
        run_scheduler(config)

