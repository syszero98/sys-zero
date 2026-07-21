"""
Admin Routes
API endpoints for admin panel (P1, P2, P3)
"""

from flask import Blueprint, request, jsonify, render_template
from werkzeug.utils import secure_filename
from backend.utils.auth import create_session, verify_session, invalidate_session
from backend.utils.excel_parser import parse_excel_file, validate_file
from backend.utils.validator import sanitize_input
import json
import os
from datetime import datetime

admin_routes = Blueprint('admin', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'database.json')
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

# ==========================================
# PHASE 1: PASSCODE VERIFICATION
# ==========================================

@admin_routes.route('/admin', methods=['GET'])
def admin_panel():
    """Render Admin Panel"""
    return render_template('admin/admin.html')

@admin_routes.route('/api/admin/login', methods=['POST'])
def admin_login():
    """P1: Verify passcode and create session"""
    try:
        data = request.get_json()
        passcode = data.get('passcode', '').strip()
        
        if not passcode:
            return jsonify({'success': False, 'message': 'Passcode required'}), 400
        
        # Create session
        session_token = create_session(passcode)
        
        if not session_token:
            return jsonify({'success': False, 'message': 'Invalid passcode'}), 401
        
        return jsonify({
            'success': True,
            'message': 'Authentication successful',
            'sessionToken': session_token
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# PHASE 2: DATA SYNC (EXCEL UPLOAD)
# ==========================================

@admin_routes.route('/api/admin/upload-excel', methods=['POST'])
def upload_excel():
    """P2: Upload and parse Excel file"""
    try:
        # Verify session
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not verify_session(session_token):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        # Check file
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        class_name = sanitize_input(request.form.get('class', ''))
        year = sanitize_input(request.form.get('year', ''))
        exam = sanitize_input(request.form.get('exam', ''))
        
        if not all([class_name, year, exam]):
            return jsonify({'success': False, 'message': 'Missing class/year/exam'}), 400
        
        # Validate file
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        ext = file.filename.split('.')[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return jsonify({'success': False, 'message': 'Invalid file format'}), 400
        
        # Save and parse
        filename = secure_filename(f"{class_name}_{year}_{exam}_{datetime.now().timestamp()}.{ext}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Parse Excel
        students, parse_msg = parse_excel_file(filepath)
        
        if students is None:
            return jsonify({'success': False, 'message': parse_msg}), 400
        
        # Load existing database
        database = load_database()
        
        # Create structure if not exists
        if class_name not in database:
            database[class_name] = {}
        if year not in database[class_name]:
            database[class_name][year] = {}
        
        # Store students
        database[class_name][year][exam] = students
        
        # Save database
        if not save_database(database):
            return jsonify({'success': False, 'message': 'Failed to save data'}), 500
        
        # Cleanup uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {len(students)} students',
            'count': len(students)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ==========================================
# PHASE 3: SUCCESS & LOGOUT
# ==========================================

@admin_routes.route('/api/admin/sync-status', methods=['GET'])
def sync_status():
    """P3: Get current sync status"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not verify_session(session_token):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
        database = load_database()
        
        total_classes = len(database)
        total_exams = sum(len(year_data) for class_data in database.values() 
                         for year_data in class_data.values())
        total_students = sum(len(exam_data) for class_data in database.values() 
                            for year_data in class_data.values() 
                            for exam_data in year_data.values())
        
        return jsonify({
            'success': True,
            'stats': {
                'totalClasses': total_classes,
                'totalExams': total_exams,
                'totalStudents': total_students,
                'lastSyncTime': datetime.now().isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_routes.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    """Logout and invalidate session"""
    try:
        session_token = request.headers.get('Authorization', '').replace('Bearer ', '')
        invalidate_session(session_token)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
