"""
Authentication Utilities
Handles passcode verification and session management
"""

import hashlib
import secrets
from datetime import datetime, timedelta

# Admin Passcode (hashed for security)
ADMIN_PASSCODE = "mutapetsarakpelet"
ADMIN_PASSCODE_HASH = hashlib.sha256(ADMIN_PASSCODE.encode()).hexdigest()

# Session storage (in production, use proper database)
admin_sessions = {}

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_passcode(passcode):
    """Verify admin passcode"""
    return hash_password(passcode) == ADMIN_PASSCODE_HASH

def create_session(passcode):
    """Create new admin session if passcode is correct"""
    if not verify_passcode(passcode):
        return None
    
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # Store session with expiry (2 hours)
    admin_sessions[session_token] = {
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=2)
    }
    
    return session_token

def verify_session(session_token):
    """Verify if session is valid and not expired"""
    if session_token not in admin_sessions:
        return False
    
    session = admin_sessions[session_token]
    if datetime.now() > session['expires_at']:
        del admin_sessions[session_token]
        return False
    
    return True

def invalidate_session(session_token):
    """Invalidate a session"""
    if session_token in admin_sessions:
        del admin_sessions[session_token]
        return True
    return False

def get_active_sessions_count():
    """Get count of active sessions"""
    # Remove expired sessions
    expired = [token for token, session in admin_sessions.items() 
               if datetime.now() > session['expires_at']]
    
    for token in expired:
        del admin_sessions[token]
    
    return len(admin_sessions)
