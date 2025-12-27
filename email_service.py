"""
Email Service
Sends Oura Ring data via email using SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional


def format_duration(seconds: int) -> str:
    """Convert seconds to human-readable duration like '7h 40m'"""
    if seconds is None:
        return "N/A"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_time(iso_string: str) -> str:
    """Convert ISO datetime to readable time like '2:01 AM'"""
    if not iso_string:
        return "N/A"
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%-I:%M %p")
    except:
        return iso_string


def format_date_short(date_str: str) -> str:
    """Convert YYYY-MM-DD to 'Dec 26'"""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %-d")
    except:
        return date_str


def safe_get(data: dict, *keys, default="N/A"):
    """Safely navigate nested dict keys"""
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        elif isinstance(result, list) and len(result) > 0:
            result = result[0].get(key) if isinstance(result[0], dict) else None
        else:
            return default
        if result is None:
            return default
    return result


def format_oura_report(oura_data: dict) -> str:
    """
    Format Oura data into clean, human-readable text report
    """
    date = oura_data.get("date", "Unknown")  # Sleep date (today)
    activity_date = oura_data.get("activity_date", date)  # Activity date (yesterday)
    
    # Extract data sections
    daily_sleep = oura_data.get("daily_sleep", {})
    sleep_data = daily_sleep.get("data", [{}])[0] if daily_sleep.get("data") else {}
    
    sleep_periods = oura_data.get("sleep_periods", {})
    # Find the main "long_sleep" period, not naps or rest periods
    period_data = {}
    if sleep_periods.get("data"):
        for period in sleep_periods["data"]:
            if period.get("type") == "long_sleep":
                period_data = period
                break
        # Fallback to first period if no long_sleep found
        if not period_data and sleep_periods["data"]:
            period_data = sleep_periods["data"][0]
    
    daily_activity = oura_data.get("daily_activity", {})
    activity_data = daily_activity.get("data", [{}])[0] if daily_activity.get("data") else {}
    
    daily_readiness = oura_data.get("daily_readiness", {})
    readiness_data = daily_readiness.get("data", [{}])[0] if daily_readiness.get("data") else {}
    
    daily_stress = oura_data.get("daily_stress", {})
    stress_data = daily_stress.get("data", [{}])[0] if daily_stress.get("data") else {}
    
    workouts = oura_data.get("workouts", {})
    workout_list = workouts.get("data", []) if workouts else []
    
    # Get scores
    sleep_score = sleep_data.get("score", "N/A")
    activity_score = activity_data.get("score", "N/A")
    readiness_score = readiness_data.get("score", "N/A")
    
    # Sleep contributors
    sleep_contrib = sleep_data.get("contributors", {})
    
    # Readiness contributors  
    readiness_contrib = readiness_data.get("contributors", {})
    
    # Sleep period details
    bedtime_start = format_time(period_data.get("bedtime_start", ""))
    bedtime_end = format_time(period_data.get("bedtime_end", ""))
    time_in_bed = format_duration(period_data.get("time_in_bed", 0))
    total_sleep = format_duration(period_data.get("total_sleep_duration", 0))
    latency_sec = period_data.get("latency", 0)
    latency_min = latency_sec // 60 if latency_sec else 0
    
    deep_duration = format_duration(period_data.get("deep_sleep_duration", 0))
    rem_duration = format_duration(period_data.get("rem_sleep_duration", 0))
    light_duration = format_duration(period_data.get("light_sleep_duration", 0))
    
    avg_hr = period_data.get("average_heart_rate", "N/A")
    lowest_hr = period_data.get("lowest_heart_rate", "N/A")
    avg_hrv = period_data.get("average_hrv", "N/A")
    avg_breath = period_data.get("average_breath", "N/A")
    restless = period_data.get("restless_periods", "N/A")
    
    # Readiness details
    temp_dev = readiness_data.get("temperature_deviation", "N/A")
    if isinstance(temp_dev, (int, float)):
        temp_dev = f"{temp_dev:+.2f}°C"
    
    # Activity details
    steps = activity_data.get("steps", "N/A")
    if isinstance(steps, int):
        steps = f"{steps:,}"
    active_cal = activity_data.get("active_calories", "N/A")
    low_activity = format_duration(activity_data.get("low_activity_time", 0))
    med_activity = format_duration(activity_data.get("medium_activity_time", 0))
    high_activity = format_duration(activity_data.get("high_activity_time", 0))
    
    # Stress details
    stress_summary = stress_data.get("day_summary", "N/A")
    recovery_high = stress_data.get("recovery_high", 0)
    stress_high = stress_data.get("stress_high", 0)
    recovery_time = format_duration(recovery_high) if recovery_high else "0m"
    stress_time = format_duration(stress_high) if stress_high else "0m"
    
    date_short = format_date_short(date)
    activity_date_short = format_date_short(activity_date)
    
    # Build the report
    report = f"""Oura Daily Report — {date}

