"""
Test scenarios for Clinic Voice AI

This module contains test scenarios and utilities for validating the voice agent.
"""

import os
import logging
import json
import requests
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Basic appointment booking",
        "description": "Test basic flow of booking an appointment with all required information",
        "inputs": [
            "Hi, I'd like to schedule an appointment",
            "My name is John Smith",
            "I need to see a dentist",
            "Next Tuesday at 2 PM would work for me",
            "My phone number is 555-123-4567",
            "No, that's all I need. Thank you"
        ]
    },
    {
        "name": "Alternative time suggestion",
        "description": "Test flow when preferred time is unavailable and alternative is suggested",
        "inputs": [
            "Hello, I need to make an appointment",
            "Sarah Johnson",
            "I need a dermatology appointment",
            "Tomorrow at 10 AM",
            "Yes, that alternative time works for me",
            "My number is 555-987-6543",
            "That's all, thanks"
        ]
    },
    {
        "name": "Multiple service inquiry",
        "description": "Test handling multiple service inquiries in one call",
        "inputs": [
            "I'd like to book an appointment",
            "Michael Brown",
            "I need both a general checkup and an ENT consultation",
            "Let's do the general checkup first",
            "Friday afternoon, maybe around 3 PM",
            "555-246-8135",
            "Yes, I'd also like to schedule the ENT appointment",
            "Next Monday morning if possible",
            "That works fine",
            "No, that's everything. Thank you"
        ]
    }
]

def run_web_demo_test(scenario, base_url="http://localhost:5000"):
    """
    Run a test scenario against the web demo
    
    Args:
        scenario: Test scenario dictionary
        base_url: Base URL of the web demo
        
    Returns:
        Test results dictionary
    """
    try:
        logger.info(f"Running test scenario: {scenario['name']}")
        
        # Start a new call session
        start_response = requests.post(f"{base_url}/api/start-call")
        start_data = start_response.json()
        
        if 'session_id' not in start_data:
            logger.error("Failed to start call session")
            return {
                "success": False,
                "error": "Failed to start call session",
                "scenario": scenario['name']
            }
        
        session_id = start_data['session_id']
        conversation = [
            {
                "role": "system",
                "text": start_data['message']
            }
        ]
        
        # Process each input in the scenario
        for i, user_input in enumerate(scenario['inputs']):
            logger.info(f"Processing input {i+1}/{len(scenario['inputs'])}: {user_input}")
            
            # Send user input
            process_response = requests.post(
                f"{base_url}/api/process-speech",
                json={
                    "session_id": session_id,
                    "transcript": user_input
                }
            )
            
            process_data = process_response.json()
            
            if 'error' in process_data:
                logger.error(f"Error processing input: {process_data['error']}")
                return {
                    "success": False,
                    "error": f"Error processing input: {process_data['error']}",
                    "scenario": scenario['name'],
                    "conversation": conversation
                }
            
            # Add to conversation
            conversation.append({
                "role": "user",
                "text": user_input
            })
            
            conversation.append({
                "role": "system",
                "text": process_data['message']
            })
            
            # If end of call, break
            if process_data['state'] == 'end_call':
                logger.info("Call ended")
                break
            
            # Small delay to simulate real conversation
            time.sleep(1)
        
        # Get final conversation state
        final_response = requests.get(
            f"{base_url}/api/get-conversation",
            params={"session_id": session_id}
        )
        
        final_data = final_response.json()
        
        # Get appointments
        appointments_response = requests.get(f"{base_url}/api/get-appointments")
        appointments_data = appointments_response.json()
        
        return {
            "success": True,
            "scenario": scenario['name'],
            "conversation": conversation,
            "final_state": final_data.get('state'),
            "patient_info": final_data.get('patient_info'),
            "appointments": appointments_data
        }
        
    except Exception as e:
        logger.error(f"Error running test scenario: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "scenario": scenario['name']
        }

def run_all_tests(base_url="http://localhost:5000"):
    """
    Run all test scenarios
    
    Args:
        base_url: Base URL of the web demo
        
    Returns:
        List of test results
    """
    results = []
    
    for scenario in TEST_SCENARIOS:
        result = run_web_demo_test(scenario, base_url)
        results.append(result)
        
        # Small delay between tests
        time.sleep(2)
    
    return results

def generate_test_report(results):
    """
    Generate a test report from test results
    
    Args:
        results: List of test results
        
    Returns:
        Test report as string
    """
    report = "# Clinic Voice AI - Test Report\n\n"
    report += f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Summary
    success_count = sum(1 for r in results if r['success'])
    report += f"## Summary\n\n"
    report += f"- Total Tests: {len(results)}\n"
    report += f"- Successful: {success_count}\n"
    report += f"- Failed: {len(results) - success_count}\n\n"
    
    # Detailed results
    report += "## Detailed Results\n\n"
    
    for i, result in enumerate(results):
        report += f"### Test {i+1}: {result['scenario']}\n\n"
        report += f"- Status: {'Success' if result['success'] else 'Failed'}\n"
        
        if not result['success']:
            report += f"- Error: {result.get('error', 'Unknown error')}\n"
            
        if 'conversation' in result:
            report += "\n#### Conversation\n\n"
            for msg in result['conversation']:
                role = "AI" if msg['role'] == 'system' else "User"
                report += f"**{role}**: {msg['text']}\n\n"
        
        if 'patient_info' in result:
            report += "\n#### Patient Information\n\n"
            for key, value in result['patient_info'].items():
                report += f"- {key.replace('_', ' ').title()}: {value}\n"
            
        report += "\n"
    
    # Appointments
    if results and 'appointments' in results[-1]:
        report += "## Appointments\n\n"
        for appt in results[-1]['appointments']:
            report += f"- Patient: {appt.get('patient_name')}\n"
            report += f"  - Service: {appt.get('service')}\n"
            report += f"  - Time: {appt.get('scheduled_time')}\n"
            report += f"  - Phone: {appt.get('phone_number')}\n\n"
    
    return report

if __name__ == "__main__":
    # Run tests
    results = run_all_tests()
    
    # Generate report
    report = generate_test_report(results)
    
    # Save report
    with open("test_report.md", "w") as f:
        f.write(report)
    
    print(f"Test report saved to test_report.md")
