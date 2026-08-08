"""
Backend Utils Package
Exports all utility functions and modules
"""

from .auth import (
    hash_password,
    verify_passcode,
    create_session,
    verify_session,
    invalidate_session,
    get_active_sessions_count
)

from .excel_parser import (
    parse_excel_file,
    get_grade,
    validate_file
)

__all__ = [
    # Auth utilities
    'hash_password',
    'verify_passcode',
    'create_session',
    'verify_session',
    'invalidate_session',
    'get_active_sessions_count',
    
    # Excel parser utilities
    'parse_excel_file',
    'get_grade',
    'validate_file'
]
