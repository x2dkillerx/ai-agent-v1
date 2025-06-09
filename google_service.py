"""
Google Service Module for Clinic Voice AI

This module provides Google integration services for the Clinic Voice AI.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock implementation for testing
def mock_google_integration():
    """
    Mock Google integration for testing without API calls
    
    Returns:
        Mock GoogleIntegration object
    """
    class MockGoogleIntegration:
        def log_appointment_to_sheets(self, appointment_data):
            logger.info(f"Mock: Logging appointment to Sheets: {appointment_data}")
            return True
            
        def create_calendar_event(self, appointment_data):
            logger.info(f"Mock: Creating calendar event: {appointment_data}")
            return "mock_event_id_12345"
            
        def check_availability(self, service, preferred_time):
            logger.info(f"Mock: Checking availability for {service} at {preferred_time}")
            return True
            
        def suggest_alternative_time(self, service, preferred_time):
            suggestion = "tomorrow at 10:30 AM"
            logger.info(f"Mock: Suggesting alternative time for {service}: {suggestion}")
            return suggestion
    
    return MockGoogleIntegration()

# Initialize Google services
def initialize_google_services():
    """Initialize Google services"""
    logger.info("Mock: Initializing Google services")
    return True