SCORES
  Sleep: {sleep_score} | Activity: {activity_score} | Readiness: {readiness_score}

SLEEP ({date_short})
  Bedtime: {bedtime_start} → {bedtime_end} ({time_in_bed} in bed)
  Total sleep: {total_sleep}
  Latency: {latency_min} min
  
  Stages:
    Deep: {deep_duration} (score: {sleep_contrib.get('deep_sleep', 'N/A')})
    REM: {rem_duration} (score: {sleep_contrib.get('rem_sleep', 'N/A')})
    Light: {light_duration}
  
  Contributors:
    Timing: {sleep_contrib.get('timing', 'N/A')} | Efficiency: {sleep_contrib.get('efficiency', 'N/A')} | Restfulness: {sleep_contrib.get('restfulness', 'N/A')}
    Latency: {sleep_contrib.get('latency', 'N/A')} | Total: {sleep_contrib.get('total_sleep', 'N/A')}
  
  Physiology:
    Avg HR: {avg_hr} bpm | Lowest: {lowest_hr} bpm
    Avg HRV: {avg_hrv} ms
    Avg breath: {avg_breath}/min
    Restless periods: {restless}

READINESS
  Score: {readiness_score}
  Temp deviation: {temp_dev}
  Contributors:
    HRV balance: {readiness_contrib.get('hrv_balance', 'N/A')} | Sleep balance: {readiness_contrib.get('sleep_balance', 'N/A')}
    Previous night: {readiness_contrib.get('previous_night', 'N/A')} | Recovery index: {readiness_contrib.get('recovery_index', 'N/A')}

ACTIVITY ({activity_date_short})
  Steps: {steps}
  Active calories: {active_cal}
  Low activity: {low_activity} | Medium: {med_activity} | High: {high_activity}

STRESS ({activity_date_short})
  Day summary: {stress_summary}
  Recovery time: {recovery_time} | Stress time: {stress_time}
"""
    
    # Add workouts if any
    if workout_list:
        report += "\nWORKOUTS\n"
        for w in workout_list:
            w_type = w.get("activity", "Unknown")
            w_cal = w.get("calories", "N/A")
            w_duration = format_duration(w.get("duration", 0))
            report += f"  {w_type}: {w_duration}, {w_cal} cal\n"
    else:
        report += "\nWORKOUTS\n  None logged\n"
    
    return report


def format_html_report(oura_data: dict) -> str:
    """
    Format Oura data as a simple plain HTML email
    """
    text_report = format_oura_report(oura_data)
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ 
            font-family: monospace;
            font-size: 14px;
            line-height: 1.5;
            color: #333;
        }}
        pre {{
            white-space: pre-wrap;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <pre>{text_report}</pre>
</body>
</html>
"""
    return html


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        sender_email: str,
        sender_password: str,
        use_tls: bool = True
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls
    
    def send_email(
        self,
        recipient: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            recipient: Email address to send to
            subject: Email subject line
            body_text: Plain text body
            body_html: Optional HTML body
            
        Returns:
            True if sent successfully, False otherwise
        """
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = recipient
        
        # Attach plain text
        part1 = MIMEText(body_text, "plain")
        msg.attach(part1)
        
        # Attach HTML if provided
        if body_html:
            part2 = MIMEText(body_html, "html")
            msg.attach(part2)
        
        try:
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, recipient, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_oura_data(self, recipient: str, oura_data: dict) -> bool:
        """
        Send Oura Ring data as a formatted email
        
        Args:
            recipient: Email address to send to
            oura_data: Dict containing Oura data from OuraClient
            
        Returns:
            True if sent successfully, False otherwise
        """
        date = oura_data.get("date", "Unknown")
        subject = f"🌙 Oura Daily Report — {date}"
        
        # Format as clean human-readable text
        body_text = format_oura_report(oura_data)
        
        # Format as styled HTML
        body_html = format_html_report(oura_data)
        
        return self.send_email(recipient, subject, body_text, body_html)
