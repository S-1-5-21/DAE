import requests
import time
import random
import threading
import sys
from datetime import datetime

API_URL = "http://localhost:8000/api/logs"

WEB_HOSTS = ["web-prod-01", "web-prod-02"]
DB_HOSTS = ["db-prod-01"]
WORKSTATIONS = ["workstation-102", "workstation-107"]
ALL_HOSTS = WEB_HOSTS + DB_HOSTS + WORKSTATIONS

USERS = ["jsmith", "bwayne", "ckent", "pwilson"]

def send_log(host, event_type, raw_message):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "host": host,
        "event_type": event_type,
        "raw_message": raw_message
    }
    try:
        requests.post(API_URL, json=log_entry)
        print(f"[*] Sent: {host} | {event_type} | {raw_message}")
    except requests.exceptions.RequestException:
        pass

def generate_normal_event():
    host_type = random.choice(["web", "db", "workstation"])
    
    if host_type == "web":
        host = random.choice(WEB_HOSTS)
        evt = random.choice(["page_view", "api_request"])
        msg = f"Standard {evt.replace('_', ' ')} from client IP"
        send_log(host, evt, msg)
        
    elif host_type == "db":
        host = random.choice(DB_HOSTS)
        send_log(host, "database_query", "Executed routine background query successfully")
        
    else:
        host = random.choice(WORKSTATIONS)
        user = random.choice(USERS)
        evt = random.choice(["successful_login", "file_access"])
        msg = f"User {user} {evt.replace('_', ' ')} routinely"
        send_log(host, evt, msg)

def backgroundActivity():
    while True:
        generate_normal_event()
        time.sleep(random.uniform(1.0, 4.0))

# All Scenarios

def trigger_password_attack():
    host = random.choice(WORKSTATIONS)
    target_user = "bwayne"
    print("\n[+] Triggering: Password Attack...")
    send_log(host, "successful_login", f"User jsmith logged in successfully.")
    time.sleep(1)
    
    for i in range(6):
        send_log(host, "failed_login", f"Repeated authentication failure for user {target_user}")
        time.sleep(0.3)
    print("[+] Done.\n")

def trigger_server_failure():
    host = random.choice(WEB_HOSTS)
    print("\n[+] Triggering: Server Failure...")
    send_log(host, "page_view", "User loaded the dashboard successfully.")
    time.sleep(1)
    
    for i in range(6):
        send_log(host, "error", f"Critical service timeout: Database connection lost ({i+1})")
        time.sleep(0.4)
    print("[+] Done.\n")

def trigger_suspicious_file_access():
    host = random.choice(WORKSTATIONS)
    print("\n[+] Triggering: Suspicious File Access...")
    send_log(host, "file_access", "User accessed public document /docs/policy.pdf")
    time.sleep(1)
    
    for i in range(6):
        send_log(host, "file_access", f"Restricted file access: Read attempt on /etc/shadow or HR database ({i+1})")
        time.sleep(0.3)
    print("[+] Done.\n")

def trigger_traffic_surge():
    host = random.choice(WEB_HOSTS)
    print("\n[+] Triggering: Traffic Surge...")
    for _ in range(2):
        send_log(host, "api_request", "Normal API request /api/v1/health")
        time.sleep(0.5)
        
    for i in range(16):
        send_log(host, "api_request", f"Overwhelming API request flood from single origin ({i+1})")
        time.sleep(0.05)
    print("[+] Done.\n")

def trigger_privilege_misuse():
    host = random.choice(WORKSTATIONS)
    user = random.choice(["jsmith", "ckent"])
    print("\n[+] Triggering: Privilege Misuse...")
    send_log(host, "successful_login", f"Standard user {user} logged in.")
    time.sleep(1)
    
    for i in range(4):
        send_log(host, "admin_action", f"Admin-only action executed: {user} modified security group policies.")
        time.sleep(0.5)
    print("[+] Done.\n")

def start_interactive():
    t = threading.Thread(target=backgroundActivity, daemon=True)
    t.start()
    
    while True:
        print("\n--- Presenter Simulator Menu ---")
        print("1. Password Attack")
        print("2. Server Failure")
        print("3. Suspicious File Access")
        print("4. Traffic Surge")
        print("5. Privilege Misuse")
        print("Q. Quit")
        choice = input("Select an incident to trigger: ").strip().lower()
        
        if choice == '1':
            trigger_password_attack()
        elif choice == '2':
            trigger_server_failure()
        elif choice == '3':
            trigger_suspicious_file_access()
        elif choice == '4':
            trigger_traffic_surge()
        elif choice == '5':
            trigger_privilege_misuse()
        elif choice == 'q':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    start_interactive()
