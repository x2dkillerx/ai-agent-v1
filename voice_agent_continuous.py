"""
Continuous Listening Clinic Voice AI with Real-Time Interruption

This version includes:
- Continuous listening with only Start/End Call controls
- Real-time interruption handling
- Adaptive AI responses to interruptions
- Advanced empathy and emotional intelligence
- Context awareness and memory throughout conversation
- Trust-building and rapport development
- Natural speech patterns with pauses and fillers
- ElevenLabs voice synthesis with improved expressiveness
- Modern UI/UX design
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
import logging
import random
import requests
import re
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # For session management

# API Keys from environment variables
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_VOICE_ID = os.getenv('ELEVENLABS_VOICE_ID')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

# In-memory storage for demo purposes
sessions = {}
appointments = []

# Sample available time slots for different services
AVAILABLE_SLOTS = {
    "dental": ["Monday at 10:00 AM", "Tuesday at 2:30 PM", "Wednesday at 9:15 AM"],
    "ent": ["Monday at 11:30 AM", "Wednesday at 3:00 PM", "Friday at 10:45 AM"],
    "dermatology": ["Tuesday at 9:00 AM", "Thursday at 1:15 PM", "Friday at 4:30 PM"],
    "general": ["Monday at 8:30 AM", "Tuesday at 4:00 PM", "Thursday at 11:00 AM"]
}

# Doctor information with detailed personality traits and specialties
DOCTORS = {
    "dental": [
        {
            "name": "Dr. Sarah Chen",
            "specialty": "cosmetic dentistry and preventative care",
            "personality": "gentle and thorough",
            "experience": "12 years",
            "patients_say": "she takes time to explain procedures and has a very gentle touch",
            "availability": ["Monday", "Wednesday", "Friday"],
            "education": "University of Michigan Dental School",
            "languages": ["English", "Mandarin"]
        },
        {
            "name": "Dr. Michael Rodriguez",
            "specialty": "orthodontics and pediatric dentistry",
            "personality": "friendly and great with anxious patients",
            "experience": "8 years",
            "patients_say": "he makes even nervous patients feel at ease and explains everything clearly",
            "availability": ["Tuesday", "Thursday", "Saturday morning"],
            "education": "UCLA School of Dentistry",
            "languages": ["English", "Spanish"]
        }
    ],
    "ent": [
        {
            "name": "Dr. James Wilson",
            "specialty": "sinus conditions and sleep apnea",
            "personality": "attentive and straightforward",
            "experience": "15 years",
            "patients_say": "he's very knowledgeable and takes time to answer all questions",
            "availability": ["Monday", "Tuesday", "Thursday"],
            "education": "Johns Hopkins Medical School",
            "languages": ["English"]
        },
        {
            "name": "Dr. Reetu Patel",
            "specialty": "hearing disorders and pediatric ENT",
            "personality": "warm and patient-centered",
            "experience": "10 years",
            "patients_say": "she's amazing with children and really listens to patient concerns",
            "availability": ["Wednesday", "Friday", "Saturday morning"],
            "education": "Stanford Medical School",
            "languages": ["English", "Hindi", "Gujarati"]
        }
    ],
    "dermatology": [
        {
            "name": "Dr. Emily Johnson",
            "specialty": "acne treatment and skin cancer screening",
            "personality": "compassionate and detail-oriented",
            "experience": "9 years",
            "patients_say": "she's thorough in her examinations and explains treatment options clearly",
            "availability": ["Monday", "Wednesday", "Friday"],
            "education": "Harvard Medical School",
            "languages": ["English"]
        },
        {
            "name": "Dr. David Kim",
            "specialty": "eczema, psoriasis, and cosmetic dermatology",
            "personality": "knowledgeable and reassuring",
            "experience": "14 years",
            "patients_say": "he's excellent at diagnosing complex skin conditions and has a calming presence",
            "availability": ["Tuesday", "Thursday", "Saturday morning"],
            "education": "Columbia University College of Physicians and Surgeons",
            "languages": ["English", "Korean"]
        }
    ],
    "general": [
        {
            "name": "Dr. Lisa Thompson",
            "specialty": "preventative care and women's health",
            "personality": "empathetic and thorough",
            "experience": "18 years",
            "patients_say": "she takes time to understand your overall health and lifestyle",
            "availability": ["Monday", "Tuesday", "Thursday"],
            "education": "Mayo Medical School",
            "languages": ["English", "French"]
        },
        {
            "name": "Dr. Robert Garcia",
            "specialty": "chronic disease management and geriatric care",
            "personality": "patient and comprehensive",
            "experience": "20 years",
            "patients_say": "he never rushes appointments and is excellent with elderly patients",
            "availability": ["Wednesday", "Friday"],
            "education": "University of Pennsylvania School of Medicine",
            "languages": ["English", "Spanish"]
        }
    ]
}

# Rachel's personality traits and background information
RACHEL_INFO = {
    "name": "Rachel",
    "full_name": "Rachel Williams",
    "role": "receptionist",
    "experience": "5 years",
    "background": "nursing assistant before becoming a receptionist",
    "favorite_part": "connecting patients with the right doctor and seeing them leave feeling better",
    "personality": "warm, empathetic, and occasionally uses humor to put patients at ease",
    "clinic_info": "Noor Medical Clinic offers comprehensive care with specialists in dental, ENT, dermatology, and general medicine.",
    "clinic_hours": "Monday through Friday from 8:00 AM to 6:00 PM, and Saturday from 9:00 AM to 1:00 PM.",
    "clinic_location": "123 Healthcare Avenue, in the Westside Medical Plaza.",
    "clinic_parking": "free parking available in the garage next to our building, and we validate for up to 2 hours.",
    "insurance": "We accept most major insurance plans including Blue Cross, Aetna, UnitedHealthcare, and Medicare.",
    "hobbies": "hiking with my dog Charlie, reading mystery novels, and trying new recipes",
    "personal_touch": "I actually used to be afraid of dentists until I started working here and saw how gentle our team is!",
    "weather": "It's lovely today! Though I mostly see it through the windows since I'm helping patients all day."
}

# Filler words and phrases for more natural speech
FILLERS = [
    "um", "uh", "hmm", "well", "you know", "like", "actually", "basically", 
    "I mean", "let's see", "so", "right", "okay", "now", "honestly", 
    "let me think", "let me check that for you", "just a moment", 
    "that's a good question", "I understand", "I see what you mean"
]

# Empathetic responses for various situations
EMPATHY = {
    "pain": [
        "Oh no, that sounds uncomfortable. We'll make sure the doctor addresses that right away.",
        "I'm sorry to hear you're in pain. That must be difficult to deal with.",
        "That sounds painful! Let's get you in to see the doctor as soon as possible.",
        "I understand how disruptive pain can be. We'll make sure you get the care you need."
    ],
    "anxiety": [
        "It's completely normal to feel nervous about medical appointments. Our doctors are really good at putting patients at ease.",
        "I understand your concerns. Many patients feel the same way, and our team is very gentle and supportive.",
        "I hear you. Medical anxiety is very common, and our doctors are really understanding about it.",
        "That's a very valid feeling. If it helps, we can make a note for the doctor so they're aware of your concerns."
    ],
    "urgency": [
        "I understand this is urgent for you. Let me see what we can do to get you in quickly.",
        "That definitely sounds like something we should address soon. Let me check our earliest openings.",
        "I can hear this is important to you. Let's prioritize finding you an appointment as soon as possible.",
        "I appreciate you letting me know this is urgent. Let me look for our next available slot."
    ],
    "confusion": [
        "I might not have explained that clearly. Let me try again in a different way.",
        "I understand that might be confusing. Let me break it down a bit more.",
        "Sorry about that! Let me clarify what I mean.",
        "That's a good point - let me make sure I'm being clear about this."
    ],
    "frustration": [
        "I understand your frustration. Let's take a step back and figure out the best way forward.",
        "I'm sorry this has been difficult. Your concerns are completely valid, and I want to help resolve this.",
        "I can hear this is frustrating for you, and I apologize for that. Let's see how we can make this better.",
        "You have every right to feel that way. Let me see what I can do to help improve the situation."
    ]
}

# Bridge phrases to handle topic changes gracefully
BRIDGES = {
    "acknowledge": [
        "I understand, that's important to know.",
        "Thanks for sharing that with me.",
        "I appreciate you mentioning that.",
        "That's good to know.",
        "I'm glad you brought that up."
    ],
    "transition": [
        "Let me address that first, and then we can continue with the booking if that's okay.",
        "I'd be happy to discuss that before we continue.",
        "Let's pause the scheduling for a moment to talk about that.",
        "That's a good question. Let me answer that before we move on.",
        "I can definitely help with that. Let's take a moment to address it."
    ],
    "return": [
        "Now, getting back to your appointment...",
        "So, returning to what we were discussing about scheduling...",
        "If you're ready, shall we continue with booking your appointment?",
        "Is there anything else you'd like to know, or shall we continue with the appointment details?",
        "Thanks for that discussion. Now, where were we with your appointment?"
    ],
    "listening": [
        "I'm listening, go ahead.",
        "Sure, I'm all ears.",
        "Of course, please tell me more.",
        "Yes, I'm here and listening.",
        "Please go ahead, I'm following you."
    ],
    "interruption": [
        "Oh, sorry about that. Go ahead.",
        "I hear you, please continue.",
        "Let me pause there. What were you saying?",
        "Sorry for talking over you. Please go on.",
        "I'll stop there. What did you want to say?"
    ]
}

# Trust-building phrases for doctor recommendations
TRUST_BUILDERS = [
    "Patients consistently give {doctor} excellent reviews, especially for {specialty}.",
    "I've heard many patients say that {doctor} is particularly good with {trait}.",
    "{doctor} has a wonderful way of {positive_action} that patients really appreciate.",
    "Many of our regular patients specifically request {doctor} because of {reason}.",
    "If it helps, {doctor} has {experience} years of experience and specializes in {specialty}.",
    "Personally, I've heard great things about how {doctor} {positive_quality}."
]

# Small talk responses for various topics
SMALL_TALK = {
    "greeting": [
        "Hi there! How are you doing today?",
        "Hello! It's great to hear from you. How can I help?",
        "Hey! How's your day going so far?",
        "Good to hear from you! How are you feeling today?"
    ],
    "how_are_you": [
        "I'm doing great, thanks for asking! It's been a busy but good day at the clinic. How about you?",
        "I'm wonderful, thank you! Always happy to help our patients. How are you today?",
        "I'm excellent! Just helping patients schedule their appointments. How are you feeling today?",
        "I'm very well, thanks! It's a pleasure to assist you today. How are you doing?"
    ],
    "thanks": [
        "You're very welcome! It's my pleasure to help.",
        "Happy to help! That's what I'm here for.",
        "No problem at all! Is there anything else I can assist you with?",
        "Of course! I'm glad I could be of assistance."
    ],
    "weather": [
        "The weather's been lovely lately! Though I'm inside the clinic most of the day. Are you enjoying it?",
        "I heard it's supposed to be nice this week! Perfect time to come in for your appointment.",
        "It's a beautiful day outside! Makes coming to appointments a bit more pleasant, doesn't it?",
        "The weather's been changing so much lately! Hope it's nice when you come in for your visit."
    ],
    "weekend": [
        "Weekends at the clinic are a bit quieter, but we're open Saturday mornings! Do you prefer weekend appointments?",
        "I love weekends too! We offer Saturday morning appointments if that works better for your schedule.",
        "Weekends are great, aren't they? We have limited Saturday hours if that's more convenient for you.",
        "The clinic has Saturday morning hours, which many of our patients find convenient for their busy schedules."
    ],
    "joke": [
        "Why don't scientists trust atoms? Because they make up everything! Sorry, that's my favorite clinic joke.",
        "What did one wall say to the other wall? I'll meet you at the corner! Sorry, I like to keep things light around here.",
        "Why did the doctor carry a red pen? In case they needed to draw blood! Sorry, medical humor is my specialty.",
        "What do you call a doctor who fixes websites? A URL-ologist! Sorry, I can't help myself with these jokes."
    ],
    "compliment": [
        "Aww, that's so sweet of you to say! You just made my day!",
        "Thank you so much! I really enjoy helping our patients.",
        "That's very kind of you! It means a lot to hear that.",
        "You're too kind! Comments like that make this job so rewarding."
    ]
}

# Humor responses for jokes or funny comments
HUMOR_RESPONSES = [
    "Haha! That's a good one! {filler} I needed that laugh today.",
    "Oh my goodness, that's funny! {filler} You have a great sense of humor.",
    "Haha! {filler} I appreciate patients who can keep things light.",
    "That made me smile! {filler} It's always nice to have a bit of humor in the day."
]

# Interruption responses based on context
INTERRUPTION_RESPONSES = {
    "greeting": [
        "Oh, sorry! Go ahead, I'm listening.",
        "Please, I didn't mean to interrupt. What were you saying?",
        "Sorry about that! Please continue."
    ],
    "collect_name": [
        "I'll pause there. Did you want to tell me your name?",
        "Sorry for talking too much. Please go ahead with your name.",
        "I hear you. Let's start with your name when you're ready."
    ],
    "collect_service": [
        "Sorry, I'll stop there. What type of appointment did you need?",
        "I hear you. What service were you interested in?",
        "Let me pause. What kind of appointment are you looking for?"
    ],
    "collect_time": [
        "Sorry about that. What time works best for you?",
        "I'll pause there. When would you like to come in?",
        "Let me stop and listen. What day and time would you prefer?"
    ],
    "collect_phone": [
        "Sorry, I'll pause. Could you share your phone number?",
        "I hear you. What's your phone number for the confirmation?",
        "Let me stop there. What phone number should we use for the confirmation?"
    ],
    "default": [
        "Sorry for talking over you. Please go ahead.",
        "I hear you. Please continue.",
        "Let me pause and listen to what you're saying."
    ]
}

@app.route('/')
def index():
    """Render the web demo interface with continuous listening"""
    return render_template('voice_index_continuous.html')

@app.route('/api/start-call', methods=['POST'])
def start_call():
    """Initialize a new call session"""
    session_id = str(random.randint(10000, 99999))
    sessions[session_id] = {
        'state': 'greeting',
        'patient_info': {},
        'conversation': [],
        'small_talk_count': 0,
        'last_topic': None,
        'mentioned_topics': set(),
        'emotional_state': 'neutral',
        'interruption_count': 0,
        'trust_established': False,
        'context_memory': {},
        'current_doctor_discussed': None,
        'rejected_doctors': set(),
        'was_interrupted': False,
        'last_response_time': datetime.now().isoformat()
    }
    
    # Add a natural filler word occasionally
    greeting = add_human_touches("Hello, thank you for calling Noor Medical Clinic. This is Rachel speaking. How can I help you today?")
    
    # Add to conversation history
    sessions[session_id]['conversation'].append({
        'role': 'system',
        'text': greeting,
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate voice audio with appropriate pauses and intonation
    audio_url = generate_voice(greeting, emotion="friendly")
    
    return jsonify({
        'session_id': session_id,
        'text': greeting,
        'audio_url': audio_url,
        'next_state': 'greeting'
    })

@app.route('/api/process-speech', methods=['POST'])
def process_speech():
    """Process transcribed speech with advanced conversation capabilities"""
    data = request.json
    session_id = data.get('session_id')
    transcript = data.get('transcript', '').strip()
    was_interrupted = data.get('interrupted', False)
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    session = sessions[session_id]
    current_state = session.get('state', 'greeting')
    patient_info = session.get('patient_info', {})
    small_talk_count = session.get('small_talk_count', 0)
    last_topic = session.get('last_topic', None)
    mentioned_topics = session.get('mentioned_topics', set())
    emotional_state = session.get('emotional_state', 'neutral')
    context_memory = session.get('context_memory', {})
    current_doctor_discussed = session.get('current_doctor_discussed', None)
    
    # Track interruptions
    if was_interrupted:
        session['interruption_count'] = session.get('interruption_count', 0) + 1
        session['was_interrupted'] = True
        logger.info(f"User interrupted. Total interruptions: {session['interruption_count']}")
    
    # Add user input to conversation history
    session['conversation'].append({
        'role': 'user',
        'text': transcript,
        'timestamp': datetime.now().isoformat(),
        'interrupted': was_interrupted
    })
    
    # Detect emotional state from text
    new_emotional_state = detect_emotion(transcript)
    if new_emotional_state != 'neutral':
        emotional_state = new_emotional_state
        session['emotional_state'] = emotional_state
        logger.info(f"Detected emotional state: {emotional_state}")

    # Handle if the user rejected a suggested doctor
    if check_doctor_rejection(transcript, session):
        service_type = get_service_category(patient_info.get('service', ''))
        new_doctor = get_available_doctor(service_type, session)
        session['current_doctor_discussed'] = new_doctor.get('name')
        response_text = (
            f"No problem, we can look at other options. {new_doctor['name']} is available"
            f" and specializes in {new_doctor['specialty']}. Would you like to schedule"
            f" with them?"
        )
        response_text = add_human_touches(response_text)
        session['conversation'].append({
            'role': 'system',
            'text': response_text,
            'timestamp': datetime.now().isoformat(),
        })
        audio_url = generate_voice(response_text, emotion="reassuring")
        sessions[session_id] = session
        return jsonify({'text': response_text, 'audio_url': audio_url, 'next_state': current_state})
    
    # Check for humor or jokes
    humor_response = check_for_humor(transcript)
    if humor_response:
        # Add human touches like fillers and pauses
        humor_response = add_human_touches(humor_response)
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': humor_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio with appropriate emotion
        audio_url = generate_voice(humor_response, emotion="amused")
        
        # Update session
        sessions[session_id] = session
        
        return jsonify({
            'text': humor_response,
            'audio_url': audio_url,
            'next_state': current_state
        })
    
    # Check for compliments
    if is_compliment(transcript):
        compliment_response = random.choice(SMALL_TALK["compliment"])
        compliment_response = add_human_touches(compliment_response)
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': compliment_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio with appropriate emotion
        audio_url = generate_voice(compliment_response, emotion="happy")
        
        # Update session
        sessions[session_id] = session
        
        return jsonify({
            'text': compliment_response,
            'audio_url': audio_url,
            'next_state': current_state
        })
    
    # Check for doctor-specific questions or comments
    doctor_response = check_for_doctor_questions(transcript, session)
    if doctor_response:
        # Remember we discussed this doctor
        if "Dr." in doctor_response:
            doctor_name = re.search(r'Dr\.\s+\w+', doctor_response)
            if doctor_name:
                session['current_doctor_discussed'] = doctor_name.group(0)
                context_memory['last_doctor_mentioned'] = doctor_name.group(0)
        
        session['last_topic'] = 'doctor_info'
        mentioned_topics.add('doctor_info')
        
        # Add empathy if the user expressed concerns
        if emotional_state in ['anxiety', 'confusion']:
            doctor_response = add_empathetic_response(emotional_state) + " " + doctor_response
        
        # Add human touches like fillers and pauses
        doctor_response = add_human_touches(doctor_response)
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': doctor_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio with appropriate emotion
        audio_url = generate_voice(doctor_response, emotion="reassuring")
        
        # Update session
        sessions[session_id] = session
        
        return jsonify({
            'text': doctor_response,
            'audio_url': audio_url,
            'next_state': current_state
        })
    
    # Check for clinic-specific questions
    clinic_response = check_for_clinic_questions(transcript)
    if clinic_response:
        session['last_topic'] = 'clinic_info'
        mentioned_topics.add('clinic_info')
        
        # Add human touches
        clinic_response = add_human_touches(clinic_response)
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': clinic_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio
        audio_url = generate_voice(clinic_response, emotion="informative")
        
        # Update session
        sessions[session_id] = session
        
        return jsonify({
            'text': clinic_response,
            'audio_url': audio_url,
            'next_state': current_state
        })
    
    # Check for small talk or personal questions
    small_talk_response = check_for_small_talk(transcript)
    if small_talk_response:
        session['small_talk_count'] = small_talk_count + 1
        session['last_topic'] = 'small_talk'
        mentioned_topics.add('small_talk')
        
        # Add human touches
        small_talk_response = add_human_touches(small_talk_response)
        
        # After 2 small talk exchanges, try to guide back to appointment booking
        if small_talk_count >= 1 and current_state in ['greeting', 'collect_name']:
            # Use a bridge phrase to transition naturally
            transition = random.choice(BRIDGES['transition'])
            return_phrase = random.choice(BRIDGES['return'])
            
            small_talk_response += f" {transition} {return_phrase}"
            next_state = 'collect_service' if 'name' in patient_info else 'collect_name'
        else:
            next_state = current_state
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': small_talk_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio with friendly tone
        audio_url = generate_voice(small_talk_response, emotion="friendly")
        
        # Update session
        session['state'] = next_state
        sessions[session_id] = session
        
        return jsonify({
            'text': small_talk_response,
            'audio_url': audio_url,
            'next_state': next_state
        })
    
    # Check for "hear me out" or similar phrases indicating user wants attention
    if re.search(r'hear me out|listen|excuse me|wait|hold on', transcript.lower()):
        listening_response = random.choice(BRIDGES['listening'])
        session['last_topic'] = 'listening'
        
        # Add human touches
        listening_response = add_human_touches(listening_response)
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': listening_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio with attentive tone
        audio_url = generate_voice(listening_response, emotion="attentive")
        
        # Update session
        sessions[session_id] = session
        
        return jsonify({
            'text': listening_response,
            'audio_url': audio_url,
            'next_state': current_state
        })
    
    # Handle if user was interrupted
    if session.get('was_interrupted', False):
        # Get appropriate interruption response based on current state
        interruption_responses = INTERRUPTION_RESPONSES.get(current_state, INTERRUPTION_RESPONSES['default'])
        interruption_response = random.choice(interruption_responses)
        
        # Reset interruption flag
        session['was_interrupted'] = False
        
        # Add system response to conversation history
        session['conversation'].append({
            'role': 'system',
            'text': interruption_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate voice audio with apologetic tone
        audio_url = generate_voice(interruption_response, emotion="apologetic")
        
        # Update session
        sessions[session_id] = session
        
        return jsonify({
            'text': interruption_response,
            'audio_url': audio_url,
            'next_state': current_state
        })
    
    # Process based on current state with improved NLP and context awareness
    if current_state == 'greeting':
        # Handle greetings and extract name if provided
        name = extract_name(transcript)
        
        if name:
            patient_info['name'] = name
            context_memory['patient_name'] = name
            session['fallback_count'] = 0
            
            # Personalized greeting with the patient's name
            response_text = f"{add_filler()} It's lovely to meet you, {name}! {add_filler()} My name is Rachel, and I'm the receptionist here at Noor Medical. What type of appointment are you looking to schedule today? We offer dental, ENT, dermatology, and general checkups."
            next_state = 'collect_service'
        else:
            # Check if they're asking about booking
            if is_booking_inquiry(transcript):
                response_text = f"{add_filler()} I'd be happy to help you book an appointment! Could I get your name first, please?"
                next_state = 'collect_name'
            else:
                response_text = f"It's great to chat with you! {add_filler()} I'm Rachel, the receptionist at Noor Medical Clinic. Could I get your name, please? Then I can help you with scheduling an appointment or answering any questions you might have."
                next_state = 'collect_name'
            
    elif current_state == 'collect_name':
        # Extract name with improved NLP
        name = extract_name(transcript)
        
        if name:
            patient_info['name'] = name
            context_memory['patient_name'] = name
            
            # Confirm the name to ensure accuracy
            response_text = f"Thanks, {name}! {add_filler()} Did I get your name right? {add_filler()} What type of appointment would you like to schedule? We offer dental care, ENT services, dermatology, and general checkups. Or if you have questions about any of our doctors or services, I'm happy to help with that too."
            next_state = 'collect_service'
        else:
            # If we still can't extract a name, ask for clarification
            response_text = handle_fallback(session, f"{add_filler()} I'm sorry, I didn't quite catch your name. Could you please repeat it for me?")
            next_state = 'collect_name'
        
    elif current_state == 'collect_service':
        # Extract service with improved NLP
        service = extract_service(transcript)
        
        if service:
            patient_info['service'] = service
            context_memory['service_type'] = service
            session['fallback_count'] = 0
            
            # Personalize with doctor information
            doctors_list = DOCTORS.get(service, [])
            if doctors_list:
                doctor = get_available_doctor(service, session)
                doctor_name = doctor["name"]
                doctor_specialty = doctor["specialty"]
                doctor_personality = doctor["personality"]
                
                # Remember this doctor for context
                session['current_doctor_discussed'] = doctor_name
                context_memory['last_doctor_mentioned'] = doctor_name
                
                # Build trust with specific details about the doctor
                trust_builder = random.choice(TRUST_BUILDERS).format(
                    doctor=doctor_name,
                    specialty=doctor_specialty,
                    trait=doctor_personality,
                    positive_action="explaining procedures in simple terms",
                    reason="their gentle approach",
                    experience=doctor["experience"],
                    positive_quality="takes time with each patient"
                )
                
                response_text = f"Great choice! {add_filler()} Our {service} department is excellent. {trust_builder} When would you prefer to come in? We have several openings this week, or I can check specific days for you."
            else:
                response_text = f"Great choice! {add_filler()} Our {service} department is excellent. When would you prefer to come in? We have several openings this week, or I can check specific days for you."
                
            next_state = 'collect_time'
        else:
            # Check if they're asking about available services
            if "what" in transcript.lower() and any(word in transcript.lower() for word in ["services", "offer", "provide", "available"]):
                response_text = f"{add_filler()} We offer a wide range of services at Noor Medical Clinic, including dental care, ENT (ear, nose, and throat), dermatology, and general medical checkups. Our doctors are all board-certified with excellent reputations. Which service were you interested in today?"
            else:
                response_text = handle_fallback(session, f"I'm sorry, {add_filler()} I didn't quite catch which service you need. We offer dental care, ENT services, dermatology, and general checkups. Which one would you like to schedule?")
            next_state = 'collect_service'
        
    elif current_state == 'collect_time':
        # Extract preferred time with improved NLP
        preferred_time = extract_time(transcript)
        
        if preferred_time:
            patient_info['preferred_time'] = preferred_time
            context_memory['appointment_time'] = preferred_time
            session['fallback_count'] = 0
            
            # Check availability with more realistic logic
            service_type = get_service_category(patient_info.get('service', ''))
            is_available = check_availability(service_type, preferred_time)
            
            if is_available:
                response_text = f"Perfect! {add_filler()} {preferred_time} works great for your {patient_info['service']} appointment. Could I get your phone number for the confirmation? We'll send you a reminder text the day before."
                next_state = 'collect_phone'
            else:
                # Suggest alternative based on service type
                alternative_time = suggest_alternative_time(service_type, preferred_time)
                patient_info['alternative_time'] = alternative_time
                context_memory['alternative_time'] = alternative_time
                
                # Get doctor information for personalization
                doctors_list = DOCTORS.get(service_type, [])
                if doctors_list:
                    doctor = get_available_doctor(service_type, session)
                else:
                    doctor = {"name": "our specialist"}

                doctor_name = doctor["name"] if isinstance(doctor, dict) else doctor
                session['current_doctor_discussed'] = doctor_name
                
                response_text = f"{add_filler()} I just checked the schedule, and unfortunately {preferred_time} is already booked for {patient_info['service']}. {doctor_name} does have availability on {alternative_time} though. Would that work for you instead?"
                next_state = 'confirm_alternative_time'
        else:
            # Check if they're asking about doctor availability
            if "available" in transcript.lower() or "schedule" in transcript.lower() or "free" in transcript.lower():
                service_type = get_service_category(patient_info.get('service', ''))
                doctors_list = DOCTORS.get(service_type, [])

                if doctors_list:
                    doctor = get_available_doctor(service_type, session)
                    doctor_name = doctor["name"] if isinstance(doctor, dict) else doctor
                    session['current_doctor_discussed'] = doctor_name
                    doctor_availability = doctor["availability"] if isinstance(doctor, dict) and "availability" in doctor else ["Monday", "Wednesday", "Friday"]
                    
                    avail_str = f"{doctor_availability[0]} and {doctor_availability[1]}" if len(doctor_availability) > 1 else doctor_availability[0]
                    
                    response_text = f"{doctor_name} is typically available on {avail_str}. {add_filler()} We could also check with other {service_type} specialists if you have a specific day in mind. What time would work best for you?"
                else:
                    response_text = f"Our {service_type} specialists have various availability throughout the week. {add_filler()} Do you have a specific day or time that works best for you?"
            else:
                msg = f"{add_filler()} I'd be happy to find a convenient time for you. Do you prefer mornings or afternoons? We have appointments available throughout the week, and even some Saturday morning slots for certain services."
                response_text = handle_fallback(session, msg)
            next_state = 'collect_time'
            
    elif current_state == 'confirm_alternative_time':
        # Check if user accepts alternative time with improved NLP
        if is_affirmative(transcript):
            # Update preferred time with the alternative
            patient_info['preferred_time'] = patient_info['alternative_time']
            context_memory['appointment_time'] = patient_info['alternative_time']
            
            response_text = f"Wonderful! {add_filler()} I've got you down for {patient_info['preferred_time']}. Could I get your phone number to send you a confirmation? We'll also send a reminder the day before your appointment."
            next_state = 'collect_phone'
        elif is_negative(transcript):
            # Suggest another time
            service_type = get_service_category(patient_info.get('service', ''))
            new_alternative = suggest_alternative_time(service_type, patient_info['alternative_time'], exclude_previous=True)
            patient_info['alternative_time'] = new_alternative
            context_memory['alternative_time'] = new_alternative
            
            response_text = f"No problem at all! {add_filler()} Let me check what else we have... How about {new_alternative}? That just opened up in our schedule. Would that work better for you?"
            next_state = 'confirm_alternative_time'
        else:
            # Check if they're asking about the doctor
            if "doctor" in transcript.lower() or "who" in transcript.lower() or "good" in transcript.lower():
                service_type = get_service_category(patient_info.get('service', ''))
                doctors_list = DOCTORS.get(service_type, [])

                if doctors_list:
                    doctor = get_available_doctor(service_type, session)
                    session['current_doctor_discussed'] = doctor['name'] if isinstance(doctor, dict) else doctor
                else:
                    doctor = {"name": "our specialist", "patients_say": "they provide excellent care"}
                
                # Build trust with specific details
                if isinstance(doctor, dict):
                    trust_response = f"{doctor['name']} is excellent! {add_filler()} Patients consistently say that {doctor['patients_say']}. {add_filler()} Would you like to proceed with the appointment at {patient_info['alternative_time']}?"
                else:
                    trust_response = f"{doctor} is one of our top specialists. Patients consistently give positive feedback about their care. Would you like to proceed with the appointment at {patient_info['alternative_time']}?"
                
                # Add system response to conversation history
                session['conversation'].append({
                    'role': 'system',
                    'text': trust_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Generate voice audio with confident tone
                audio_url = generate_voice(trust_response, emotion="confident")
                
                # Update session
                sessions[session_id] = session
                
                return jsonify({
                    'text': trust_response,
                    'audio_url': audio_url,
                    'next_state': current_state
                })
            
            response_text = f"{add_filler()} I'm not quite sure if that works for you. Just to confirm, would {patient_info['alternative_time']} work for your {patient_info['service']} appointment? We want to make sure we find a time that's convenient for you."
            next_state = 'confirm_alternative_time'
            
    elif current_state == 'collect_phone':
        # Extract phone number with improved NLP
        phone = extract_phone(transcript)
        
        if phone:
            # Validate phone number format for UAE
            if is_valid_uae_phone(phone):
                patient_info['phone'] = phone
                context_memory['phone_number'] = phone
                session['fallback_count'] = 0
                
                # Confirm the phone number to ensure accuracy
                formatted_phone = format_uae_phone(phone)
                response_text = f"Let me confirm that phone number - {formatted_phone}. Is that correct? {add_filler()} This is the number we'll use to send your appointment confirmation."
                next_state = 'confirm_phone'
            else:
                response_text = handle_fallback(session, f"{add_filler()} That doesn't seem to be a valid UAE phone number. Could you please provide your phone number again? It should start with 05 or +971.")
                next_state = 'collect_phone'
        else:
            response_text = handle_fallback(session, f"I'm sorry, {add_filler()} I didn't quite catch your phone number. Could you please provide it again? We'll use it to send you a confirmation text and appointment reminder.")
            next_state = 'collect_phone'
    
    elif current_state == 'confirm_phone':
        # Check if user confirms phone number
        if is_affirmative(transcript):
            # Save appointment
            appointment = {
                'patient_name': patient_info['name'],
                'service': patient_info['service'],
                'scheduled_time': patient_info['preferred_time'],
                'phone_number': patient_info['phone'],
                'timestamp': datetime.now().isoformat()
            }
            
            appointments.append(appointment)
            
            # Mock logging to Google Sheets and Calendar
            logger.info(f"Mock: Appointment logged to Google Sheets: {json.dumps(appointment)}")
            logger.info(f"Mock: Calendar event created: {json.dumps(appointment)}")
            
            # Mock SMS confirmation
            logger.info(f"Mock: SMS confirmation sent to {patient_info['phone']}")
            
            # Personalize confirmation
            service_type = get_service_category(patient_info.get('service', ''))
            doctors_list = DOCTORS.get(service_type, [])
            
            if doctors_list:
                doctor = get_available_doctor(service_type, session)
                doctor_name = doctor["name"] if isinstance(doctor, dict) else doctor
                session['current_doctor_discussed'] = doctor_name
            else:
                doctor = {"name": "our specialist"}
                doctor_name = doctor["name"]
            
            response_text = f"Perfect! {add_filler()} I've booked your {patient_info['service']} appointment with {doctor_name} for {patient_info['preferred_time']}. You'll receive a text confirmation at {format_uae_phone(patient_info['phone'])} shortly, and a reminder the day before your appointment. Is there anything else I can help you with today? Any questions about preparing for your visit?"
            next_state = 'confirm_complete'
        elif is_negative(transcript):
            response_text = f"I apologize for getting that wrong. {add_filler()} Could you please provide your phone number again? We want to make sure we have the correct number for your appointment confirmation."
            next_state = 'collect_phone'
        else:
            response_text = f"{add_filler()} I'm not sure if that's a yes or no. Could you please confirm if {format_uae_phone(patient_info['phone'])} is the correct phone number for your appointment confirmation?"
            next_state = 'confirm_phone'
        
    elif current_state == 'confirm_complete':
        if is_affirmative(transcript) or "question" in transcript.lower():
            service_type = get_service_category(patient_info.get('service', ''))
            
            if service_type == "dental":
                response_text = f"{add_filler()} For your dental appointment, it's best to brush and floss before coming in, but avoid eating right before your visit. {add_filler()} Do you have any specific concerns about your teeth or gums that we should note for the dentist?"
            elif service_type == "ent":
                response_text = f"{add_filler()} For your ENT appointment, there's no special preparation needed. Just arrive about 10 minutes early to complete any paperwork. {add_filler()} Is there a specific ear, nose, or throat issue you're experiencing that we should note for the doctor?"
            elif service_type == "dermatology":
                response_text = f"{add_filler()} For your dermatology appointment, it's helpful to avoid wearing makeup if the issue is on your face. Also, make a note of when you first noticed the skin concern. {add_filler()} Is there anything specific about your skin condition that we should tell the doctor in advance?"
            else:
                response_text = f"{add_filler()} For your general checkup, it's good to fast for about 8 hours before if bloodwork might be needed. Wear comfortable clothing, and bring a list of any medications you're taking. {add_filler()} Do you have any specific health concerns you'd like the doctor to address?"
                
            next_state = 'provide_info'
        else:
            # Check if they're asking about something specific
            if "parking" in transcript.lower():
                response_text = f"{add_filler()} We have {RACHEL_INFO['clinic_parking']} I've made a note of your appointment, and we're looking forward to seeing you. Is there anything else you'd like to know before we end the call?"
                next_state = 'confirm_complete'
            elif "insurance" in transcript.lower() or "payment" in transcript.lower():
                response_text = f"{add_filler()} {RACHEL_INFO['insurance']} If you'd like, you can bring your insurance card to your appointment, and we can verify coverage for you. Is there anything else you need to know?"
                next_state = 'confirm_complete'
            else:
                response_text = f"Thank you for calling Noor Medical Clinic today! {add_filler()} We're looking forward to seeing you for your appointment. If you need to reschedule or have any questions before your visit, please don't hesitate to call us back. Have a wonderful day!"
                next_state = 'end_call'
            
    elif current_state == 'provide_info':
        # Add the information to the appointment notes
        context_memory['additional_notes'] = transcript
        
        response_text = f"Thank you for sharing that information. {add_filler()} I've added a note to your appointment so the doctor will be prepared to discuss this with you. We're looking forward to seeing you at Noor Medical Clinic! Is there anything else you'd like to know before we end the call?"
        next_state = 'end_call'
        
    else:
        # Handle unexpected states or inputs
        # Check if we can extract intent from the transcript
        if "appointment" in transcript.lower() or "schedule" in transcript.lower() or "book" in transcript.lower():
            response_text = f"{add_filler()} I'd be happy to help you book an appointment. Could you please tell me what type of service you're looking for? We offer dental, ENT, dermatology, and general checkups."
            next_state = 'collect_service'
        elif "doctor" in transcript.lower() or "specialist" in transcript.lower():
            response_text = f"{add_filler()} We have excellent doctors in all our departments. Could you tell me what type of specialist you'd like to see? We have dental, ENT, dermatology, and general practice doctors."
            next_state = 'collect_service'
        else:
            msg = f"I'm sorry, {add_filler()} I didn't quite catch that. Could you please repeat what you said? I want to make sure I'm helping you correctly."
            response_text = handle_fallback(session, msg)
            next_state = current_state
    
    # Add empathy based on detected emotion
    if emotional_state != 'neutral' and random.random() < 0.7:  # 70% chance to add empathy
        empathy_prefix = add_empathetic_response(emotional_state)
        if empathy_prefix:
            response_text = f"{empathy_prefix} {response_text}"
    
    # Add human touches like fillers and pauses
    response_text = add_human_touches(response_text)
    
    # Add system response to conversation history
    session['conversation'].append({
        'role': 'system',
        'text': response_text,
        'timestamp': datetime.now().isoformat()
    })
    
    # Generate voice audio with appropriate emotion
    emotion = "friendly"
    if emotional_state == "anxiety":
        emotion = "reassuring"
    elif emotional_state == "urgency":
        emotion = "efficient"
    elif emotional_state == "frustration":
        emotion = "apologetic"
    
    audio_url = generate_voice(response_text, emotion=emotion)
    
    # Update session
    session['state'] = next_state
    session['patient_info'] = patient_info
    session['last_topic'] = 'appointment'
    session['context_memory'] = context_memory
    session['last_response_time'] = datetime.now().isoformat()
    sessions[session_id] = session
    
    return jsonify({
        'text': response_text,
        'audio_url': audio_url,
        'next_state': next_state
    })

@app.route('/api/get-conversation', methods=['GET'])
def get_conversation():
    """Get conversation history for a session"""
    session_id = request.args.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    return jsonify(sessions[session_id]['conversation'])

@app.route('/api/get-appointments', methods=['GET'])
def get_appointments():
    """Get all booked appointments"""
    return jsonify(appointments)

@app.route('/api/interrupt', methods=['POST'])
def handle_interruption():
    """Handle user interruption during AI speech"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Invalid session ID'})
    
    # Mark the session as interrupted
    sessions[session_id]['was_interrupted'] = True
    sessions[session_id]['interruption_count'] = sessions[session_id].get('interruption_count', 0) + 1
    
    # Log the interruption
    logger.info(f"User interrupted AI speech for session {session_id}")
    
    # Return acknowledgment
    return jsonify({
        'status': 'ok',
        'message': 'Interruption registered'
    })

