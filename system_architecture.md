# Clinic Voice AI - System Architecture

## Overview

The Clinic Voice AI system is designed to function as an automated receptionist for medical clinics, handling appointment scheduling through natural voice conversations. The system integrates multiple technologies to provide a seamless experience for callers while efficiently managing appointment data.

## System Components

### 1. Telephony Layer (Twilio)
- **Incoming Call Handling**: Receives and manages incoming phone calls
- **Audio Streaming**: Streams audio bidirectionally between caller and system
- **Webhook Integration**: Triggers application logic when calls are received
- **SMS Notifications**: Sends confirmation messages to patients

### 2. Speech Processing Layer
- **Speech Recognition (Whisper)**: Converts caller's speech to text
- **Text-to-Speech (ElevenLabs)**: Converts system responses to natural speech using "Rachel" voice
- **Audio Processing**: Handles noise reduction and audio quality optimization

### 3. Conversation Intelligence Layer
- **Natural Language Understanding (GPT-4)**: Interprets caller intent and extracts relevant information
- **Conversation Flow Management**: Guides the conversation to collect required information
- **Context Management**: Maintains conversation context throughout the call
- **Error Handling**: Manages misunderstandings and guides callers back on track

### 4. Appointment Management Layer
- **Time Slot Management**: Checks availability and suggests alternative times
- **Google Calendar Integration**: Creates and manages appointments
- **Google Sheets Integration**: Logs appointment details for record-keeping
- **Confirmation Generation**: Creates confirmation messages for SMS delivery

### 5. Web Demo Interface
- **Call Simulation**: Provides browser-based testing environment
- **Visual Feedback**: Displays conversation transcript and system state
- **Configuration Interface**: Allows adjustment of system parameters
- **Debug Tools**: Provides insights into system operation for development

## Data Flow

1. **Call Initiation**:
   - Caller dials clinic number
   - Twilio receives call and triggers webhook to application server
   - Application initializes conversation session

2. **Conversation Flow**:
   - System greets caller using ElevenLabs TTS
   - Caller responds, audio streamed to Whisper for transcription
   - Transcribed text processed by GPT-4 to determine intent and extract information
   - System generates appropriate response
   - Response converted to speech using ElevenLabs and played to caller

3. **Appointment Scheduling**:
   - System extracts patient name, requested service, and preferred time
   - Application checks Google Calendar for availability
   - If time slot available, appointment is confirmed
   - If unavailable, system suggests alternatives

4. **Confirmation Process**:
   - Appointment details added to Google Calendar
   - Appointment logged in Google Sheets
   - Confirmation SMS sent to patient via Twilio (if phone number provided)
   - Verbal confirmation provided to caller

## API Integrations

### Twilio API
- **Voice API**: Manages call handling and audio streaming
- **SMS API**: Sends confirmation messages
- **TwiML**: Defines call behavior and response logic

### ElevenLabs API
- **Text-to-Speech API**: Converts system responses to natural speech
- **Voice Selection**: Utilizes "Rachel" voice profile

### OpenAI API
- **Whisper API**: Transcribes caller speech to text
- **GPT-4 API**: Processes transcribed text for intent and information extraction

### Google APIs
- **Google Sheets API**: Logs appointment information
- **Google Calendar API**: Creates and manages appointments

## System Requirements

### Server Requirements
- Python 3.8+ runtime environment
- Flask/FastAPI web framework for webhook handling
- Secure HTTPS endpoint accessible by Twilio
- Sufficient processing power for real-time audio processing

### API Credentials
- Twilio account with phone number
- ElevenLabs API key
- OpenAI API key
- Google API credentials with appropriate permissions

### Storage
- Database for session management (optional)
- Google Sheets for appointment logging
- Google Calendar for appointment scheduling

## Scalability Considerations

The architecture is designed to be modular and scalable, allowing for:
- Multiple concurrent calls
- Easy addition of new clinic services
- Expansion to multiple clinic locations
- Customization of voice and conversation flow

## Security Considerations

- All API communications use HTTPS
- API keys stored securely as environment variables
- Patient data handled according to healthcare privacy standards
- Authentication required for administrative access
- Call recordings handled according to consent requirements
