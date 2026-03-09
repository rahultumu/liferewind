# Memory storage utility module
# Handles persistent storage of memories if needed

import json
from datetime import datetime
from pathlib import Path

MEMORY_LOG_FILE = "memory_log.json"

def log_memory(memory_data):
    """Log memory with timestamp"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "data": memory_data
    }
    
    try:
        if Path(MEMORY_LOG_FILE).exists():
            with open(MEMORY_LOG_FILE, "r") as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(entry)
        
        with open(MEMORY_LOG_FILE, "w") as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"Error logging memory: {e}")

def get_memory_logs():
    """Retrieve all memory logs"""
    try:
        if Path(MEMORY_LOG_FILE).exists():
            with open(MEMORY_LOG_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"Error reading memory logs: {e}")
    return []