# Conversation Helper Functions
def check_for_small_talk(text):
    """Check if the user is making small talk and generate appropriate response"""
    text_lower = text.lower()
    
    # Check for questions about Rachel
    if "your name" in text_lower or "who are you" in text_lower:
        return f"My name is {RACHEL_INFO['name']}! I'm the receptionist here at Noor Medical Clinic. I've been working here for {RACHEL_INFO['experience']} and I really enjoy {RACHEL_INFO['favorite_part']}."
    
    if "how are you" in text_lower or "how's your day" in text_lower or "how are things" in text_lower:
        return random.choice(SMALL_TALK["how_are_you"])
    
    if "thank you" in text_lower or "thanks" in text_lower:
        return random.choice(SMALL_TALK["thanks"])
    
    if "weather" in text_lower or "nice day" in text_lower or "raining" in text_lower or "sunny" in text_lower:
        return random.choice(SMALL_TALK["weather"])
    
    if "weekend" in text_lower or "saturday" in text_lower or "sunday" in text_lower:
        return random.choice(SMALL_TALK["weekend"])
    
    if "joke" in text_lower or "funny" in text_lower:
        return random.choice(SMALL_TALK["joke"])
    
    # Check for personal questions about Rachel
    if "how long" in text_lower and ("work" in text_lower or "been" in text_lower):
        return f"I've been working at Noor Medical Clinic for {RACHEL_INFO['experience']}. Before that, I was a {RACHEL_INFO['background']}. I really love working here because {RACHEL_INFO['favorite_part']}."
    
    if "like" in text_lower and "job" in text_lower:
        return f"I really enjoy my job! My favorite part is {RACHEL_INFO['favorite_part']}. {RACHEL_INFO['personal_touch']}"
    
    if "do you" in text_lower and ("live" in text_lower or "from" in text_lower):
        return f"I live pretty close to the clinic actually. Makes for an easy commute! In my free time, I enjoy {RACHEL_INFO['hobbies']}."
    
    # Check for general greetings if no other small talk detected
    if any(word in text_lower for word in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening"]):
        if len(text_lower.split()) < 5:  # Only respond to short greetings
            return random.choice(SMALL_TALK["greeting"])
    
    return None

def check_for_humor(text):
    """Check if the user is making a joke or being humorous"""
    text_lower = text.lower()
    
    # Check for common joke indicators
    joke_indicators = [
        "haha", "hehe", "lol", "lmao", "rofl", "joke", "funny", "kidding", "just kidding", "jk"
    ]
    
    if any(indicator in text_lower for indicator in joke_indicators):
        response = random.choice(HUMOR_RESPONSES).format(filler=add_filler())
        return response
    
    # Check for specific joke patterns
    if "knock knock" in text_lower:
        return "Haha! Who's there? I love knock-knock jokes!"
    
    if "why did the" in text_lower or "what do you call" in text_lower:
        return "Haha! That's a good one! I love jokes like that. They make my day at the reception desk more fun."
    
    return None

def is_compliment(text):
    """Check if the user is giving a compliment"""
    text_lower = text.lower()
    
    compliment_indicators = [
        "nice voice", "sound nice", "sound good", "like your voice", 
        "helpful", "you're great", "you are great", "you're amazing", "you are amazing",
        "thank you so much", "appreciate", "wonderful", "excellent", "fantastic",
        "good job", "well done", "impressive"
    ]
    
    return any(indicator in text_lower for indicator in compliment_indicators)

def check_for_doctor_questions(text, session):
    """Check if the user is asking about doctors with context awareness"""
    text_lower = text.lower()
    context_memory = session.get('context_memory', {})
    current_doctor = session.get('current_doctor_discussed')
    
    # Check for questions about specific doctors
    for service, doctors_list in DOCTORS.items():
        for doctor in doctors_list:
            doctor_last = doctor["name"].split()[1].lower()
            doctor_first = doctor["name"].split()[0].lower().replace("dr.", "").strip()
            
            if doctor_last in text_lower or (doctor_first in text_lower and "dr" in text_lower):
                # Remember this doctor was discussed
                session['current_doctor_discussed'] = doctor["name"]
                
                # Check for specific questions about the doctor
                if "good" in text_lower or "recommend" in text_lower or "best" in text_lower or "trust" in text_lower:
                    return f"Yes, {doctor['name']} is excellent! Patients consistently say that {doctor['patients_say']}. They have {doctor['experience']} experience and are known for being {doctor['personality']}. Would you like to schedule with them?"
                
                if "available" in text_lower or "schedule" in text_lower or "appointment" in text_lower or "book" in text_lower:
                    avail_str = f"{doctor['availability'][0]} and {doctor['availability'][1]}" if len(doctor['availability']) > 1 else doctor['availability'][0]
                    return f"{doctor['name']} is typically available on {avail_str}. Would any of those days work for you?"
                
                if "specialty" in text_lower or "specialize" in text_lower or "expert" in text_lower:
                    return f"{doctor['name']} specializes in {doctor['specialty']}. They're particularly known for their {doctor['personality']} approach with patients."
                
                if "experience" in text_lower or "how long" in text_lower or "background" in text_lower:
                    return f"{doctor['name']} has {doctor['experience']} of experience and trained at {doctor['education']}. They're one of our most experienced specialists in {service}."
                
                if "language" in text_lower or "speak" in text_lower:
                    langs = ", ".join(doctor['languages'])
                    return f"{doctor['name']} speaks {langs}. Would you prefer your appointment in a specific language?"
                
                # General information if no specific question detected
                return f"{doctor['name']} is one of our top {service} specialists with {doctor['experience']} experience. They're known for being {doctor['personality']} and specializing in {doctor['specialty']}. Patients particularly appreciate how {doctor['patients_say']}. Would you like to schedule an appointment with them?"
    
    # Check if they're asking about the previously mentioned doctor
    if current_doctor and ("doctor" in text_lower or "about" in text_lower or "tell me" in text_lower or "good" in text_lower or "who" in text_lower):
        # Find the doctor in our database
        for service, doctors_list in DOCTORS.items():
            for doctor in doctors_list:
                if doctor["name"] == current_doctor:
                    if "good" in text_lower or "recommend" in text_lower or "best" in text_lower or "trust" in text_lower:
                        return f"Yes, {doctor['name']} is excellent! Patients consistently say that {doctor['patients_say']}. They have {doctor['experience']} experience and are known for being {doctor['personality']}. Would you like to schedule with them?"
                    
                    # General information if no specific question detected
                    return f"{doctor['name']} is one of our top {service} specialists with {doctor['experience']} experience. They're known for being {doctor['personality']} and specializing in {doctor['specialty']}. Patients particularly appreciate how {doctor['patients_say']}. Would you like to schedule an appointment with them?"
    
    # Check for general questions about doctors
    if "doctor" in text_lower or "specialist" in text_lower or "physician" in text_lower:
        if "best" in text_lower or "recommend" in text_lower or "good" in text_lower:
            return "All of our doctors are excellent and board-certified in their specialties. If you let me know what type of service you're looking for, I can tell you more about the specific doctors in that department."
        
        if "how many" in text_lower or "available" in text_lower:
            return "We have multiple specialists in each department. Our dental, ENT, dermatology, and general practice departments each have at least two dedicated doctors, plus supporting staff. Would you like to know about a specific department?"
    
    return None

def check_for_clinic_questions(text):
    """Check if the user is asking about the clinic"""
    text_lower = text.lower()
    
    if "hours" in text_lower or "open" in text_lower or "close" in text_lower or "when" in text_lower:
        return f"Noor Medical Clinic is open {RACHEL_INFO['clinic_hours']}"
    
    if "location" in text_lower or "address" in text_lower or "where" in text_lower:
        return f"We're located at {RACHEL_INFO['clinic_location']}"
    
    if "parking" in text_lower:
        return f"We have {RACHEL_INFO['clinic_parking']}"
    
    if "insurance" in text_lower or "cover" in text_lower or "payment" in text_lower:
        return f"{RACHEL_INFO['insurance']} We also offer payment plans for those without insurance. Would you like me to check if we accept your specific insurance?"
    
    if "covid" in text_lower or "mask" in text_lower or "vaccination" in text_lower:
        return "We follow all current health guidelines. Masks are optional but available if you'd like one. If you're experiencing any COVID symptoms, we ask that you reschedule or consider a telehealth appointment instead."
    
    if "services" in text_lower or "offer" in text_lower or "provide" in text_lower:
        return f"{RACHEL_INFO['clinic_info']} Each department has highly qualified specialists. Is there a particular service you're interested in today?"
    
    return None

def is_booking_inquiry(text):
    """Check if the user is asking about booking an appointment"""
    text_lower = text.lower()
    booking_terms = ["book", "schedule", "appointment", "reserve", "see a doctor", "visit", "come in"]
    
    return any(term in text_lower for term in booking_terms)

def detect_emotion(text):
    """Detect emotional state from text"""
    text_lower = text.lower()
    
    # Pain indicators
    pain_words = ["pain", "hurt", "ache", "sore", "discomfort", "suffering", "agony", "ouch"]
    if any(word in text_lower for word in pain_words):
        return "pain"
    
    # Anxiety indicators
    anxiety_words = ["anxious", "nervous", "worried", "scared", "afraid", "fear", "stress", "concern", "panic"]
    if any(word in text_lower for word in anxiety_words):
        return "anxiety"
    
    # Urgency indicators
    urgency_words = ["urgent", "emergency", "asap", "right away", "immediately", "soon", "hurry", "quick"]
    if any(word in text_lower for word in urgency_words):
        return "urgency"
    
    # Confusion indicators
    confusion_words = ["confused", "don't understand", "what do you mean", "unclear", "lost", "not following"]
    if any(word in text_lower for word in confusion_words):
        return "confusion"
    
    # Frustration indicators
    frustration_words = ["frustrated", "annoyed", "upset", "angry", "mad", "irritated", "fed up", "tired of"]
    if any(word in text_lower for word in frustration_words):
        return "frustration"
    
    return "neutral"

def add_empathetic_response(emotional_state):
    """Add an empathetic response based on detected emotion"""
    if emotional_state in EMPATHY:
        return random.choice(EMPATHY[emotional_state])
    return ""

def add_filler():
    """Add a filler word or phrase for more natural speech"""
    # 40% chance to add a filler
    if random.random() < 0.4:
        return random.choice(FILLERS)
    return ""

def add_human_touches(text):
    """Add human touches like fillers, pauses, and repetitions to text"""
    # Don't modify text that already has human touches
    if any(filler in text.lower() for filler in ["um", "uh", "well", "actually", "you know"]):
        return text
    
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Process each sentence
    for i in range(len(sentences)):
        # Skip very short sentences
        if len(sentences[i].split()) < 3:
            continue
        
        # 30% chance to add a filler at the beginning of a sentence
        if random.random() < 0.3 and i > 0:
            sentences[i] = add_filler() + " " + sentences[i]
    
    # Rejoin sentences
    text = " ".join(sentences)
    
    # Remove any double spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text

# Fallback helper to escalate when repeated misunderstandings occur
def handle_fallback(session, default_message):
    """Return a fallback message and update fallback counter."""
    count = session.get('fallback_count', 0) + 1
    session['fallback_count'] = count

    if count == 1:
        return default_message
    elif count == 2:
        return f"{default_message} Could you rephrase it another way?"
    else:
        return "I'm still having trouble understanding. Would you like me to connect you to a staff member for further assistance?"

# Doctor helper utilities
def get_available_doctor(service_type, session):
    """Return a doctor not previously rejected."""
    doctors_list = DOCTORS.get(service_type, [])
    rejected = session.get('rejected_doctors', set())
    available = [d for d in doctors_list if d.get('name') not in rejected]
    if not available:
        available = doctors_list
    return random.choice(available) if available else {"name": "our specialist"}


def check_doctor_rejection(text, session):
    """Detect if the user rejected the currently suggested doctor."""
    current_doctor = session.get('current_doctor_discussed')
    if not current_doctor:
        return False

    text_lower = text.lower()
    doctor_last = current_doctor.split()[-1].lower()
    doctor_first = current_doctor.split()[1].lower() if len(current_doctor.split()) > 1 else doctor_last

    rejection_triggers = [
        'another doctor',
        'different doctor',
        'someone else',
        "don't want",
        'not ' + doctor_first,
        'not ' + doctor_last,
    ]

    if any(trigger in text_lower for trigger in rejection_triggers) or (
        (doctor_first in text_lower or doctor_last in text_lower) and is_negative(text_lower)
    ):
        rejected = session.setdefault('rejected_doctors', set())
        rejected.add(current_doctor)
        session['current_doctor_discussed'] = None
        return True

    return False

# NLP Helper Functions
def extract_name(text):
    """Extract name from user input with improved NLP"""
    # Common name patterns
    name_patterns = [
        r"(?:my name is|i am|i'm|this is|it's) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)",
        r"([A-Z][a-z]+(?: [A-Z][a-z]+)*) (?:here|speaking)",
        r"(?:call me|i'm|i am) ([A-Z][a-z]+(?: [A-Z][a-z]+)*)",
    ]
    
    # Check for common greeting patterns with name
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1)
            # Filter out common false positives
            false_positives = ["unable to hear", "looking for", "trying to", "calling about", "interested in", "checking", "inquiring"]
            if not any(fp in name.lower() for fp in false_positives):
                return name
    
    # If no patterns match but text is short and looks like a name
    words = text.strip().split()
    if 1 <= len(words) <= 3 and all(word.isalpha() for word in words):
        # Check if first word is capitalized or can be capitalized
        if words[0][0].isupper() or words[0][0].isalpha():
            name = ' '.join(words)
            # Filter out common false positives
            false_positives = ["unable to hear", "looking for", "trying to", "calling about", "interested in", "checking", "inquiring"]
            if not any(fp in name.lower() for fp in false_positives):
                return name
    
    return None

