from flask import Flask, request, render_template, jsonify
import os
import json
import uuid
import logging
from datetime import datetime

# Initialize Flask app
# Use directories relative to this file so the app can run from the project root
app = Flask(__name__, template_folder='templates', static_folder='static')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for demo purposes
# In production, this would be a database
sessions = {}
appointments = []

@app.route('/')
def index():
    """Render the web demo interface"""
    return render_template('index.html')

@app.route('/api/start-call', methods=['POST'])
def start_call():
    """Initialize a new call session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'id': session_id,
        'start_time': datetime.now().isoformat(),
        'conversation': [],
        'patient_info': {
            'name': None,
            'service': None,
            'preferred_time': None,
            'phone_number': None
        },
        'state': 'greeting'
    }
    
    # Initial greeting message
    initial_response = {
        'text': "Thank you for calling Noor Medical Clinic. This is Rachel speaking. How may I help you today?",
        'next_state': 'collect_name'
    }
    
    sessions[session_id]['conversation'].append({
        'role': 'system',
        'text': initial_response['text'],
        'timestamp': datetime.now().isoformat()
    })
    
    sessions[session_id]['state'] = initial_response['next_state']
    
    return jsonify({
        'session_id': session_id,
        'message': initial_response['text']
    })

@app.route('/api/process-speech', methods=['POST'])
def process_speech():
    """Process transcribed speech from the caller"""
    data = request.json
    session_id = data.get('session_id')
    transcript = data.get('transcript')
    
    if not session_id or not transcript or session_id not in sessions:
        return jsonify({'error': 'Invalid session or missing transcript'}), 400
    
    # Log user input
    sessions[session_id]['conversation'].append({
        'role': 'user',
        'text': transcript,
        'timestamp': datetime.now().isoformat()
    })
    
    # Process the input based on current state
    response = process_conversation(session_id, transcript)
    
    # Log system response
    sessions[session_id]['conversation'].append({
        'role': 'system',
        'text': response['text'],
        'timestamp': datetime.now().isoformat()
    })
    
    # Update session state
    sessions[session_id]['state'] = response['next_state']
    
    return jsonify({
        'message': response['text'],
        'state': response['next_state'],
        'session_id': session_id
    })

def process_conversation(session_id, transcript):
    """Process user input based on conversation state"""
    session = sessions[session_id]
    current_state = session['state']
    patient_info = session['patient_info']
    
    # This is a simplified state machine
    # In production, this would use GPT-4 for more natural conversation
    
    if current_state == 'collect_name':
        # Extract name from transcript
        # In production, use GPT-4 for better name extraction
        patient_info['name'] = transcript.strip()
        
        return {
            'text': f"Thank you, {patient_info['name']}. What service are you looking to book today? For example, dental, ENT, dermatology, or general checkup?",
            'next_state': 'collect_service'
        }
        
    elif current_state == 'collect_service':
        # Extract service from transcript
        patient_info['service'] = transcript.strip()
        
        return {
            'text': f"Great, I have you down for {patient_info['service']}. What date and time would you prefer for your appointment?",
            'next_state': 'collect_time'
        }
        
    elif current_state == 'collect_time':
        # Extract preferred time
        # In production, use GPT-4 for better time/date extraction
        patient_info['preferred_time'] = transcript.strip()
        
        # Check availability (mock implementation)
        is_available = check_availability(patient_info['service'], patient_info['preferred_time'])
        
        if is_available:
            return {
                'text': f"Perfect! I can book you for {patient_info['preferred_time']}. Could I get your phone number for a confirmation SMS?",
                'next_state': 'collect_phone'
            }
        else:
            # Suggest alternative time (mock implementation)
            alternative_time = suggest_alternative(patient_info['service'], patient_info['preferred_time'])
            return {
                'text': f"I'm sorry, but {patient_info['preferred_time']} is not available. We do have an opening at {alternative_time}. Would that work for you?",
                'next_state': 'confirm_alternative_time'
            }
            
    elif current_state == 'confirm_alternative_time':
        # Check if user accepts alternative time
        if 'yes' in transcript.lower() or 'sure' in transcript.lower() or 'okay' in transcript.lower():
            # Update preferred time with the alternative
            patient_info['preferred_time'] = suggest_alternative(patient_info['service'], patient_info['preferred_time'])
            
            return {
                'text': f"Great! I've booked you for {patient_info['preferred_time']}. Could I get your phone number for a confirmation SMS?",
                'next_state': 'collect_phone'
            }
        else:
            # Suggest another alternative
            alternative_time = suggest_alternative(patient_info['service'], patient_info['preferred_time'], second_try=True)
            return {
                'text': f"I understand. We also have an opening at {alternative_time}. Would that work better for you?",
                'next_state': 'confirm_alternative_time'
            }
            
    elif current_state == 'collect_phone':
        # Extract phone number
        patient_info['phone_number'] = transcript.strip()
        
        # Book the appointment (mock implementation)
        book_appointment(patient_info)
        
        return {
            'text': f"Thank you! I've booked your {patient_info['service']} appointment for {patient_info['preferred_time']}. You'll receive a confirmation SMS shortly at {patient_info['phone_number']}. Is there anything else I can help you with today?",
            'next_state': 'closing'
        }
        
    elif current_state == 'closing':
        if 'yes' in transcript.lower():
            return {
                'text': "What else can I help you with today?",
                'next_state': 'new_request'
            }
        else:
            return {
                'text': "Thank you for calling Noor Medical Clinic. Have a great day!",
                'next_state': 'end_call'
            }
            
    else:
        # Default response for unhandled states
        return {
            'text': "I'm sorry, I didn't quite catch that. Could you please repeat?",
            'next_state': current_state
        }

def check_availability(service, preferred_time):
    """Mock function to check appointment availability"""
    # In production, this would check Google Calendar
    # For demo, return True 70% of the time
    import random
    return random.random() > 0.3

def suggest_alternative(service, preferred_time, second_try=False):
    """Mock function to suggest alternative appointment times"""
    # In production, this would check Google Calendar for actual availability
    if 'am' in preferred_time.lower():
        return "2:00 PM tomorrow" if second_try else "3:30 PM today"
    else:
        return "10:30 AM tomorrow" if second_try else "9:15 AM tomorrow"

def book_appointment(patient_info):
    """Mock function to book an appointment"""
    # In production, this would:
    # 1. Add to Google Calendar
    # 2. Log to Google Sheets
    # 3. Send SMS confirmation
    
    # For demo, just add to in-memory list
    appointment = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'patient_name': patient_info['name'],
        'service': patient_info['service'],
        'scheduled_time': patient_info['preferred_time'],
        'phone_number': patient_info['phone_number']
    }
    
    appointments.append(appointment)
    logger.info(f"Booked appointment: {json.dumps(appointment)}")
    return appointment

@app.route('/api/get-conversation', methods=['GET'])
def get_conversation():
    """Get the full conversation history for a session"""
    session_id = request.args.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'}), 400
        
    return jsonify({
        'conversation': sessions[session_id]['conversation'],
        'patient_info': sessions[session_id]['patient_info'],
        'state': sessions[session_id]['state']
    })

@app.route('/api/get-appointments', methods=['GET'])
def get_appointments():
    """Get all booked appointments (for demo purposes)"""
    return jsonify(appointments)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
