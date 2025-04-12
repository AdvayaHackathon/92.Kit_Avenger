from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from tensorflow.keras.models import load_model
import uuid

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Load AI model (placeholder - in a real app, you'd have a trained model)
# model = load_model('wound_care_model.h5')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Mock database (in a real app, use a proper database)
patients = {
    'patient1': {
        'name': 'John Doe',
        'surgery_type': 'Knee Replacement',
        'surgery_date': '2023-05-15',
        'doctor': 'Dr. Smith',
        'medications': [
            {'id': 'med1', 'name': 'Ibuprofen', 'dosage': '200mg', 'frequency': 'Every 8 hours', 'instructions': 'Take with food'},
            {'id': 'med2', 'name': 'Antibiotic', 'dosage': '500mg', 'frequency': 'Twice daily', 'instructions': 'Complete full course'}
        ],
        'appointments': [
            {'id': 'appt1', 'doctor': 'Dr. Smith', 'date': '2023-05-22', 'time': '10:00', 'purpose': 'Post-op checkup'},
            {'id': 'appt2', 'doctor': 'Dr. Smith', 'date': '2023-06-05', 'time': '14:30', 'purpose': 'Follow-up'}
        ],
        'progress': [
            {'date': '2023-05-16', 'pain_level': 6, 'mobility_score': 2, 'notes': 'First day after surgery, significant pain'},
            {'date': '2023-05-20', 'pain_level': 4, 'mobility_score': 4, 'notes': 'Pain improving, starting to walk with crutches'}
        ]
    }
}

@app.route('/')
def home():
    return render_template('dashboard.html', patient=patients['patient1'])

@app.route('/dashboard')
def dashboard():
    # Calculate next medication time
    patient = patients['patient1']
    now = datetime.now()
    
    # Find next medication
    next_med = None
    for med in patient['medications']:
        # Simplified logic - in real app would use actual schedule
        next_med = med
        break
    
    # Find next appointment
    next_appt = None
    for appt in patient['appointments']:
        appt_datetime = datetime.strptime(f"{appt['date']} {appt['time']}", "%Y-%m-%d %H:%M")
        if appt_datetime > now:
            next_appt = appt
            break
    
    return render_template('dashboard.html', 
                         patient=patient,
                         next_med=next_med,
                         next_appt=next_appt)

@app.route('/medication')
def medication():
    return render_template('medication.html', medications=patients['patient1']['medications'])

@app.route('/appointments')
def appointments():
    return render_template('appointments.html', appointments=patients['patient1']['appointments'])

@app.route('/wound-care', methods=['GET', 'POST'])
def wound_care():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'woundImage' not in request.files:
            return render_template('wound_care.html', error="No file selected")
        
        file = request.files['woundImage']
        
        if file.filename == '':
            return render_template('wound_care.html', error="No file selected")
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            
            # Process image with AI (simplified)
            img = cv2.imread(save_path)
            
            # In a real app, you would:
            # 1. Preprocess the image
            # 2. Run it through your model
            # 3. Generate suggestions
            
            # Mock AI analysis
            suggestions = [
                "Wound appears to be healing normally",
                "Slight redness detected - monitor for infection",
                "Keep the area clean and dry",
                "Change dressing every 24 hours",
                "Avoid strenuous activity that might stress the wound"
            ]
            
            return render_template('wound_care.html', 
                                image_url=f"uploads/{unique_filename}",
                                suggestions=suggestions)
    
    return render_template('wound_care.html')

@app.route('/progress')
def progress():
    return render_template('progress.html', progress=patients['patient1']['progress'])

@app.route('/api/add_progress_entry', methods=['POST'])
def add_progress_entry():
    data = request.json
    new_entry = {
        'date': datetime.now().strftime("%Y-%m-%d"),
        'pain_level': data['painLevel'],
        'mobility_score': data['mobilityScore'],
        'notes': data.get('notes', '')
    }
    
    # In a real app, save to database
    patients['patient1']['progress'].append(new_entry)
    
    return jsonify(success=True, entry=new_entry)

@app.route('/api/analyze_wound', methods=['POST'])
def analyze_wound():
    # In a real app, this would process the image with AI
    # For demo, return mock suggestions
    suggestions = [
        "Wound shows signs of normal healing",
        "No visible signs of infection detected",
        "Recommend changing dressing daily",
        "Keep wound dry for next 48 hours"
    ]
    
    return jsonify(success=True, suggestions=suggestions)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)