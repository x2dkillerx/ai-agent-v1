"""
Google Integration Module for Clinic Voice AI

This module handles integration with Google services:
1. Google Sheets for appointment logging
2. Google Calendar for appointment scheduling
3. Authentication and credential management
"""

import os
import json
import logging
from datetime import datetime, timedelta
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define scopes needed for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/calendar'
]

# In a production environment, these would be environment variables
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
GOOGLE_TOKEN_FILE = 'token.pickle'
SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
CALENDAR_ID = 'primary'  # Use 'primary' for the user's primary calendar

class GoogleIntegration:
    """Class to handle Google Sheets and Calendar integration"""
    
    def __init__(self ):
        """Initialize Google API clients"""
        self.creds = self._get_credentials()
        self.sheets_service = None
        self.calendar_service = None
        
        if self.creds:
            self.sheets_service = build('sheets', 'v4', credentials=self.creds)
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
    
    def _get_credentials(self):
        """Get Google API credentials"""
        creds = None
        
        # Check if token file exists
        if os.path.exists(GOOGLE_TOKEN_FILE):
            with open(GOOGLE_TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for future use
            with open(GOOGLE_TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def log_appointment_to_sheets(self, appointment_data):
        """
        Log appointment details to Google Sheets
        
        Args:
            appointment_data: Dictionary containing appointment details
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.sheets_service:
                logger.error("Sheets service not initialized")
                return False
            
            # Format data for Sheets
            row_data = [
                appointment_data.get('timestamp', datetime.now().isoformat()),
                appointment_data.get('patient_name', ''),
                appointment_data.get('service', ''),
                appointment_data.get('scheduled_time', ''),
                appointment_data.get('phone_number', '')
            ]
            
            # Append row to sheet
            result = self.sheets_service.spreadsheets().values().append(
                spreadsheetId=SPREADSHEET_ID,
                range='Appointments!A:E',
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={'values': [row_data]}
            ).execute()
            
            logger.info(f"Appointment logged to Google Sheets: {result.get('updates').get('updatedRange')}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging appointment to Sheets: {str(e)}")
            return False
    
    def create_calendar_event(self, appointment_data):
        """
        Create a calendar event for the appointment
        
        Args:
            appointment_data: Dictionary containing appointment details
            
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            if not self.calendar_service:
                logger.error("Calendar service not initialized")
                return None
            
            # Parse appointment time
            # In production, this would use a proper datetime parser
            # For demo, we'll use a simple approach
            scheduled_time = appointment_data.get('scheduled_time', '')
            
            # Mock time parsing for demo
            # In production, use a proper datetime parser
            start_time = datetime.now() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)
            
            # Create event
            event = {
                'summary': f"{appointment_data.get('service', 'Medical')} Appointment - {appointment_data.get('patient_name', 'Patient')}",
                'description': f"Patient: {appointment_data.get('patient_name', '')}\nService: {appointment_data.get('service', '')}\nPhone: {appointment_data.get('phone_number', '')}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Los_Angeles',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Los_Angeles',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 60},
                    ],
                },
            }
            
            # Add event to calendar
            event = self.calendar_service.events().insert(
                calendarId=CALENDAR_ID,
                body=event
            ).execute()
            
            logger.info(f"Calendar event created: {event.get('htmlLink')}")
            return event.get('id')
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return None
    
    def check_availability(self, service, preferred_time):
        """
        Check if a time slot is available in the calendar
        
        Args:
            service: Type of service requested
            preferred_time: Preferred appointment time
            
        Returns:
            True if available, False otherwise
        """
        try:
            if not self.calendar_service:
                logger.error("Calendar service not initialized")
                return False
            
            # Parse preferred time
            # In production, this would use a proper datetime parser
            # For demo, we'll use a simple approach
            
            # Mock time parsing for demo
            # In production, use a proper datetime parser
            start_time = datetime.now() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)
            
            # Check for conflicting events
            events_result = self.calendar_service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # If no events, time slot is available
            return len(events) == 0
            
        except Exception as e:
            logger.error(f"Error checking availability: {str(e)}")
            return False
    
    def suggest_alternative_time(self, service, preferred_time):
        """
        Suggest an alternative time slot based on calendar availability
        
        Args:
            service: Type of service requested
            preferred_time: Preferred appointment time
            
        Returns:
            Alternative time slot as string
        """
        try:
            if not self.calendar_service:
                logger.error("Calendar service not initialized")
                return "tomorrow at 10:00 AM"  # Default fallback
            
            # Parse preferred time
            # In production, this would use a proper datetime parser
            # For demo, we'll use a simple approach
            
            # Mock time parsing for demo
            # In production, use a proper datetime parser
            start_time = datetime.now() + timedelta(days=1)
            
            # Look for available slots in the next 3 days
            for days in range(1, 4):
                for hour in [9, 10, 11, 13, 14, 15, 16]:
                    check_time = start_time + timedelta(days=days)
                    check_time = check_time.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    end_time = check_time + timedelta(hours=1)
                    
                    # Check for conflicting events
                    events_result = self.calendar_service.events().list(
                        calendarId=CALENDAR_ID,
                        timeMin=check_time.isoformat() + 'Z',
                        timeMax=end_time.isoformat() + 'Z',
                        singleEvents=True,
                        orderBy='startTime'
                    ).execute()
                    
                    events = events_result.get('items', [])
                    
                    # If no events, time slot is available
                    if len(events) == 0:
                        # Format time for response
                        day_str = "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days"
                        hour_str = f"{hour}:00 AM" if hour < 12 else f"{hour-12}:00 PM"
                        return f"{day_str} at {hour_str}"
            
            # If no slots found, return a default
            return "next Monday at 9:00 AM"
            
        except Exception as e:
            logger.error(f"Error suggesting alternative time: {str(e)}")
            return "tomorrow at 10:00 AM"  # Default fallback

