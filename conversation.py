"""
Conversation Management Module for Clinic Voice AI

This module handles the conversation flow using GPT-4:
1. Understanding user intent
2. Extracting relevant information
3. Managing conversation state
4. Generating appropriate responses
"""

import os
import logging
import json
import re
from datetime import datetime, timedelta
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a production environment, this would be an environment variable
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

# System prompt for GPT-4
SYSTEM_PROMPT = """
You are Rachel, a friendly and professional AI receptionist for Noor Medical Clinic.
Your job is to help patients schedule appointments by collecting their information in a natural, conversational way.

You need to collect the following information:
1. Patient's full name
2. The medical service they need (e.g., dental, ENT, dermatology, general checkup)
3. Their preferred appointment date and time

If their preferred time is not available, suggest an alternative.
Once all information is collected, confirm the appointment details.

Keep your responses concise, warm, and professional. Speak naturally as a helpful receptionist would.
"""

def extract_entities(text):
    """
    Extract relevant entities from user input using GPT-4
    
    Args:
        text: User input text
        
    Returns:
        Dictionary of extracted entities
    """
    try:
        prompt = f"""
        Extract the following information from this patient's statement, if present:
        - Patient name
        - Medical service requested
        - Preferred appointment date and time
        - Phone number
        
        Patient statement: "{text}"
        
        Format your response as a JSON object with these fields: name, service, datetime, phone
        If any field is not present in the statement, set its value to null.
        Only respond with the JSON object, nothing else.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You extract structured information from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from the response (in case there's any extra text)
        json_match = re.search(r'({.*})', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
            
        entities = json.loads(content)
        return entities
        
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        return {
            "name": None,
            "service": None,
            "datetime": None,
            "phone": None
        }

def generate_response(conversation_history, current_state, patient_info):
    """
    Generate a response using GPT-4 based on conversation history and state
    
    Args:
        conversation_history: List of conversation messages
        current_state: Current conversation state
        patient_info: Dictionary of collected patient information
        
    Returns:
        Generated response text and next state
    """
    try:
        # Format conversation history for GPT-4
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Add conversation context
        context = f"""
        Current conversation state: {current_state}
        
        Patient information collected so far:
        - Name: {patient_info.get('name') or 'Not provided'}
        - Service requested: {patient_info.get('service') or 'Not provided'}
        - Preferred time: {patient_info.get('preferred_time') or 'Not provided'}
        - Phone number: {patient_info.get('phone_number') or 'Not provided'}
        
        Based on the conversation state and collected information, respond appropriately to collect missing information or confirm the appointment.
        """
        
        messages.append({"role": "user", "content": context})
        
        # Add conversation history
        for message in conversation_history[-5:]:  # Only use the last 5 messages for context
            role = "assistant" if message["role"] == "system" else "user"
            messages.append({"role": role, "content": message["text"]})
        
        # Generate response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        
        # Get the generated text
        generated_text = response.choices[0].message.content.strip()
        
        # Determine next state based on current state and generated text
        next_state = determine_next_state(current_state, generated_text, patient_info)
        
        return {
            "text": generated_text,
            "next_state": next_state
        }
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return {
            "text": "I'm sorry, I'm having trouble processing your request. Could you please repeat that?",
            "next_state": current_state
        }

def determine_next_state(current_state, response_text, patient_info):
    """
    Determine the next conversation state based on current state and response
    
    Args:
        current_state: Current conversation state
        response_text: Generated response text
        patient_info: Dictionary of collected patient information
        
    Returns:
        Next conversation state
    """
    # Check if all required information is collected
    all_info_collected = all([
        patient_info.get('name'),
        patient_info.get('service'),
        patient_info.get('preferred_time')
    ])
    
    # State transition logic
    if current_state == 'greeting':
        return 'collect_name'
        
    elif current_state == 'collect_name' and patient_info.get('name'):
        return 'collect_service'
        
    elif current_state == 'collect_service' and patient_info.get('service'):
        return 'collect_time'
        
    elif current_state == 'collect_time' and patient_info.get('preferred_time'):
        return 'collect_phone'
        
    elif current_state == 'collect_phone' and patient_info.get('phone_number'):
        return 'confirm_appointment'
        
    elif current_state == 'confirm_appointment' and all_info_collected:
        if "thank you" in response_text.lower() and "goodbye" in response_text.lower():
            return 'end_call'
        else:
            return 'closing'
            
    elif current_state == 'closing':
        return 'end_call'
        
    # Default: stay in current state
    return current_state

def process_conversation(session_id, transcript, session=None):
    """
    Process user input based on conversation state
    
    Args:
        session_id: Unique session identifier
        transcript: Transcribed user input
        session: Optional session object (for Twilio integration)
        
    Returns:
        Response object with text and next state
    """
    # For demo purposes, use a simplified state machine
    # In production, this would use the GPT-4 functions above
    
    # If session is provided (from Twilio), use it
    # Otherwise, use the global sessions dictionary from app.py
    if session:
        current_state = session['state']
        patient_info = session['patient_info']
        conversation = session['conversation']
    else:
        # Import here to avoid circular imports
        from app import sessions
        
        if session_id not in sessions:
            return {
                'text': "I'm sorry, there was an error with your session. Please try again.",
                'next_state': 'end_call'
            }
            
        current_state = sessions[session_id]['state']
        patient_info = sessions[session_id]['patient_info']
        conversation = sessions[session_id]['conversation']
    
    # Extract entities from transcript
    entities = extract_entities(transcript)
    
    # Update patient info with any extracted entities
    if entities.get('name'):
        patient_info['name'] = entities.get('name')
    
    if entities.get('service'):
        patient_info['service'] = entities.get('service')
    
    if entities.get('datetime'):
        patient_info['preferred_time'] = entities.get('datetime')
    
    if entities.get('phone'):
        patient_info['phone_number'] = entities.get('phone')
    
    # Generate response using GPT-4
    return generate_response(conversation, current_state, patient_info)

# For demo/testing purposes
def mock_process_conversation(session_id, transcript, session=None):
    """
    Mock conversation processing for testing without API calls
    
    Returns:
        Predefined responses for testing
    """
    # If session is provided (from Twilio), use it
    # Otherwise, use the global sessions dictionary from app.py
    if session:
        current_state = session['state']
        patient_info = session['patient_info']
    else:
        # Import here to avoid circular imports
        from app import sessions
        
        if session_id not in sessions:
            return {
                'text': "I'm sorry, there was an error with your session. Please try again.",
                'next_state': 'end_call'
            }
            
        current_state = sessions[session_id]['state']
        patient_info = sessions[session_id]['patient_info']
    
    # Simple state machine for demo purposes
    if current_state == 'collect_name':
        # Extract name from transcript
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
    
    # For demo, just log the appointment
    logger.info(f"Booked appointment: {json.dumps(patient_info)}")
    return True
