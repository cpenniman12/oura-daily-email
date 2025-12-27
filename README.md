# Oura Ring Daily Email Service

Automatically fetches your Oura Ring sleep and activity data and emails it to you every day at 10am.

## Features

- Fetches daily sleep scores and contributors
- Fetches detailed sleep period data (HR, HRV, etc.)
- Fetches daily activity scores and metrics
- Sends a beautifully formatted HTML email
- Runs on a schedule (default: 10:00 AM daily)

## Setup

### 1. Install Dependencies

```bash
cd /Users/cooperpenniman/oura-daily-email
pip install -r requirements.txt
```

### 2. Configure Email (Gmail)

For Gmail, you need to create an **App Password**:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication if not already enabled
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create a new app password for "Mail"
5. Copy the 16-character password

### 3. Update `.env` File

Edit the `.env` file with your email credentials:

```bash
OURA_ACCESS_TOKEN=your_token_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=cooperpenniman@gmail.com
SCHEDULE_TIME=10:00
```

## Usage

### Test Oura API Connection

```bash
python main.py test
```

This will fetch yesterday's data and print it to verify your Oura token works.

### Send Email Now (Manual)

```bash
python main.py now
```

### Run Scheduled Service

```bash
python main.py schedule
```

Or simply:

```bash
python main.py
```

This will run continuously and send an email every day at the scheduled time.

## Running as a Background Service (macOS)

### Option 1: Using launchd (Recommended)

Create a launch agent to run this automatically:

```bash
# Create the plist file
cat > ~/Library/LaunchAgents/com.oura.dailyemail.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.oura.dailyemail</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/cooperpenniman/oura-daily-email/venv/bin/python</string>
        <string>/Users/cooperpenniman/oura-daily-email/main.py</string>
        <string>schedule</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/cooperpenniman/oura-daily-email</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/cooperpenniman/oura-daily-email/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/cooperpenniman/oura-daily-email/logs/stderr.log</string>
</dict>
</plist>
EOF

# Create logs directory
mkdir -p /Users/cooperpenniman/oura-daily-email/logs

# Load the service
launchctl load ~/Library/LaunchAgents/com.oura.dailyemail.plist
```

To stop the service:
```bash
launchctl unload ~/Library/LaunchAgents/com.oura.dailyemail.plist
```

### Option 2: Using nohup

```bash
cd /Users/cooperpenniman/oura-daily-email
nohup python main.py schedule > logs/output.log 2>&1 &
```

## Data Included

### Sleep Data
- Sleep score
- Contributors: deep sleep, efficiency, latency, REM, restfulness, timing, total sleep

### Activity Data
- Activity score
- Active calories
- Average MET minutes
- Steps
- Contributors: daily targets, hourly movement, recovery time, stay active, training frequency/volume

## Troubleshooting

### Email not sending?
- Make sure you're using an App Password, not your regular Gmail password
- Check that 2FA is enabled on your Google account
- Verify the SMTP settings are correct

### No data from Oura?
- Run `python main.py test` to verify the API connection
- Make sure you wore your ring yesterday
- Data usually syncs a few hours after waking up