def extract_service(text):
    """Extract medical service from user input"""
    text = text.lower()
    
    # Define service keywords
    services = {
        "dental": ["dental", "dentist", "teeth", "tooth", "cavity", "filling", "crown", "root canal", "braces", "orthodontist", "gums"],
        "ent": ["ent", "ear", "nose", "throat", "sinus", "hearing", "tonsil", "voice", "snoring", "sleep apnea"],
        "dermatology": ["dermatology", "dermatologist", "skin", "rash", "acne", "mole", "eczema", "psoriasis", "hair loss"],
        "general": ["general", "checkup", "check up", "check-up", "physical", "exam", "consultation", "primary care", "doctor"]
    }
    
    # Check for service mentions
    for service, keywords in services.items():
        for keyword in keywords:
            if keyword in text:
                return service
    
    return None

def extract_time(text):
    """Extract time and date from user input"""
    text = text.lower()
    
    # Check for common time patterns
    day_patterns = [
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        r"(tomorrow|today|next week)",
        r"(january|february|march|april|may|june|july|august|september|october|november|december) (\d{1,2})(?:st|nd|rd|th)?",
        r"(\d{1,2})(?:st|nd|rd|th)? of (january|february|march|april|may|june|july|august|september|october|november|december)"
    ]
    
    time_patterns = [
        r"(\d{1,2})(?::(\d{2}))? ?(am|pm)",
        r"(\d{1,2}) o'?clock",
        r"(morning|afternoon|evening)",
        r"(noon|midnight)"
    ]
    
    day_match = None
    for pattern in day_patterns:
        match = re.search(pattern, text)
        if match:
            day_match = match.group(0)
            break
    
    time_match = None
    for pattern in time_patterns:
        match = re.search(pattern, text)
        if match:
            time_match = match.group(0)
            break
    
    if day_match and time_match:
        return f"{day_match} at {time_match}"
    elif day_match:
        # Default to morning if only day is specified
        return f"{day_match} at 10:00 AM"
    elif time_match:
        # Default to tomorrow if only time is specified
        return f"tomorrow at {time_match}"
    
    return None

