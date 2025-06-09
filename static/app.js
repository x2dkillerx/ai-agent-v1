// Clinic Voice AI - Web Demo Interface

// Global variables
let sessionId = null;
let isRecording = false;
let mediaRecorder = null;
let audioChunks = [];
let conversationHistory = [];

// DOM elements
document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI event listeners
    document.getElementById('start-call-btn').addEventListener('click', startCall);
    document.getElementById('end-call-btn').addEventListener('click', endCall);
    document.getElementById('toggle-mic-btn').addEventListener('click', toggleMicrophone);
    
    // Disable end call and mic buttons initially
    document.getElementById('end-call-btn').disabled = true;
    document.getElementById('toggle-mic-btn').disabled = true;
});

// Start a new call session
async function startCall() {
    try {
        const response = await fetch('/api/start-call', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        sessionId = data.session_id;
        
        // Update UI
        document.getElementById('start-call-btn').disabled = true;
        document.getElementById('end-call-btn').disabled = false;
        document.getElementById('toggle-mic-btn').disabled = false;
        document.getElementById('call-status').textContent = 'Call Active';
        document.getElementById('call-status').className = 'status-active';
        
        // Add system message to conversation
        addMessageToConversation('system', data.message);
        
        // Synthesize and play the greeting
        synthesizeSpeech(data.message);
        
    } catch (error) {
        console.error('Error starting call:', error);
        alert('Failed to start call. Please try again.');
    }
}

// End the current call session
function endCall() {
    // In a real implementation, this would notify the server
    
    // Reset session state
    sessionId = null;
    stopRecording();
    
    // Update UI
    document.getElementById('start-call-btn').disabled = false;
    document.getElementById('end-call-btn').disabled = true;
    document.getElementById('toggle-mic-btn').disabled = true;
    document.getElementById('mic-status').textContent = 'Microphone Off';
    document.getElementById('mic-status').className = 'status-inactive';
    document.getElementById('call-status').textContent = 'Call Ended';
    document.getElementById('call-status').className = 'status-inactive';
    
    // Add end message to conversation
    addMessageToConversation('system', 'Call ended. Thank you for using Noor Medical Clinic Voice AI.');
}

// Toggle microphone recording
async function toggleMicrophone() {
    if (!sessionId) {
        alert('Please start a call first.');
        return;
    }
    
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// Start recording audio from microphone
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            // In a real implementation, this would send audio to Whisper API
            // For demo, we'll use a text input to simulate speech recognition
            const transcript = prompt('Simulate speech recognition by entering what you would say:');
            
            if (transcript && transcript.trim()) {
                // Add user message to conversation
                addMessageToConversation('user', transcript);
                
                // Process the transcript
                await processTranscript(transcript);
            }
        };
        
        mediaRecorder.start();
        isRecording = true;
        
        // Update UI
        document.getElementById('mic-status').textContent = 'Microphone Active';
        document.getElementById('mic-status').className = 'status-active';
        document.getElementById('toggle-mic-btn').textContent = 'Stop Speaking';
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        alert('Failed to access microphone. Please check permissions and try again.');
    }
}

// Stop recording audio
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        document.getElementById('mic-status').textContent = 'Microphone Off';
        document.getElementById('mic-status').className = 'status-inactive';
        document.getElementById('toggle-mic-btn').textContent = 'Start Speaking';
    }
}

// Process transcribed speech
async function processTranscript(transcript) {
    try {
        const response = await fetch('/api/process-speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: sessionId,
                transcript: transcript
            })
        });
        
        const data = await response.json();
        
        // Add system message to conversation
        addMessageToConversation('system', data.message);
        
        // Synthesize and play the response
        synthesizeSpeech(data.message);
        
        // Check if call should end
        if (data.state === 'end_call') {
            setTimeout(endCall, 5000); // End call after response is played
        }
        
    } catch (error) {
        console.error('Error processing speech:', error);
        alert('Failed to process speech. Please try again.');
    }
}

// Add message to conversation history and UI
function addMessageToConversation(role, text) {
    const timestamp = new Date().toISOString();
    
    // Add to history array
    conversationHistory.push({
        role: role,
        text: text,
        timestamp: timestamp
    });
    
    // Add to UI
    const conversationDiv = document.getElementById('conversation');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;
    
    const textSpan = document.createElement('span');
    textSpan.textContent = text;
    
    messageDiv.appendChild(textSpan);
    conversationDiv.appendChild(messageDiv);
    
    // Scroll to bottom
    conversationDiv.scrollTop = conversationDiv.scrollHeight;
}

// Synthesize speech (mock implementation)
function synthesizeSpeech(text) {
    // In a real implementation, this would call ElevenLabs API
    console.log('Synthesizing speech:', text);
    
    // For demo purposes, we'll use the browser's built-in speech synthesis
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9; // Slightly slower for clarity
    utterance.pitch = 1.0;
    
    // Try to find a female voice
    const voices = window.speechSynthesis.getVoices();
    const femaleVoice = voices.find(voice => voice.name.includes('female') || voice.name.includes('woman'));
    if (femaleVoice) {
        utterance.voice = femaleVoice;
    }
    
    window.speechSynthesis.speak(utterance);
}

// Get appointment data (for demo purposes)
async function getAppointments() {
    try {
        const response = await fetch('/api/get-appointments');
        const data = await response.json();
        
        // Display appointments in console for demo
        console.log('Current appointments:', data);
        
    } catch (error) {
        console.error('Error fetching appointments:', error);
    }
}
