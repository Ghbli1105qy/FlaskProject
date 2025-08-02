from datetime import datetime, timedelta
import json

def format_time(timestamp):
    return datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_time_range(days=1):
    end = datetime.now()
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()