def extract_phone(text):
    """Extract phone number from user input"""
    # Remove all non-numeric characters
    digits_only = ''.join(c for c in text if c.isdigit())
    
    # Check for common phone number patterns
    if len(digits_only) >= 9:
        # UAE mobile numbers typically start with 05 and are 10 digits long
        if digits_only.startswith('05') and len(digits_only) >= 10:
            return digits_only[:10]
        # Numbers may also include the country code (971 or 00971)
        elif digits_only.startswith('971') and len(digits_only) >= 12:
            return digits_only[:12]
        elif digits_only.startswith('00971') and len(digits_only) >= 14:
            return digits_only[:14]
    
    # If no clear phone number pattern, return None
    return None

def is_valid_uae_phone(phone):
    """Validate UAE phone number format"""
    # UAE mobile numbers start with 05 and are 10 digits long
    if phone.startswith('05') and len(phone) == 10 and phone.isdigit():
        return True
    # Or they start with +971 or 00971 followed by 9 digits
    elif (phone.startswith('+971') or phone.startswith('00971')) and len(phone) >= 12:
        return True
    # Or they start with 971 followed by 9 digits
    elif phone.startswith('971') and len(phone) >= 12:
        return True
    return False

def format_uae_phone(phone):
    """Format UAE phone number for display"""
    if phone.startswith('05') and len(phone) == 10:
        return f"({phone[:2]}) {phone[2:5]}-{phone[5:]}"
    elif phone.startswith('971'):
        return f"+{phone[:3]} {phone[3:5]} {phone[5:8]}-{phone[8:]}"
    elif phone.startswith('+971'):
        return f"{phone[:4]} {phone[4:6]} {phone[6:9]}-{phone[9:]}"
    return phone

