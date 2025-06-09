"""
SMS Confirmation Module for Clinic Voice AI

This module handles SMS confirmation using Twilio:
1. Generating confirmation messages
2. Sending SMS notifications
3. Handling delivery status
"""

import os
import logging
from twilio.rest import Client
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a production environment, these would be environment variables
TWILIO_ACCOUNT_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_PHONE_NUMBER = "YOUR_TWILIO_PHONE_NUMBER"

# Initialize Twilio client
try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
except Exception as e:
    logger.error(f"Error initializing Twilio client: {str(e)}")
    client = None

def generate_confirmation_message(appointment_data):
    """
    Generate a confirmation message for an appointment
    
    Args:
        appointment_data: Dictionary containing appointment details
        
    Returns:
        Formatted confirmation message
    """
    try:
        patient_name = appointment_data.get('patient_name', 'Patient')
        service = appointment_data.get('service', 'medical')
        scheduled_time = appointment_data.get('scheduled_time', 'your scheduled time')
        
        message = (
            f"Hello {patient_name}, your {service} appointment at Noor Medical Clinic "
            f"is confirmed for {scheduled_time}. Please arrive 15 minutes early. "
            f"Call 555-123-4567 if you need to reschedule."
        )
        
        return message
        
    except Exception as e:
        logger.error(f"Error generating confirmation message: {str(e)}")
        return "Your appointment at Noor Medical Clinic has been confirmed. Please call 555-123-4567 for any questions."

def send_sms_confirmation(to_number, message=None, appointment_data=None):
    """
    Send SMS confirmation using Twilio
    
    Args:
        to_number: Recipient phone number
        message: Optional pre-formatted message
        appointment_data: Optional appointment data to generate message
        
    Returns:
        Tuple of (success, message_id or error)
    """
    try:
        if not client:
            logger.error("Twilio client not initialized")
            return False, "Twilio client not initialized"
        
        # Validate phone number format
        if not to_number.startswith('+'):
            to_number = '+' + to_number
        
        # Generate message if not provided
        if not message and appointment_data:
            message = generate_confirmation_message(appointment_data)
        elif not message:
            logger.error("No message or appointment data provided")
            return False, "No message or appointment data provided"
        
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

def check_sms_status(message_sid):
    """
    Check the delivery status of an SMS
    
    Args:
        message_sid: Twilio message SID
        
    Returns:
        Message status
    """
    try:
        if not client:
            logger.error("Twilio client not initialized")
            return "unknown"
        
        message = client.messages(message_sid).fetch()
        return message.status
        
    except Exception as e:
        logger.error(f"Error checking SMS status: {str(e)}")
        return "unknown"

# For demo/testing purposes
def mock_send_sms(to_number, message=None, appointment_data=None):
    """
    Mock SMS sending for testing without API calls
    
    Returns:
        Success message for testing
    """
    # Generate message if not provided
    if not message and appointment_data:
        message = generate_confirmation_message(appointment_data)
    elif not message:
        message = "Your appointment at Noor Medical Clinic has been confirmed."
    
    logger.info(f"Mock: SMS to {to_number}: {message}")
    return True, f"mock_message_sid_{datetime.now().strftime('%Y%m%d%H%M%S')}"
