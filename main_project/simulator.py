import requests
import time
import random
from datetime import datetime

API_URL = "http://localhost:8000/api/logs"

HOSTS = ["web-prod-01", "web-prod-02", "db-prod-01", "mail-server-01", "workstation-102"]
USERS = ["admin", "jsmith", "bwayne", "ckent", "pwilson"]
NORMAL_EVENTS = ["page_view", "successful_login", "file_access", "api_request"]

def send_log(host, event_type, raw_message):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "host": host,
        "event_type": event_type,
        "raw_message": raw_message
    }
    try:
        requests.post(API_URL, json=log_entry)
        print(f"Sent: {host} | {event_type} | {raw_message}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send log (Is the backend running?): {e}")

def simulate_normal_traffic():
    host = random.choice(HOSTS)
    event_type = random.choice(NORMAL_EVENTS)
    msg = f"Normal activity: {event_type} by user {random.choice(USERS)}"
    send_log(host, event_type, msg)

def simulate_attack_failed_logins():
    print("\n--- INITIATING BRUTE FORCE SIMULATION ---")
    host = random.choice(HOSTS)
    user = random.choice(USERS)
    # The rule threshold is 5 failed logins within 60s. We send 7.
    for i in range(7):
        send_log(host, "failed_login", f"Failed authentication for user {user} from unknown IP")
        time.sleep(0.5)

def simulate_error_spike():
    print("\n--- INITIATING ERROR SPIKE SIMULATION ---")
    host = random.choice(HOSTS)
    # The rule threshold is 10 errors within 60s. We send 12.
    for i in range(12):
        send_log(host, "error", f"Critical service failure or timeout {i+1}")
        time.sleep(0.5)

if __name__ == "__main__":
    print("Starting Mini SIEM Event Simulator...")
    print("Press Ctrl+C to stop.")
    
    counter = 0
    try:
        while True:
            # Send normal traffic
            simulate_normal_traffic()
            time.sleep(random.uniform(0.5, 2.0))
            counter += 1
            
            # Occasionally trigger anomalies (roughly every ~15-30 seconds)
            if counter % 15 == 0:
                if random.choice([True, False]):
                    simulate_attack_failed_logins()
                else:
                    simulate_error_spike()
    except KeyboardInterrupt:
        print("\nSimulator stopped.")
