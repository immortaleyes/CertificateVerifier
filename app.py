import os
import io
import logging
import pandas as pd
import zipfile
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-dev")

# Add a now function for templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow}

# Allowed file extensions
ALLOWED_EXTENSIONS_EXCEL = {'xlsx', 'xls'}
ALLOWED_EXTENSIONS_ZIP = {'zip'}

def allowed_file_excel(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_EXCEL

def allowed_file_zip(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ZIP

@app.route('/')
def index():
    # Clear session data when returning to the home page
    if 'excel_data' in session:
        session.pop('excel_data')
    if 'zip_file' in session:
        session.pop('zip_file')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    # Check if files are present in the request
    if 'excel_file' not in request.files or 'zip_file' not in request.files:
        flash('Both Excel and ZIP files are required', 'danger')
        return redirect(request.url)
    
    excel_file = request.files['excel_file']
    zip_file = request.files['zip_file']
    
    # Check if filenames are empty
    if excel_file.filename == '' or zip_file.filename == '':
        flash('Both Excel and ZIP files are required', 'danger')
        return redirect(request.url)
    
    # Check file types
    if not allowed_file_excel(excel_file.filename):
        flash('Invalid Excel file format. Please upload .xlsx or .xls files.', 'danger')
        return redirect(request.url)
    
    if not allowed_file_zip(zip_file.filename):
        flash('Invalid ZIP file format. Please upload .zip files.', 'danger')
        return redirect(request.url)
    
    # Process Excel file
    try:
        # Read Excel into DataFrame
        df = pd.read_excel(excel_file)
        # Convert DataFrame to dict and store in session
        excel_data = df.to_dict(orient='records')
        session['excel_data'] = excel_data
        
        # Store the ZIP file in memory
        zip_content = zip_file.read()
        zip_io = io.BytesIO(zip_content)
        session['zip_file'] = zip_io.getvalue()
        
        flash('Files uploaded successfully! You can now search for a student by ID.', 'success')
        return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        flash(f'Error processing files: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search_student():
    student_id = request.form.get('student_id')
    
    if not student_id:
        flash('Please enter a Student ID', 'warning')
        return redirect(url_for('index'))
    
    # Check if excel data exists in session
    if 'excel_data' not in session:
        flash('Please upload the Excel file first', 'warning')
        return redirect(url_for('index'))
    
    excel_data = session['excel_data']
    
    # Search for student in the excel data
    found_student = None
    for student in excel_data:
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
    if 'found_student' not in session or 'zip_file' not in session:
        flash('Missing required data. Please start over.', 'danger')
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
    
    # Load zip file from session
    zip_bytes = session.get('zip_file')
    zip_io = io.BytesIO(zip_bytes)
    
    try:
        # Open the zip file
        with zipfile.ZipFile(zip_io, 'r') as zip_ref:
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
