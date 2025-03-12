import re
import argparse
import json
import time
import os
import smtplib
from email.mime.text import MIMEText

# Load email settings from a configuration file
def load_email_settings():
    """Load email notification settings from a JSON config file."""
    with open("email_config.json", "r") as file:
        return json.load(file)

# Send email alert
def send_email_alert(subject, message):
    """Send an email alert when suspicious activity is detected."""
    settings = load_email_settings()
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = settings["sender_email"]
    msg["To"] = settings["recipient_email"]
    
    try:
        with smtplib.SMTP(settings["smtp_server"], settings["smtp_port"]) as server:
            server.starttls()
            server.login(settings["sender_email"], settings["password"])
            server.sendmail(settings["sender_email"], settings["recipient_email"], msg.as_string())
            print("📧 Email alert sent successfully.")
    except Exception as e:
        print(f"❌ Error sending email alert: {e}")

def load_config(config_file):
    """Load security patterns from a JSON config file."""
    with open(config_file, "r") as file:
        return json.load(file)

def scan_log(log_file, patterns):
    """Monitor a log file for suspicious activity."""
    suspicious_entries = []
    
    with open(log_file, "r") as file:
        for line in file:
            for label, pattern in patterns.items():
                if re.search(pattern, line):
                    suspicious_entries.append((label, line.strip()))
    
    return suspicious_entries

def generate_alerts(entries):
    """Print out detected suspicious entries and send email alerts."""
    if not entries:
        print("✅ No suspicious activity detected.")
        return
    
    print("\n🚨 ALERT: Suspicious activity detected! 🚨")
    alert_message = ""
    for label, entry in entries:
        alert_message += f"[{label}] -> {entry}\n"
        print(f"[{label}] -> {entry}")
    
    # Send email notification
    send_email_alert("LogHawk Security Alert", alert_message)

def monitor_log(log_file, patterns):
    """Continuously monitor the log file for real-time analysis."""
    print(f"🔍 Monitoring {log_file} for suspicious activity... Press Ctrl+C to stop.")
    try:
        with open(log_file, "r") as file:
            file.seek(0, os.SEEK_END)  # Move to the end of the file
            while True:
                line = file.readline()
                if not line:
                    time.sleep(1)  # Wait for new lines to appear
                    continue
                
                for label, pattern in patterns.items():
                    if re.search(pattern, line):
                        alert_message = f"[{label}] -> {line.strip()}"
                        print(f"\n🚨 {alert_message}")
                        send_email_alert("LogHawk Security Alert", alert_message)
    except KeyboardInterrupt:
        print("\n🛑 Stopping log monitoring.")

def main():
    parser = argparse.ArgumentParser(description="LogHawk - Real-Time Log Monitoring Tool")
    parser.add_argument("logfile", help="Path to the log file")
    parser.add_argument("--config", default="config.json", help="Path to config file with search patterns")
    parser.add_argument("--monitor", action='store_true', help="Enable real-time monitoring mode")
    args = parser.parse_args()
    
    if not os.path.exists(args.logfile):
        print(f"❌ Error: Log file {args.logfile} does not exist.")
        return
    
    if not os.path.exists(args.config):
        print(f"❌ Error: Config file {args.config} does not exist.")
        return
    
    patterns = load_config(args.config)
    
    if args.monitor:
        monitor_log(args.logfile, patterns)
    else:
        suspicious_entries = scan_log(args.logfile, patterns)
        generate_alerts(suspicious_entries)

if __name__ == "__main__":
    main()
