"""Utility functions for gdmongolite"""

import re
import json
import hashlib
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime, date
from decimal import Decimal
from bson import ObjectId
from pydantic import BaseModel

def to_snake_case(name: str) -> str:
    """Convert CamelCase to snake_case"""
    # Handle acronyms and multiple capitals
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()

def to_camel_case(name: str) -> str:
    """Convert snake_case to CamelCase"""
    components = name.split('_')
    return ''.join(word.capitalize() for word in components)

def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase (same as CamelCase)"""
    return to_camel_case(name)

def sanitize_collection_name(name: str) -> str:
    """Sanitize collection name for MongoDB"""
    # Remove invalid characters and convert to snake_case
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    return to_snake_case(sanitized).strip('_')

def generate_object_id() -> str:
    """Generate a new MongoDB ObjectId as string"""
    return str(ObjectId())

def is_valid_object_id(oid: str) -> bool:
    """Check if string is a valid ObjectId"""
    try:
        ObjectId(oid)
        return True
    except:
        return False

def serialize_for_mongo(obj: Any) -> Any:
    """Serialize Python objects for MongoDB storage"""
    if isinstance(obj, BaseModel):
        return obj.dict()
    elif isinstance(obj, (datetime, date)):
        return obj
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, ObjectId):
        return obj
    elif isinstance(obj, dict):
        return {k: serialize_for_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_mongo(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return serialize_for_mongo(obj.__dict__)
    else:
        return obj

def deserialize_from_mongo(obj: Any, target_type: Type = None) -> Any:
    """Deserialize MongoDB objects to Python objects"""
    if target_type and issubclass(target_type, BaseModel):
        return target_type(**obj) if isinstance(obj, dict) else obj
    elif isinstance(obj, dict):
        return {k: deserialize_from_mongo(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deserialize_from_mongo(item) for item in obj]
    else:
        return obj

def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary with dot notation"""
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)

def unflatten_dict(d: Dict, sep: str = '.') -> Dict:
    """Unflatten dictionary with dot notation"""
    result = {}
    
    for key, value in d.items():
        keys = key.split(sep)
        current = result
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    return result

def calculate_hash(data: Any) -> str:
    """Calculate MD5 hash of data"""
    if isinstance(data, dict):
        # Sort keys for consistent hashing
        data_str = json.dumps(data, sort_keys=True, default=str)
    else:
        data_str = str(data)
    
    return hashlib.md5(data_str.encode()).hexdigest()

def validate_field_name(name: str) -> bool:
    """Validate MongoDB field name"""
    # MongoDB field names cannot start with $ or contain .
    if name.startswith('$') or '.' in name:
        return False
    return True

def clean_field_name(name: str) -> str:
    """Clean field name for MongoDB compatibility"""
    # Replace invalid characters
    cleaned = re.sub(r'[.$]', '_', name)
    
    # Ensure it doesn't start with _
    if cleaned.startswith('_'):
        cleaned = 'field' + cleaned
    
    return cleaned

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def format_duration(milliseconds: float) -> str:
    """Format duration in human readable format"""
    if milliseconds < 1000:
        return f"{milliseconds:.1f}ms"
    elif milliseconds < 60000:
        return f"{milliseconds/1000:.1f}s"
    else:
        minutes = int(milliseconds / 60000)
        seconds = (milliseconds % 60000) / 1000
        return f"{minutes}m {seconds:.1f}s"

def batch_list(items: List, batch_size: int) -> List[List]:
    """Split list into batches"""
    return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]

def safe_get(dictionary: Dict, key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation"""
    keys = key_path.split('.')
    current = dictionary
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default

def safe_set(dictionary: Dict, key_path: str, value: Any) -> Dict:
    """Safely set nested dictionary value using dot notation"""
    keys = key_path.split('.')
    current = dictionary
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return dictionary

class Timer:
    """Simple timer for measuring execution time"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer"""
        self.start_time = datetime.now()
        return self
    
    def stop(self):
        """Stop the timer"""
        self.end_time = datetime.now()
        return self
    
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        if not self.start_time:
            return 0
        
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() * 1000
    
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds"""
        return self.elapsed_ms() / 1000
    
    def __enter__(self):
        """Context manager entry"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry function on failure"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        raise last_exception
            
            return None
        return wrapper
    return decorator

def validate_mongodb_name(name: str) -> bool:
    """Validate MongoDB database/collection name"""
    # MongoDB naming rules
    if not name:
        return False
    
    # Cannot be empty or too long
    if len(name) > 64:
        return False
    
    # Cannot contain certain characters
    invalid_chars = ['/', '\\', '.', '"', '*', '<', '>', ':', '|', '?']
    if any(char in name for char in invalid_chars):
        return False
    
    # Cannot start with certain characters
    if name.startswith(('$', ' ')) or name.endswith(' '):
        return False
    
    return True

def create_index_name(fields: Dict[str, int]) -> str:
    """Create index name from fields"""
    parts = []
    for field, direction in fields.items():
        direction_str = "1" if direction > 0 else "-1"
        parts.append(f"{field}_{direction_str}")
    
    return "_".join(parts)

def parse_connection_string(uri: str) -> Dict[str, Any]:
    """Parse MongoDB connection string"""
    import urllib.parse
    
    parsed = urllib.parse.urlparse(uri)
    
    result = {
        'scheme': parsed.scheme,
        'username': parsed.username,
        'password': parsed.password,
        'hostname': parsed.hostname,
        'port': parsed.port,
        'database': parsed.path.lstrip('/') if parsed.path else None,
        'options': {}
    }
    
    # Parse query parameters
    if parsed.query:
        result['options'] = dict(urllib.parse.parse_qsl(parsed.query))
    
    return result

class DebugLogger:
    """Simple debug logger for development"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message"""
        if self.enabled:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {level}: {message}")
    
    def debug(self, message: str):
        """Log debug message"""
        self.log(message, "DEBUG")
    
    def info(self, message: str):
        """Log info message"""
        self.log(message, "INFO")
    
    def warning(self, message: str):
        """Log warning message"""
        self.log(message, "WARNING")
    
    def error(self, message: str):
        """Log error message"""
        self.log(message, "ERROR")

# Global debug logger instance
debug_logger = DebugLogger()