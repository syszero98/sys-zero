#!/usr/bin/env python3
"""
Application Entry Point
Run this file to start the server
"""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Syszero Student Result Portal")
    print("=" * 50)
    print("📍 Server running at: http://localhost:5000")
    print("👨‍💼 Admin Panel: http://localhost:5000/admin")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
