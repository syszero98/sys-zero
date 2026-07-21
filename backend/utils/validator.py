"""
Input Validation Utility
Handles data validation and sanitization
"""

import re
from typing import Tuple, Any

def validate_email(email: str) -> Tuple[bool, str]:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Valid email"
    return False, "Invalid email format"

def validate_roll_number(roll: str) -> Tuple[bool, str]:
    """Validate roll number (alphanumeric)"""
    if not roll or not isinstance(roll, str):
        return False, "Roll number must be a string"
    
    if len(roll.strip()) == 0:
        return False, "Roll number cannot be empty"
    
    if len(roll) > 20:
        return False, "Roll number too long"
    
    return True, "Valid roll number"

def validate_student_name(name: str) -> Tuple[bool, str]:
    """Validate student name"""
    if not name or not isinstance(name, str):
        return False, "Name must be a string"
    
    if len(name.strip()) == 0:
        return False, "Name cannot be empty"
    
    if len(name) > 100:
        return False, "Name too long"
    
    return True, "Valid name"

def validate_marks(marks: Any) -> Tuple[bool, float]:
    """Validate marks (0-100)"""
    try:
        marks_float = float(marks)
        if 0 <= marks_float <= 100:
            return True, marks_float
        return False, 0
    except:
        return False, 0

def sanitize_input(input_str: str, max_length: int = 100) -> str:
    """Sanitize string input to prevent injection"""
    if not isinstance(input_str, str):
        return ""
    
    # Remove leading/trailing whitespace
    sanitized = input_str.strip()
    
    # Limit length
    sanitized = sanitized[:max_length]
    
    # Remove special characters except basic punctuation
    sanitized = re.sub(r'[<>\"\'%;()&+]', '', sanitized)
    
    return sanitized

def validate_class_name(class_name: str) -> Tuple[bool, str]:
    """Validate class name"""
    valid_classes = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    if class_name in valid_classes:
        return True, "Valid class"
    
    return False, f"Invalid class. Must be one of: {', '.join(valid_classes)}"

def validate_year(year: str) -> Tuple[bool, str]:
    """Validate academic year"""
    try:
        year_int = int(year)
        current_year = 2024
        
        if year_int >= 2000 and year_int <= current_year + 1:
            return True, "Valid year"
        
        return False, "Year out of range"
    except:
        return False, "Invalid year format"

def validate_search_query(query: str) -> Tuple[bool, str]:
    """Validate search query"""
    if not query or len(query.strip()) == 0:
        return False, "Search query cannot be empty"
    
    if len(query) > 50:
        return False, "Search query too long"
    
    return True, "Valid search query"