def is_affirmative(text):
    """Check if text indicates affirmative response"""
    text = text.lower()
    affirmative_words = ["yes", "yeah", "yep", "sure", "okay", "ok", "fine", "good", "alright", "correct", "right", "yup", "absolutely", "definitely", "certainly", "indeed", "true", "affirmative", "agreed", "works", "that works"]
    
    for word in affirmative_words:
        if word in text:
            return True
    
    return False

def is_negative(text):
    """Check if text indicates negative response"""
    text = text.lower()
    negative_words = ["no", "nope", "nah", "not", "don't", "cannot", "can't", "won't", "wouldn't", "shouldn't", "never", "negative", "disagree", "incorrect", "wrong", "false", "impossible", "unavailable"]
    
    for word in negative_words:
        if word in text:
            return True
    
    return False

def get_service_category(service):
    """Map service to a category for availability checking"""
    service = service.lower()
    
    if any(keyword in service for keyword in ["dental", "dentist", "teeth"]):
        return "dental"
    elif any(keyword in service for keyword in ["ent", "ear", "nose", "throat"]):
        return "ent"
    elif any(keyword in service for keyword in ["dermatology", "skin"]):
        return "dermatology"
    else:
        return "general"

def check_availability(service_type, preferred_time):
    """Check if the preferred time is available for the service"""
    # For demo purposes, randomly determine availability
    # In a real implementation, this would check a database or calendar
    return random.choice([True, False])

