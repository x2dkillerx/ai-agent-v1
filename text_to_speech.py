"""
Text-to-Speech Module for Clinic Voice AI

This module handles voice synthesis using ElevenLabs API:
1. Converting text responses to natural speech
2. Managing voice profiles and settings
3. Optimizing audio for telephony and web playback
"""

import os
import requests
import json
import base64
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a production environment, this would be an environment variable
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_API_KEY"
ELEVENLABS_VOICE_ID = "YOUR_RACHEL_VOICE_ID"  # Rachel voice ID

def synthesize_speech(text):
    """
    Convert text to speech using ElevenLabs API
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Audio data in bytes
    """
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            return response.content
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error synthesizing speech: {str(e)}")
        return None

def get_base64_audio(text):
    """
    Get base64-encoded audio for web playback
    
    Args:
        text: Text to convert to speech
        
    Returns:
        Base64-encoded audio data
    """
    try:
        audio_data = synthesize_speech(text)
        
        if audio_data:
            # Convert to base64
            base64_audio = base64.b64encode(audio_data).decode('utf-8')
            return f"data:audio/mpeg;base64,{base64_audio}"
        else:
            return None
            
    except Exception as e:
        logger.error(f"Error getting base64 audio: {str(e)}")
        return None

def save_audio_file(text, file_path):
    """
    Save synthesized speech to a file
    
    Args:
        text: Text to convert to speech
        file_path: Path to save the audio file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        audio_data = synthesize_speech(text)
        
        if audio_data:
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            return True
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error saving audio file: {str(e)}")
        return False

# For demo/testing purposes
def mock_synthesize_speech(text):
    """
    Mock speech synthesis for testing without API calls
    
    Returns:
        Success message for testing
    """
    logger.info(f"Mock TTS: '{text}'")
    return "Mock audio data generated"
