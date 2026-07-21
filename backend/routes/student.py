"""
Student Routes
API endpoints for student search and result retrieval
"""

from flask import Blueprint, request, jsonify
from backend.utils.validator import sanitize_input, validate_search_query
import json
import os

student_routes = Blueprint('student', __name__)

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.json')

def load_database():
    """Load database from JSON file"""
    try:
        if os.path.exists(DATABASE_PATH):
            with open(DATABASE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading database: {e}")
        return {}

@student_routes.route('/api/student/search', methods=['POST'])
def search_student():
    """Search student by roll or name"""
    try:
        data = request.get_json()
        
        class_name = sanitize_input(data.get('class', ''))
        year = sanitize_input(data.get('year', ''))
        exam = sanitize_input(data.get('exam', ''))
        search_type = data.get('searchType', 'roll')
        search_value = sanitize_input(data.get('searchValue', ''))
        
        # Validate search query
        is_valid, msg = validate_search_query(search_value)
        if not is_valid:
            return jsonify({'success': False, 'message': msg}), 400
        
        # Load database
        database = load_database()
        
        # Navigate to exam data
        if class_name not in database:
            return jsonify({'success': False, 'message': 'Class not found'}), 404
        
        if year not in database[class_name]:
            return jsonify({'success': False, 'message': 'Year not found'}), 404
        
        if exam not in database[class_name][year]:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404
        
        exam_data = database[class_name][year][exam]
        
        # Search
        student = None
        if search_type == 'roll':
            for std in exam_data:
                if str(std.get('roll', '')).lower() == str(search_value).lower():
                    student = std
                    break
        else:
            search_lower = search_value.lower()
            for std in exam_data:
                if str(std.get('name', '')).lower().startswith(search_lower):
                    student = std
                    break
        
        if not student:
            return jsonify({
                'success': False,
                'message': f'Student not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': student
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@student_routes.route('/api/student/options', methods=['GET'])
def get_student_options():
    """Get all class/year/exam options"""
    try:
        database = load_database()
        
        options = {}
        for class_name in database:
            options[class_name] = {}
            for year in database[class_name]:
                options[class_name][year] = list(database[class_name][year].keys())
        
        return jsonify({
            'success': True,
            'data': options
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
