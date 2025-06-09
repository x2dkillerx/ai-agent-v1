"""
Twilio Integration Module for Clinic Voice AI

This module handles the integration with Twilio for:
1. Receiving and managing incoming phone calls
2. Processing audio streams for speech recognition
3. Generating TwiML responses
4. Sending SMS confirmations
"""

from flask import request, Response
import os
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import logging
import json
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a production environment, these would be environment variables
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "YOUR_TWILIO_PHONE_NUMBER"

# Initialize Twilio client
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# In-memory session storage (would be a database in production)
call_sessions = {}

def register_twilio_routes(app, conversation_handler):
    """Register Twilio webhook routes with the Flask app"""
    
    @app.route('/twilio/voice', methods=['POST'])
    def twilio_voice():
        """Handle incoming Twilio voice calls"""
        # Get call SID from Twilio request
        call_sid = request.values.get('CallSid')
        
        # Create a new session for this call
        session_id = str(uuid.uuid4())
        call_sessions[call_sid] = {
            'id': session_id,
            'call_sid': call_sid,
            'start_time': datetime.now().isoformat(),
            'conversation': [],
            'patient_info': {
                'name': None,
                'service': None,
                'preferred_time': None,
                'phone_number': request.values.get('From')
            },
            'state': 'greeting'
        }
        
        # Log the new call
        logger.info(f"New call received: {call_sid}, session: {session_id}")
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Add initial greeting message
        response.say(
            "Thank you for calling Noor Medical Clinic. This is Rachel speaking. How may I help you today?",
            voice="alice"  # In production, this would use ElevenLabs
        )
        
        # Start gathering speech input
        gather = Gather(
            input='speech',
            action='/twilio/gather',
            method='POST',
            speech_timeout='auto',
            language='en-US'
        )
        response.append(gather)
        
        # Update session state
        call_sessions[call_sid]['state'] = 'collect_name'
        call_sessions[call_sid]['conversation'].append({
            'role': 'system',
            'text': "Thank you for calling Noor Medical Clinic. This is Rachel speaking. How may I help you today?",
            'timestamp': datetime.now().isoformat()
        })
        
        return Response(str(response), mimetype='text/xml')
    
    @app.route('/twilio/gather', methods=['POST'])
    def twilio_gather():
        """Handle speech input from Twilio Gather"""
        # Get call SID and speech result from Twilio request
        call_sid = request.values.get('CallSid')
        speech_result = request.values.get('SpeechResult')
        
        # Check if we have a valid session
        if call_sid not in call_sessions:
            logger.error(f"No session found for call: {call_sid}")
            response = VoiceResponse()
            response.say("I'm sorry, there was an error with your call. Please try again later.")
            response.hangup()
            return Response(str(response), mimetype='text/xml')
        
        # Get the current session
        session = call_sessions[call_sid]
        
        # Log user input
        logger.info(f"Speech input for call {call_sid}: {speech_result}")
        session['conversation'].append({
            'role': 'user',
            'text': speech_result,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process the conversation using the handler
        # In production, this would use Whisper for better transcription and GPT-4 for conversation
        result = conversation_handler(session['id'], speech_result, session)
        
        # Create TwiML response
        response = VoiceResponse()
        
        # Add the response message
        response.say(result['text'], voice="alice")  # In production, this would use ElevenLabs
        
        # Log system response
        session['conversation'].append({
            'role': 'system',
            'text': result['text'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Update session state
        session['state'] = result['next_state']
        
        # If we're not ending the call, gather more speech
        if result['next_state'] != 'end_call':
            gather = Gather(
                input='speech',
                action='/twilio/gather',
                method='POST',
                speech_timeout='auto',
                language='en-US'
            )
            response.append(gather)
        else:
            # End the call after a delay
            response.pause(length=1)
            response.hangup()
        
        return Response(str(response), mimetype='text/xml')

def send_sms_confirmation(to_number, message):
    """Send SMS confirmation using Twilio"""
    try:
        # Validate phone number format
        if not to_number.startswith('+'):
            to_number = '+' + to_number
            
        # Send the message
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_number
        )
        
        logger.info(f"SMS sent to {to_number}: {message.sid}")
        return True, message.sid
        
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        return False, str(e)
