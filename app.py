from flask import Flask, request, jsonify, render_template
import os
from src.pdf_parser import process_pdf_schedule
from src.tasks_manager import authenticate_google_tasks, add_task_to_google_tasks, format_due_date_for_google_tasks
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Serve the main index page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_pdf():
    """Handle the uploaded PDF, process it, and add tasks to Google Calendar."""
    if 'pdf' not in request.files:
        return jsonify(success=False, message='No file part')
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify(success=False, message='No file selected')
    
    if file and file.filename.endswith('.pdf'):
        # Secure the filename and save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract course name from filename
        course_name = os.path.splitext(filename)[0]

        # Process the PDF to extract deadlines and exams
        deadlines, exams = process_pdf_schedule(file_path)

        # Authenticate Google Tasks API
        service = authenticate_google_tasks()

        # Add tasks to Google Calendar
        for deadline in deadlines:
            try:
                due_date_str = deadline.split('due on ')[-1]
                due_date = format_due_date_for_google_tasks(due_date_str)
                task_title = f"{course_name}: {deadline}"
                add_task_to_google_tasks(service, '@default', task_title, due_date)
            except Exception as e:
                print(f"Error scheduling task '{deadline}': {e}")

        # Add exams to Google Tasks
        for exam in exams:
            try:
                exam_date_str = exam.split('on ')[-1]
                exam_date = format_due_date_for_google_tasks(exam_date_str)
                exam_title = f"{course_name}: {exam}"
                add_task_to_google_tasks(service, '@default', exam_title, exam_date)
            except Exception as e:
                print(f"Error scheduling exam '{exam}': {e}")

        return jsonify(success=True, deadlines=deadlines, exams=exams)
    else:
        return jsonify(success=False, message='Invalid file type')

if __name__ == '__main__':
    app.run(debug=True)