# For demo/testing purposes
def mock_google_integration():
    """
    Mock Google integration for testing without API calls
    
    Returns:
        Mock GoogleIntegration object
    """
    class MockGoogleIntegration:
        def log_appointment_to_sheets(self, appointment_data):
            logger.info(f"Mock: Logging appointment to Sheets: {json.dumps(appointment_data)}")
            return True
            
        def create_calendar_event(self, appointment_data):
            logger.info(f"Mock: Creating calendar event: {json.dumps(appointment_data)}")
            return "mock_event_id_12345"
            
        def check_availability(self, service, preferred_time):
            import random
            available = random.random() > 0.3
            logger.info(f"Mock: Checking availability for {service} at {preferred_time}: {available}")
            return available
            
        def suggest_alternative_time(self, service, preferred_time):
            if 'am' in preferred_time.lower():
                suggestion = "tomorrow at 2:00 PM"
            else:
                suggestion = "tomorrow at 10:30 AM"
            logger.info(f"Mock: Suggesting alternative time for {service}: {suggestion}")
            return suggestion
    
    return MockGoogleIntegration()

# Create a setup function to initialize Google Sheets
def setup_google_sheets():
    """
    Set up Google Sheets for appointment logging
    
    Creates the appointment tracking spreadsheet if it doesn't exist
    """
    try:
        google = GoogleIntegration()
        
        if not google.sheets_service:
            logger.error("Sheets service not initialized")
            return False
        
        # Check if spreadsheet exists
        try:
            google.sheets_service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
            logger.info(f"Spreadsheet exists: {SPREADSHEET_ID}")
            
            # Make sure the Appointments sheet exists with headers
            result = google.sheets_service.spreadsheets().values().get(
                spreadsheetId=SPREADSHEET_ID,
                range='Appointments!A1:E1'
            ).execute()
            
            # If no values, add headers
            if 'values' not in result:
                headers = [
                    'Timestamp',
                    'Patient Name',
                    'Service',
                    'Scheduled Time',
                    'Phone Number'
                ]
                
                google.sheets_service.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range='Appointments!A1:E1',
                    valueInputOption='RAW',
                    body={'values': [headers]}
                ).execute()
                
                logger.info("Added headers to Appointments sheet")
            
        except Exception:
            # Spreadsheet doesn't exist, create it
            spreadsheet = {
                'properties': {
                    'title': 'Clinic Voice AI - Appointment Tracking'
                },
                'sheets': [
                    {
                        'properties': {
                            'title': 'Appointments',
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 5
                            }
                        }
                    }
                ]
            }
            
            spreadsheet = google.sheets_service.spreadsheets().create(
                body=spreadsheet
            ).execute()
            
            # Update the spreadsheet ID
            global SPREADSHEET_ID
            SPREADSHEET_ID = spreadsheet.get('spreadsheetId')
            
            logger.info(f"Created new spreadsheet: {SPREADSHEET_ID}")
            
            # Add headers
            headers = [
                'Timestamp',
                'Patient Name',
                'Service',
                'Scheduled Time',
                'Phone Number'
            ]
            
            google.sheets_service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range='Appointments!A1:E1',
                valueInputOption='RAW',
                body={'values': [headers]}
            ).execute()
            
            logger.info("Added headers to Appointments sheet")
        
        return True
        
    except Exception as e:
        logger.error(f"Error setting up Google Sheets: {str(e)}")
        return False
