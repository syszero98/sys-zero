"""
Flask Main Application Server
Student Result Portal - Syszero
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime

# Initialize Flask App
app = Flask(__name__, 
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'assets')
)

# Enable CORS
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'database.json')

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

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

def save_database(data):
    """Save database to JSON file"""
    try:
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving database: {e}")
        return False

def get_all_options():
    """Get all available Class, Year, Exam options"""
    data = load_database()
    
    # Structure: { Class: { Year: { Exam: [...students] } } }
    return data

# ==========================================
# STUDENT ROUTES
# ==========================================

@app.route('/')
def index():
    """Render Student Portal Home Page"""
    return render_template('index.html')

@app.route('/api/get-options', methods=['GET'])
def get_options():
    """API: Get all Class, Year, Exam options for dropdowns"""
    try:
        data = get_all_options()
        
        # Create structured response
        response_data = {}
        for class_name in data:
            response_data[class_name] = {}
            for year in data[class_name]:
                response_data[class_name][year] = list(data[class_name][year].keys())
        
        return jsonify({
            'success': True,
            'data': response_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/search-result', methods=['POST'])
def search_result():
    """API: Search student result"""
    try:
        req_data = request.get_json()
        
        class_name = req_data.get('class')
        year = req_data.get('year')
        exam = req_data.get('exam')
        search_type = req_data.get('searchType')
        search_value = req_data.get('searchValue', '').strip()

        # Validate input
        if not all([class_name, year, exam, search_type, search_value]):
            return jsonify({
                'success': False,
                'message': 'Missing required fields'
            }), 400

        # Load database
        data = load_database()

        # Navigate to exam data
        if class_name not in data:
            return jsonify({'success': False, 'message': 'Class not found'}), 404

        if year not in data[class_name]:
            return jsonify({'success': False, 'message': 'Year not found'}), 404

        if exam not in data[class_name][year]:
            return jsonify({'success': False, 'message': 'Exam not found'}), 404

        exam_data = data[class_name][year][exam]

        # Search based on type
        student = None
        
        if search_type == 'roll':
            # Search by roll number
            for std in exam_data:
                if str(std.get('roll', '')).lower() == str(search_value).lower():
                    student = std
                    break
        else:
            # Search by name
            search_lower = search_value.lower()
            for std in exam_data:
                if str(std.get('name', '')).lower().startswith(search_lower):
                    student = std
                    break

        if not student:
            return jsonify({
                'success': False,
                'message': f'No student found with {search_type}: {search_value}'
            }), 404

        return jsonify({
            'success': True,
            'data': student
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

# ==========================================
# ERROR HANDLERS
# ==========================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Resource not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

# ==========================================
# MAIN
# ==========================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
