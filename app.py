import os
import io
import logging
import pandas as pd
import zipfile
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-dev")

# Add a now function for templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow}

# Paths to the data files
EXCEL_FILE_PATH = 'attached_assets/OJT Schedule Certificate.xlsx'
ZIP_FILE_PATH = 'attached_assets/OJT Student\'s Certificate_2025.zip'

# Global variable to store student data
STUDENT_DATA = []

def load_student_data():
    """Load student data from Excel file"""
    global STUDENT_DATA
    try:
        logging.debug(f"Loading Excel file from {EXCEL_FILE_PATH}")
        # Use header=1 to skip the first row (which contains the title)
        df = pd.read_excel(EXCEL_FILE_PATH, header=1)
        
        # Rename columns to standardize (Student Id -> Student ID)
        if 'Student Id' in df.columns:
            df = df.rename(columns={'Student Id': 'Student ID'})
            
        # Also rename other important columns for consistency
        column_mapping = {
            'Name of the Student': 'Name',
            'Programme/College': 'Course',
            'Reference No': 'Reference Number'
        }
        df = df.rename(columns=column_mapping)
        
        # Convert to records
        STUDENT_DATA = df.to_dict(orient='records')
        
        # Log column names and sample data for debugging
        logging.debug(f"Columns in Excel: {df.columns.tolist()}")
        if len(df) > 0:
            logging.debug(f"Sample Student ID: {df.iloc[0]['Student ID'] if 'Student ID' in df.columns else 'Not found'}")
            
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
    student_id = request.form.get('student_id', '').strip()
    
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
        student_data = {k: str(v).strip() for k, v in student.items() if v is not None}
        if 'Student ID' in student_data and student_data['Student ID'] == student_id:
            found_student = student
            break
    
    if found_student:
        # Store found student in session for the result page
        session['found_student'] = found_student
        logger.info(f"Found student with ID: {student_id}")
        return redirect(url_for('show_result'))
    else:
        logger.warning(f"No student found with ID: {student_id}")
        # Instead of redirecting with a flash message, render the not_found template
        return render_template('not_found.html', student_id=student_id)

@app.route('/result')
def show_result():
    if 'found_student' not in session:
        flash('No student data found. Please search for a student first.', 'warning')
        return redirect(url_for('index'))
    
    student = session['found_student']
    # Format the student data for display
    formatted_student = {}
    for key, value in student.items():
        if pd.notna(value):  # Skip NaN values
            # Format special fields
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                formatted_student[key] = str(value).replace('.0', '') if str(value).endswith('.0') else str(value)
            else:
                formatted_student[key] = str(value)
    
    return render_template('result.html', student=formatted_student)

@app.route('/download_certificate')
def download_certificate():
    if 'found_student' not in session:
        flash('No student data found. Please search for a student first.', 'warning')
        return redirect(url_for('index'))
    
    student = session['found_student']
    
    # Get the student ID for error handling
    student_id = None
    if 'Student ID' in student and pd.notna(student['Student ID']):
        student_id = str(student['Student ID']).strip()

    # Get the reference number from the student data
    reference_no = None
    
    # Check all possible reference column names
    for ref_column in ['Reference Number', 'Reference No']:
        if ref_column in student and pd.notna(student[ref_column]):
            value = student[ref_column]
            reference_no = str(value).replace('.0', '') if str(value).endswith('.0') else str(value)
            logger.debug(f"Found reference number '{reference_no}' in column '{ref_column}'")
            break
    
    if not reference_no:
        logger.error("Missing reference number for student")
        # Render certificate error template instead of redirect and flash
        return render_template('certificate_error.html', 
                             error_message="No reference number found for this student record.",
                             student_id=student_id)
    
    try:
        # Check if ZIP file exists
        if not os.path.exists(ZIP_FILE_PATH):
            logger.error(f"ZIP file not found: {ZIP_FILE_PATH}")
            return render_template('certificate_error.html',
                                 error_message="Certificate archive not found. Please contact support.",
                                 student_id=student_id)
        
        # Open the zip file
        with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            logger.debug(f"Found {len(file_list)} files in archive")
            
            # Find the certificate by reference number
            certificate_file = None
            for file_name in file_list:
                # Check if the file name contains the reference number
                if reference_no in file_name:
                    certificate_file = file_name
                    logger.info(f"Found matching certificate: {file_name}")
                    break
            
            if not certificate_file:
                logger.error(f"No certificate found for reference number: {reference_no}")
                return render_template('certificate_error.html',
                                     error_message=f"Certificate not found for reference number: {reference_no}",
                                     student_id=student_id)
            
            # Extract the certificate file
            certificate_data = zip_ref.read(certificate_file)
            certificate_io = io.BytesIO(certificate_data)
            certificate_io.seek(0)
            
            # Get student name for the download filename
            student_name = "Unknown"
            if 'Name' in student and pd.notna(student['Name']):
                student_name = str(student['Name']).strip().replace(' ', '_')
            
            # Send the file to the client
            logger.info(f"Sending certificate file for reference: {reference_no}")
            
            # Determine the file extension from the original filename (most likely PNG)
            file_extension = os.path.splitext(certificate_file)[1].lower() or '.png'
            
            # Set the correct mimetype based on file extension
            mimetype = 'image/png' if file_extension == '.png' else 'application/octet-stream'
            
            return send_file(
                certificate_io,
                as_attachment=True,
                download_name=f"OJT_Certificate_{student_name}_{reference_no}{file_extension}",
                mimetype=mimetype
            )
    
    except Exception as e:
        logger.error(f"Error extracting certificate: {str(e)}")
        return render_template('certificate_error.html',
                             error_message=f"Error retrieving certificate: {str(e)}",
                             student_id=student_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
