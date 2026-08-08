"""
Backend Routes Package
Exports all route blueprints
"""

from .student import student_routes
from .admin import admin_routes

__all__ = [
    'student_routes',
    'admin_routes'
]