def suggest_alternative_time(service_type, preferred_time, exclude_previous=False):
    """Suggest an alternative time based on service type"""
    # Get available slots for the service type
    available_slots = AVAILABLE_SLOTS.get(service_type, AVAILABLE_SLOTS["general"])
    
    # Filter out the previous suggestion if needed
    if exclude_previous and preferred_time in available_slots:
        available_slots = [slot for slot in available_slots if slot != preferred_time]
    
    # Return a random available slot
    return random.choice(available_slots)

def generate_voice(text, emotion="neutral"):
    """
    Generate voice audio using ElevenLabs API with emotion
    
    Args:
        text: Text to convert to speech
        emotion: Emotional tone for the voice
        
    Returns:
        URL to the generated audio file
    """
    try:
        # Check if we have valid ElevenLabs credentials
        if not ELEVENLABS_API_KEY or not ELEVENLABS_VOICE_ID:
            logger.warning("Missing ElevenLabs credentials, using mock audio")
            return "/static/mock_audio.mp3"
        
        # Add SSML tags for emotion and pauses
        text_with_emotion = add_ssml_tags(text, emotion)
        
        # Call ElevenLabs API
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        # Adjust voice settings based on emotion
        stability, similarity_boost = get_voice_settings(emotion)
        
        data = {
            "text": text_with_emotion,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Save the audio file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"response_{timestamp}.mp3"
            filepath = os.path.join("static", "audio", filename)
            
            # Ensure directory exists
            os.makedirs(os.path.join("static", "audio"), exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            # Return the URL to the audio file
            return f"/static/audio/{filename}"
        else:
            logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
            return "/static/mock_audio.mp3"
            
    except Exception as e:
        logger.error(f"Error generating voice: {str(e)}")
        return "/static/mock_audio.mp3"

def add_ssml_tags(text, emotion):
    """Add SSML tags for emotion and pauses"""
    # Replace fillers with SSML pauses
    for filler in ["um", "uh", "hmm", "well", "let me think", "let me check"]:
        if filler in text:
            text = text.replace(filler, f'<break time="500ms"/>{filler}<break time="300ms"/>')
    
    # Add pauses after punctuation
    text = re.sub(r'\.', '.<break time="500ms"/>', text)
    text = re.sub(r'\?', '?<break time="500ms"/>', text)
    text = re.sub(r'\!', '!<break time="500ms"/>', text)
    text = re.sub(r'\,', ',<break time="300ms"/>', text)
    
    # Wrap in SSML tags
    return text

def get_voice_settings(emotion):
    """Get voice settings based on emotion"""
    settings = {
        "neutral": (0.5, 0.5),
        "friendly": (0.4, 0.7),
        "professional": (0.6, 0.4),
        "reassuring": (0.3, 0.8),
        "apologetic": (0.3, 0.7),
        "confident": (0.7, 0.6),
        "informative": (0.6, 0.5),
        "attentive": (0.4, 0.6),
        "efficient": (0.7, 0.4),
        "amused": (0.3, 0.8),
        "happy": (0.4, 0.8)
    }
    
    return settings.get(emotion, (0.5, 0.5))

if __name__ == '__main__':
    # Create audio directory if it doesn't exist
    audio_dir = os.path.join("static", "audio")
    try:
        # First check if it's a file instead of a directory
        if os.path.exists(audio_dir) and not os.path.isdir(audio_dir):
            # It exists but is not a directory, rename it
            os.rename(audio_dir, audio_dir + "_file")
            logger.info(f"Renamed existing file '{audio_dir}' to '{audio_dir}_file'")
        
        # Now create the directory
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
            logger.info(f"Created directory: {audio_dir}")
    except Exception as e:
        logger.error(f"Error creating audio directory: {str(e)}")
    
    # Create a mock audio file if it doesn't exist
    mock_audio_path = os.path.join("static", "mock_audio.mp3")
    if not os.path.exists(mock_audio_path):
        # This is just a placeholder, in a real implementation you'd have a real audio file
        with open(mock_audio_path, "wb") as f:
            f.write(b"")
    
    # Run the Flask app
    app.run(debug=True)  # Using default localhost
