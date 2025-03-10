import os
import io
import logging
import pandas as pd
import zipfile
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-dev")

# Add a now function for templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow}

# Paths to the data files
EXCEL_FILE_PATH = 'data/OJT Schedule Certificate.xlsx'
ZIP_FILE_PATH = 'data/renamed_certificates_2025.zip'

# Global variable to store student data
STUDENT_DATA = []

def load_student_data():
    """Load student data from Excel file"""
    global STUDENT_DATA
    try:
        logging.debug(f"Loading Excel file from {EXCEL_FILE_PATH}")
        df = pd.read_excel(EXCEL_FILE_PATH)
        STUDENT_DATA = df.to_dict(orient='records')
        logging.info(f"Loaded {len(STUDENT_DATA)} student records")
    except Exception as e:
        logging.error(f"Error loading student data: {str(e)}")
        STUDENT_DATA = []

# Load student data when app starts
load_student_data()

@app.route('/')
def index():
    # Ensure student data is loaded
    if not STUDENT_DATA:
        load_student_data()
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_student():
    student_id = request.form.get('student_id')
    
    if not student_id:
        flash('Please enter a Student ID', 'warning')
        return redirect(url_for('index'))
    
    # Make sure student data is loaded
    if not STUDENT_DATA:
        load_student_data()
        if not STUDENT_DATA:
            flash('System error: Could not load student data', 'danger')
            return redirect(url_for('index'))
    
    # Search for student in the loaded data
    found_student = None
    for student in STUDENT_DATA:
        # Convert all values to string for comparison
        student_data = {k: str(v) for k, v in student.items()}
        if 'Student ID' in student_data and student_data['Student ID'] == student_id:
            found_student = student
            break
    
    if found_student:
        # Store found student in session for the result page
        session['found_student'] = found_student
        return redirect(url_for('show_result'))
    else:
        flash(f'No student found with ID: {student_id}', 'danger')
        return redirect(url_for('index'))

@app.route('/result')
def show_result():
    if 'found_student' not in session:
        flash('No student data found. Please search for a student first.', 'warning')
        return redirect(url_for('index'))
    
    student = session['found_student']
    return render_template('result.html', student=student)

@app.route('/download_certificate')
def download_certificate():
    if 'found_student' not in session:
        flash('No student data found. Please search for a student first.', 'warning')
        return redirect(url_for('index'))
    
    student = session['found_student']
    
    # Get the reference number from the student data
    reference_no = None
    if 'Reference No' in student:
        reference_no = str(student['Reference No'])
    elif 'Reference Number' in student:
        reference_no = str(student['Reference Number'])
    
    if not reference_no:
        flash('No reference number found for this student', 'danger')
        return redirect(url_for('show_result'))
    
    try:
        # Check if ZIP file exists
        if not os.path.exists(ZIP_FILE_PATH):
            flash('Certificate archive not found', 'danger')
            logging.error(f"ZIP file not found: {ZIP_FILE_PATH}")
            return redirect(url_for('show_result'))
        
        # Open the zip file
        with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            
            # Find the certificate by reference number
            certificate_file = None
            for file_name in file_list:
                # Check if the file name contains the reference number
                if reference_no in file_name:
                    certificate_file = file_name
                    break
            
            if not certificate_file:
                flash(f'Certificate not found for reference number: {reference_no}', 'danger')
                return redirect(url_for('show_result'))
            
            # Extract the certificate file
            certificate_data = zip_ref.read(certificate_file)
            certificate_io = io.BytesIO(certificate_data)
            certificate_io.seek(0)
            
            # Send the file to the client
            return send_file(
                certificate_io,
                as_attachment=True,
                download_name=f"Certificate_{reference_no}.pdf",
                mimetype='application/pdf'
            )
    
    except Exception as e:
        logging.error(f"Error extracting certificate: {str(e)}")
        flash(f'Error retrieving certificate: {str(e)}', 'danger')
        return redirect(url_for('show_result'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
