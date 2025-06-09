#!/bin/bash

# Setup script for Clinic Voice AI
# This script sets up the environment and installs dependencies

echo "Setting up Clinic Voice AI..."

# Create .env file template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env template..."
    cat > .env << EOL
# Twilio Credentials
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# OpenAI Credentials
OPENAI_API_KEY=your_openai_api_key

# ElevenLabs Credentials
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ELEVENLABS_VOICE_ID=your_rachel_voice_id

# Google API
GOOGLE_CREDENTIALS_FILE=credentials.json
SPREADSHEET_ID=your_google_spreadsheet_id
EOL
    echo ".env template created. Please update with your API credentials."
fi

# Create logs directory
mkdir -p logs

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo "Setup complete! You can now run the application with:"
echo "python run.py"
