# Clinic Voice AI - Documentation

## Overview

Clinic Voice AI is an automated receptionist system for medical clinics that handles appointment scheduling through natural voice conversations. The system integrates multiple technologies to provide a seamless experience for callers while efficiently managing appointment data.

## Features

- Natural voice conversations using ElevenLabs "Rachel" voice
- Appointment scheduling with availability checking
- Google Calendar integration for appointment management
- Google Sheets integration for appointment logging
- SMS confirmation messages via Twilio
- Web-based demo interface for testing
- Real phone call handling via Twilio

## System Requirements

- Python 3.8+
- Flask web framework
- Twilio account with phone number
- ElevenLabs API key
- OpenAI API key (for Whisper and GPT-4)
- Google API credentials with Sheets and Calendar access
- Internet-accessible server for Twilio webhooks

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/clinic-voice-ai.git
cd clinic-voice-ai
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up API Credentials

Create a `.env` file in the project root with the following variables:

```
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
GOOGLE_CREDENTIALS_FILE=path_to_credentials.json
SPREADSHEET_ID=your_google_spreadsheet_id
```

### 5. Set Up Google API Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Calendar API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file and save it to the project directory
6. Update the `GOOGLE_CREDENTIALS_FILE` in your `.env` file

## Running the Application

### Web Demo

To run the web-based demo:

```bash
python run.py
```

This will start the Flask server on `http://localhost:5000`.

### Running Tests

To run the automated test scenarios:

```bash
python run_tests.py
```

This will execute all test scenarios and generate a test report in `test_report.md`.

## Deployment

### Deploying to Production

1. Set up a production server with Python 3.8+
2. Clone the repository and install dependencies
3. Set up a production WSGI server (e.g., Gunicorn)
4. Configure Nginx or Apache as a reverse proxy
5. Set up SSL certificates for HTTPS
6. Update Twilio webhook URLs to point to your production server

Example Gunicorn configuration:

```bash
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloning for Other Clinics

To clone this system for another clinic:

1. Create a new copy of the repository
2. Update the clinic name and greeting messages in `app.py`
3. Set up new API credentials for the new clinic
4. Update the `.env` file with the new credentials
5. Deploy to a new server or hosting environment

## Configuration

### Customizing Voice and Conversation

To customize the voice and conversation flow:

1. Update the ElevenLabs voice ID in the `.env` file
2. Modify the system prompt in `src/conversation.py` to change the conversation style
3. Update the greeting and response templates in the code

### Modifying Appointment Types

To add or modify appointment types:

1. Update the conversation logic in `src/conversation.py` to handle new service types
2. Modify the Google Calendar event creation in `src/google_integration.py` if needed

## Troubleshooting

### Common Issues

1. **Twilio webhook errors**: Ensure your server is publicly accessible and the webhook URLs are correctly configured in the Twilio console.

2. **Google API authentication errors**: Verify that your credentials have the correct permissions and that the OAuth consent screen is properly configured.

3. **ElevenLabs voice synthesis issues**: Check your API key and voice ID, and ensure you have sufficient credits in your ElevenLabs account.

4. **Speech recognition problems**: Verify your OpenAI API key and check that the audio format is compatible with the Whisper API.

### Logs

Check the application logs for detailed error messages:

```bash
tail -f logs/app.log
```

## Architecture

The system is built with a modular architecture:

1. **Telephony Layer** (Twilio): Handles incoming calls and SMS
2. **Speech Processing Layer** (Whisper, ElevenLabs): Handles speech recognition and synthesis
3. **Conversation Intelligence Layer** (GPT-4): Manages the conversation flow
4. **Appointment Management Layer** (Google Calendar, Sheets): Handles appointment scheduling and logging
5. **Web Demo Interface**: Provides a testing environment

## API Reference

### Twilio Webhooks

- `/twilio/voice`: Handles incoming voice calls
- `/twilio/gather`: Processes speech input from callers

### Web Demo API

- `/api/start-call`: Initializes a new call session
- `/api/process-speech`: Processes transcribed speech
- `/api/get-conversation`: Gets conversation history
- `/api/get-appointments`: Gets all booked appointments

## Security Considerations

- All API keys should be kept secure and not committed to version control
- Use HTTPS for all production deployments
- Implement proper authentication for admin access
- Handle patient data according to healthcare privacy regulations
- Regularly rotate API keys and credentials

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, contact [your-email@example.com](mailto:your-email@example.com).
