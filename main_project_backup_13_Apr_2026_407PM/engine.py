import json
import os
from datetime import datetime, timedelta
from database import get_db

RULES_PATH = os.path.join(os.path.dirname(__file__), 'rules.json')

def load_rules():
    if not os.path.exists(RULES_PATH):
        return []
    with open(RULES_PATH, 'r') as f:
        return json.load(f)

def process_log(log):
    rules = load_rules()
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Insert log
        cursor.execute(
            'INSERT INTO logs (timestamp, host, event_type, raw_message) VALUES (?, ?, ?, ?)',
            (log.timestamp, log.host, log.event_type, log.raw_message)
        )
        conn.commit()
        
        # Evaluate rules
        for rule in rules:
            if log.event_type == rule.get('event_type'):
                threshold = rule.get('threshold', 5)
                interval_seconds = rule.get('interval_seconds', 60)
                
                # Check for threshold breaches
                try:
                    log_time = datetime.fromisoformat(log.timestamp)
                except ValueError:
                    continue # Ignore invalid timestamps
                    
                window_start = (log_time - timedelta(seconds=interval_seconds)).isoformat()
                
                cursor.execute('''
                    SELECT count(id) as count FROM logs 
                    WHERE host = ? AND event_type = ? AND timestamp >= ? AND timestamp <= ?
                ''', (log.host, log.event_type, window_start, log.timestamp))
                
                row = cursor.fetchone()
                if row and row['count'] >= threshold:
                    # Prevent alert spam (only 1 alert per minute per rule+host)
                    cursor.execute('''
                        SELECT count(id) as count FROM alerts
                        WHERE host = ? AND rule_triggered = ? AND timestamp >= ?
                    ''', (log.host, rule['rule_name'], window_start))
                    
                    alert_spam_check = cursor.fetchone()
                    if alert_spam_check and alert_spam_check['count'] == 0:
                        alert_msg = f"{rule.get('description')} ({row['count']} events in {interval_seconds}s)"
                        cursor.execute(
                            'INSERT INTO alerts (timestamp, host, rule_triggered, message, status) VALUES (?, ?, ?, ?, ?)',
                            (log.timestamp, log.host, rule['rule_name'], alert_msg, 'New')
                        )
                        conn.commit()
