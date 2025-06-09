"""
Speech Recognition Module for Clinic Voice AI

This module handles speech recognition using OpenAI's Whisper API:
1. Transcribing audio from callers
2. Processing and cleaning transcriptions
3. Handling different languages and accents
"""

import os
import tempfile
import logging
import requests
import json
import base64
from pydub import AudioSegment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a production environment, this would be an environment variable
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

def transcribe_audio(audio_data, format="wav"):
    """
    Transcribe audio using OpenAI's Whisper API
    
    Args:
        audio_data: Binary audio data
        format: Audio format (default: wav)
        
    Returns:
        Transcribed text
    """
    try:
        # Save audio data to a temporary file
        with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        # In a production environment, this would use the official OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "multipart/form-data"
        }
        
        with open(temp_file_path, "rb") as audio_file:
            files = {
                "file": (f"audio.{format}", audio_file, f"audio/{format}"),
                "model": (None, "whisper-1"),
                "language": (None, "en")
            }
            
            response = requests.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files
            )
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Parse response
        if response.status_code == 200:
            result = response.json()
            return result.get("text", "")
        else:
            logger.error(f"Whisper API error: {response.status_code} - {response.text}")
            return ""
            
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return ""

def process_twilio_recording(recording_url):
    """
    Process a Twilio recording URL and transcribe it
    
    Args:
        recording_url: URL of the Twilio recording
        
    Returns:
        Transcribed text
    """
    try:
        # Download the recording
        response = requests.get(recording_url)
        
        if response.status_code == 200:
            # Transcribe the audio
            return transcribe_audio(response.content, "wav")
        else:
            logger.error(f"Error downloading Twilio recording: {response.status_code}")
            return ""
            
    except Exception as e:
        logger.error(f"Error processing Twilio recording: {str(e)}")
        return ""

def transcribe_web_audio(base64_audio):
    """
    Transcribe base64-encoded audio from web client
    
    Args:
        base64_audio: Base64-encoded audio data
        
    Returns:
        Transcribed text
    """
    try:
        # Decode base64 audio
        audio_data = base64.b64decode(base64_audio.split(",")[1] if "," in base64_audio else base64_audio)
        
        # Transcribe the audio
        return transcribe_audio(audio_data, "webm")
        
    except Exception as e:
        logger.error(f"Error transcribing web audio: {str(e)}")
        return ""

# For demo/testing purposes
def mock_transcribe(audio_data=None):
    """
    Mock transcription function for testing without API calls
    
    Returns:
        Predefined responses for testing
    """
    import random
    
    # Sample responses for testing
    responses = [
        "I'd like to schedule an appointment for a dental checkup.",
        "My name is Sarah Johnson.",
        "I'm looking for a dermatologist appointment.",
        "Next Tuesday at 2 PM would work for me.",
        "Yes, that time works for me.",
        "My phone number is 555-123-4567.",
        "No, that's all I needed today. Thank you."
    ]
    
    return random.choice(responses)
