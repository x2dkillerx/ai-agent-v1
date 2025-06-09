from flask import Flask, render_template, request, jsonify
import logging
import random
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# In-memory storage for demo purposes
sessions = {}
appointments = []

@app.route('/')
def index():
    """Render the web demo interface"""
    return render_template('index.html')

@app.route('/api/start-call', methods=['POST'])
def start_call():
    """Initialize a new call session"""
    session_id = str(random.randint(10000, 99999))
    sessions[session_id] = {
        'state': 'greeting',
        'patient_info': {}
    }
    
    return jsonify({
        'session_id': session_id,
        'text': "Hello, thank you for calling Noor Medical Clinic. This is Rachel speaking. How can I help you today?",
        'next_state': 'collect_name'
    })

@app.route('/api/process-speech', methods=['POST'])
def process_speech():
    """Process transcribed speech from the user"""
    data = request.json
    session_id = data.get('session_id')
    transcript = data.get('transcript', '').strip()
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    session = sessions[session_id]
    current_state = session.get('state', 'greeting')
    patient_info = session.get('patient_info', {})
    
    # Process based on current state
    if current_state == 'collect_name':
        # Extract name from transcript
        patient_info['name'] = transcript
        
        return jsonify({
            'text': f"Thank you, {patient_info['name']}. What service are you looking to book? For example, dental, ENT, dermatology, or general checkup?",
            'next_state': 'collect_service'
        })
        
    elif current_state == 'collect_service':
        # Extract service from transcript
        patient_info['service'] = transcript
        
        return jsonify({
            'text': f"Great, I can help you book a {patient_info['service']} appointment. What day and time would you prefer?",
            'next_state': 'collect_time'
        })
        
    elif current_state == 'collect_time':
        # Extract preferred time from transcript
        patient_info['preferred_time'] = transcript
        
        # Check availability (mock implementation)
        is_available = random.choice([True, False])
        
        if is_available:
            return jsonify({
                'text': f"Perfect! I can book you for {patient_info['preferred_time']}. Could I get your phone number for confirmation?",
                'next_state': 'collect_phone'
            })
        else:
            alternative_time = "tomorrow at 10:30 AM" if "morning" in transcript.lower() else "tomorrow at 2:00 PM"
            patient_info['alternative_time'] = alternative_time
            
            return jsonify({
                'text': f"I'm sorry, but {patient_info['preferred_time']} is not available. We do have an opening {alternative_time}. Would that work for you?",
                'next_state': 'confirm_alternative_time'
            })
            
    elif current_state == 'confirm_alternative_time':
        # Check if user accepts alternative time
        if 'yes' in transcript.lower() or 'sure' in transcript.lower() or 'okay' in transcript.lower():
            # Update preferred time with the alternative
            patient_info['preferred_time'] = patient_info['alternative_time']
            
            return jsonify({
                'text': f"Great! I've booked you for {patient_info['preferred_time']}. Could I get your phone number for a confirmation?",
                'next_state': 'collect_phone'
            })
        else:
            # Suggest another time
            new_alternative = "Thursday at 11:00 AM" if "afternoon" in patient_info['alternative_time'].lower() else "Thursday at 3:00 PM"
            patient_info['alternative_time'] = new_alternative
            
            return jsonify({
                'text': f"I understand. We also have availability on {new_alternative}. Would that work better for you?",
                'next_state': 'confirm_alternative_time'
            })
            
    elif current_state == 'collect_phone':
        # Extract phone number from transcript
        patient_info['phone'] = transcript
        
        # Save appointment
        appointment = {
            'patient_name': patient_info['name'],
            'service': patient_info['service'],
            'scheduled_time': patient_info['preferred_time'],
            'phone_number': patient_info['phone'],
            'timestamp': 'now'
        }
        
        appointments.append(appointment)
        
        # Mock logging to Google Sheets and Calendar
        logger.info(f"Mock: Appointment logged to Google Sheets: {json.dumps(appointment)}")
        logger.info(f"Mock: Calendar event created: {json.dumps(appointment)}")
        
        return jsonify({
            'text': f"Perfect! I've booked your {patient_info['service']} appointment for {patient_info['preferred_time']}. You'll receive an SMS confirmation at {patient_info['phone']}. Is there anything else you need help with today?",
            'next_state': 'confirm_complete'
        })
        
    elif current_state == 'confirm_complete':
        return jsonify({
            'text': "Thank you for calling Noor Medical Clinic. We look forward to seeing you at your appointment. Have a great day!",
            'next_state': 'end_call'
        })
        
    else:
        return jsonify({
            'text': "I'm sorry, I didn't understand that. Could you please repeat?",
            'next_state': current_state
        })
    
    # Update session
    session['state'] = current_state
    session['patient_info'] = patient_info
    sessions[session_id] = session

@app.route('/api/get-appointments', methods=['GET'])
def get_appointments():
    """Get all booked appointments"""
    return jsonify(appointments)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
