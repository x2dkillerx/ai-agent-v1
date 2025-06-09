"""
Updated main application with SMS confirmation integration
"""

from flask import Flask, request, render_template, jsonify, Response
import os
import json
import uuid
import logging
from datetime import datetime

# Import modules
from src.twilio_integration import register_twilio_routes
from src.speech_recognition import transcribe_web_audio, mock_transcribe
from src.conversation import process_conversation, mock_process_conversation
from src.text_to_speech import get_base64_audio, mock_synthesize_speech
from src.google_service import (
    initialize_google_services,
    log_appointment,
    create_calendar_event,
    check_availability,
    suggest_alternative_time
)
from src.sms_confirmation import send_sms_confirmation, mock_send_sms, generate_confirmation_message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# In-memory storage for demo purposes
# In production, this would be a database
sessions = {}
appointments = []

# Environment variables
DEBUG_MODE = True  # Set to False in production
USE_MOCK_SERVICES = True  # Set to False in production to use real APIs

# Initialize Google services
google_initialized = initialize_google_services()
if not google_initialized and not USE_MOCK_SERVICES:
    logger.warning("Failed to initialize Google services. Some features may not work correctly.")

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
    
    # Generate speech if not in mock mode
    audio_data = None
    if not USE_MOCK_SERVICES:
        audio_data = get_base64_audio(initial_response['text'])
    
    return jsonify({
        'session_id': session_id,
        'message': initial_response['text'],
        'audio': audio_data
    })

@app.route('/api/process-speech', methods=['POST'])
def process_speech():
    """Process transcribed speech from the caller"""
    data = request.json
    session_id = data.get('session_id')
    
    # Handle direct transcript or audio data
    if 'transcript' in data:
        transcript = data.get('transcript')
    elif 'audio' in data:
        # Process audio data through Whisper
        if USE_MOCK_SERVICES:
            transcript = mock_transcribe()
        else:
            transcript = transcribe_web_audio(data.get('audio'))
    else:
        return jsonify({'error': 'Missing transcript or audio data'}), 400
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    # Log user input
    sessions[session_id]['conversation'].append({
        'role': 'user',
        'text': transcript,
        'timestamp': datetime.now().isoformat()
    })
    
    # Process the input based on current state
    if USE_MOCK_SERVICES:
        response = mock_process_conversation(session_id, transcript)
    else:
        response = process_conversation(session_id, transcript)
    
    # Log system response
    sessions[session_id]['conversation'].append({
        'role': 'system',
        'text': response['text'],
        'timestamp': datetime.now().isoformat()
    })
    
    # Update session state
    sessions[session_id]['state'] = response['next_state']
    
    # If confirming appointment, book it
    if response['next_state'] == 'confirm_appointment' or response['next_state'] == 'closing':
        patient_info = sessions[session_id]['patient_info']
        if all([patient_info.get('name'), patient_info.get('service'), patient_info.get('preferred_time')]):
            book_appointment(patient_info)
    
    # Generate speech if not in mock mode
    audio_data = None
    if not USE_MOCK_SERVICES:
        audio_data = get_base64_audio(response['text'])
    
    return jsonify({
        'message': response['text'],
        'state': response['next_state'],
        'session_id': session_id,
        'audio': audio_data
    })

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

def book_appointment(patient_info):
    """Book an appointment and handle integrations"""
    # Create appointment record
    appointment = {
        'id': str(uuid.uuid4()),
        'timestamp': datetime.now().isoformat(),
        'patient_name': patient_info['name'],
        'service': patient_info['service'],
        'scheduled_time': patient_info['preferred_time'],
        'phone_number': patient_info['phone_number']
    }
    
    # Add to in-memory list
    appointments.append(appointment)
    
    # Log the appointment
    logger.info(f"Booked appointment: {json.dumps(appointment)}")
    
    # Log to Google Sheets
    sheets_result = log_appointment(appointment)
    if not sheets_result:
        logger.warning("Failed to log appointment to Google Sheets")
    
    # Add to Google Calendar
    calendar_result = create_calendar_event(appointment)
    if not calendar_result:
        logger.warning("Failed to create calendar event")
    
    # Send SMS confirmation if phone number is provided
    if patient_info['phone_number']:
        # Generate confirmation message
        message = generate_confirmation_message(appointment)
        
        # Send SMS
        if USE_MOCK_SERVICES:
            sms_result, sms_id = mock_send_sms(patient_info['phone_number'], message)
        else:
            sms_result, sms_id = send_sms_confirmation(patient_info['phone_number'], message)
        
        if not sms_result:
            logger.warning(f"Failed to send SMS confirmation: {sms_id}")
        else:
            logger.info(f"SMS confirmation sent: {sms_id}")
            
            # Add SMS ID to appointment record for status tracking
            appointment['sms_id'] = sms_id
    
    return appointment

def check_time_availability(service, preferred_time):
    """Check appointment availability"""
    # Use Google Calendar in production
    return check_availability(service, preferred_time)

def suggest_alternative_appointment_time(service, preferred_time, second_try=False):
    """Suggest alternative appointment times"""
    # Use Google Calendar in production
    return suggest_alternative_time(service, preferred_time)

# Register Twilio routes
register_twilio_routes(app, process_conversation if not USE_MOCK_SERVICES else mock_process_conversation)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=DEBUG_MODE)
