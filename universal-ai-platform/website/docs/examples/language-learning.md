# Language Learning Example

This example demonstrates how to build an interactive language learning application using the Universal AI Platform with the language learning adapter.

## Overview

The language learning example creates an AI tutor that helps users practice conversation in their target language. It features:

- **Adaptive Conversation**: Adjusts to user's proficiency level
- **Pronunciation Feedback**: Voice-enabled practice sessions
- **Topic Guidance**: Structured conversation topics
- **Progress Tracking**: Monitors learning progress

## Quick Start

### Running the Demo

```bash
# Navigate to the language learning demo
cd demos/language_learning

# Install dependencies (if needed)
pip install -r requirements.txt

# Run the application
python app.py
```

The application will start on `http://localhost:5001`.

### Basic Usage

```python
from universal_ai_sdk import create_simple_agent

# Create Spanish tutor
session = create_simple_agent(
    instructions="You are a friendly Spanish tutor",
    capabilities=["text", "voice"],
    business_logic_adapter="languagelearning",
    custom_settings={
        "target_language": "Spanish",
        "proficiency_level": "beginner",
        "conversation_topics": ["greetings", "family", "food"]
    }
)

# Start conversation
session.send_message("Hola! ¿Cómo te llamas?")
response = session.wait_for_response()
print(f"Tutor: {response.content}")
```

## Complete Implementation

### Backend Application (app.py)

```python
from flask import Flask, render_template, request, jsonify
from universal_ai_sdk import UniversalAIClient, AgentConfig
import json
import uuid

app = Flask(__name__)

class LanguageLearningApp:
    def __init__(self):
        self.client = UniversalAIClient()
        self.active_sessions = {}
        self.user_progress = {}
    
    def create_tutor_session(self, user_id, target_language, proficiency_level):
        """Create a new language tutor session"""
        config = AgentConfig(
            instructions=f"""You are an experienced {target_language} tutor. 
            Your role is to help the user practice conversation in {target_language}.
            
            Guidelines:
            - Keep conversations natural and engaging
            - Gently correct mistakes
            - Encourage the user to speak more
            - Ask follow-up questions to continue the conversation
            - Adapt to the user's proficiency level
            
            Current student level: {proficiency_level}
            """,
            capabilities=["text", "voice"],
            business_logic_adapter="languagelearning",
            custom_settings={
                "target_language": target_language,
                "proficiency_level": proficiency_level,
                "conversation_topics": self._get_topics_for_level(proficiency_level),
                "correction_style": "gentle",
                "encouragement_level": "high"
            },
            client_id=user_id
        )
        
        session = self.client.create_agent(config)
        self.active_sessions[user_id] = session.session_id
        
        return session.session_id
    
    def _get_topics_for_level(self, level):
        """Get conversation topics based on proficiency level"""
        topics = {
            "beginner": ["greetings", "family", "food", "numbers", "colors"],
            "intermediate": ["travel", "hobbies", "work", "weather", "shopping"],
            "advanced": ["politics", "culture", "literature", "current_events", "philosophy"]
        }
        return topics.get(level, topics["beginner"])
    
    def send_message(self, user_id, message):
        """Send message to tutor"""
        session_id = self.active_sessions.get(user_id)
        if not session_id:
            raise ValueError("No active session for user")
        
        self.client.send_message(session_id, message)
        return self.client.get_messages(session_id)
    
    def get_progress(self, user_id):
        """Get user's learning progress"""
        return self.user_progress.get(user_id, {
            "sessions_completed": 0,
            "total_messages": 0,
            "current_level": "beginner",
            "topics_covered": []
        })
    
    def end_session(self, user_id):
        """End tutor session"""
        session_id = self.active_sessions.get(user_id)
        if session_id:
            self.client.close_session(session_id)
            del self.active_sessions[user_id]

# Initialize the app
language_app = LanguageLearningApp()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_session', methods=['POST'])
def start_session():
    data = request.json
    user_id = data.get('user_id', str(uuid.uuid4()))
    target_language = data.get('target_language', 'Spanish')
    proficiency_level = data.get('proficiency_level', 'beginner')
    
    try:
        session_id = language_app.create_tutor_session(
            user_id, target_language, proficiency_level
        )
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_id': user_id,
            'message': f'{target_language} tutor session started!'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')
    
    try:
        messages = language_app.send_message(user_id, message)
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/progress/<user_id>')
def get_progress(user_id):
    progress = language_app.get_progress(user_id)
    return jsonify(progress)

@app.route('/api/end_session', methods=['POST'])
def end_session():
    data = request.json
    user_id = data.get('user_id')
    
    language_app.end_session(user_id)
    return jsonify({'success': True, 'message': 'Session ended'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

### Frontend Interface (templates/index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Language Learning AI Tutor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: #4A90E2;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .setup-panel {
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        
        .setup-panel.hidden {
            display: none;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        select, input, button {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        
        button {
            background: #4A90E2;
            color: white;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #357ABD;
        }
        
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 12px;
            max-width: 80%;
        }
        
        .user-message {
            background: #4A90E2;
            color: white;
            margin-left: auto;
        }
        
        .tutor-message {
            background: white;
            border: 1px solid #ddd;
        }
        
        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        
        .message-input {
            flex: 1;
        }
        
        .send-btn {
            width: auto;
            padding: 10px 20px;
        }
        
        .progress-panel {
            padding: 20px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        
        .progress-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌟 AI Language Tutor</h1>
            <p>Practice conversation with your personal AI tutor</p>
        </div>
        
        <!-- Setup Panel -->
        <div id="setupPanel" class="setup-panel">
            <h3>Setup Your Learning Session</h3>
            
            <div class="form-group">
                <label for="languageSelect">Target Language:</label>
                <select id="languageSelect">
                    <option value="Spanish">Spanish</option>
                    <option value="French">French</option>
                    <option value="German">German</option>
                    <option value="Italian">Italian</option>
                    <option value="Portuguese">Portuguese</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="levelSelect">Proficiency Level:</label>
                <select id="levelSelect">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="nameInput">Your Name (optional):</label>
                <input type="text" id="nameInput" placeholder="Enter your name">
            </div>
            
            <button onclick="startSession()">Start Learning Session</button>
        </div>
        
        <!-- Chat Interface -->
        <div id="chatInterface" class="chat-container" style="display: none;">
            <div id="messages"></div>
        </div>
        
        <!-- Input Area -->
        <div id="inputArea" class="input-area" style="display: none;">
            <input type="text" id="messageInput" class="message-input" 
                   placeholder="Type your message in your target language...">
            <button onclick="sendMessage()" class="send-btn">Send</button>
        </div>
        
        <!-- Progress Panel -->
        <div id="progressPanel" class="progress-panel" style="display: none;">
            <h4>Session Progress</h4>
            <div class="progress-item">
                <span>Messages Exchanged:</span>
                <span id="messageCount">0</span>
            </div>
            <div class="progress-item">
                <span>Session Duration:</span>
                <span id="sessionDuration">0 minutes</span>
            </div>
            <button onclick="endSession()" style="margin-top: 10px; background: #dc3545;">
                End Session
            </button>
        </div>
    </div>

    <script>
        let currentUserId = null;
        let sessionId = null;
        let messageCount = 0;
        let sessionStartTime = null;
        
        async function startSession() {
            const language = document.getElementById('languageSelect').value;
            const level = document.getElementById('levelSelect').value;
            const name = document.getElementById('nameInput').value || 'Student';
            
            try {
                const response = await fetch('/api/start_session', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        target_language: language,
                        proficiency_level: level,
                        user_name: name
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentUserId = data.user_id;
                    sessionId = data.session_id;
                    sessionStartTime = new Date();
                    
                    // Show chat interface
                    document.getElementById('setupPanel').classList.add('hidden');
                    document.getElementById('chatInterface').style.display = 'block';
                    document.getElementById('inputArea').style.display = 'flex';
                    document.getElementById('progressPanel').style.display = 'block';
                    
                    // Add welcome message
                    addMessage('tutor', `¡Hola ${name}! I'm your ${language} tutor. Let's start practicing! How are you today?`);
                    
                    // Start duration timer
                    setInterval(updateSessionDuration, 60000); // Update every minute
                } else {
                    alert('Error starting session: ' + data.error);
                }
            } catch (error) {
                alert('Network error: ' + error.message);
            }
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            addMessage('user', message);
            input.value = '';
            messageCount++;
            
            try {
                const response = await fetch('/api/send_message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        user_id: currentUserId,
                        message: message
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Find the latest tutor response
                    const messages = data.messages;
                    const lastMessage = messages[messages.length - 1];
                    
                    if (lastMessage.type === 'agent') {
                        addMessage('tutor', lastMessage.content);
                        messageCount++;
                    }
                    
                    updateProgress();
                } else {
                    addMessage('system', 'Error: ' + data.error);
                }
            } catch (error) {
                addMessage('system', 'Network error: ' + error.message);
            }
        }
        
        function addMessage(sender, content) {
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            
            if (sender === 'tutor') {
                messageDiv.innerHTML = `<strong>Tutor:</strong> ${content}`;
            } else if (sender === 'user') {
                messageDiv.innerHTML = `<strong>You:</strong> ${content}`;
            } else {
                messageDiv.innerHTML = content;
                messageDiv.style.background = '#ffebee';
                messageDiv.style.color = '#c62828';
            }
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function updateProgress() {
            document.getElementById('messageCount').textContent = messageCount;
        }
        
        function updateSessionDuration() {
            if (sessionStartTime) {
                const now = new Date();
                const minutes = Math.floor((now - sessionStartTime) / 60000);
                document.getElementById('sessionDuration').textContent = `${minutes} minutes`;
            }
        }
        
        async function endSession() {
            if (confirm('Are you sure you want to end this learning session?')) {
                try {
                    await fetch('/api/end_session', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            user_id: currentUserId
                        })
                    });
                    
                    alert('Session ended. Great job practicing!');
                    location.reload();
                } catch (error) {
                    alert('Error ending session: ' + error.message);
                }
            }
        }
        
        // Send message on Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
```

## Advanced Features

### Voice Integration

```python
# Add to app.py for voice capabilities
import speech_recognition as sr
from gtts import gTTS
import io
import base64

class VoiceLanguageTutor(LanguageLearningApp):
    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
    
    def process_voice_input(self, audio_data, target_language='es'):
        """Process voice input and return text"""
        try:
            # Convert audio to text
            text = self.recognizer.recognize_google(
                audio_data, 
                language=target_language
            )
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand the audio"
        except sr.RequestError as e:
            return f"Error with speech recognition: {e}"
    
    def generate_speech(self, text, language='es'):
        """Generate speech from text"""
        try:
            tts = gTTS(text=text, lang=language, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Return base64 encoded audio
            audio_base64 = base64.b64encode(audio_buffer.read()).decode()
            return audio_base64
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

@app.route('/api/process_voice', methods=['POST'])
def process_voice():
    """Handle voice input from user"""
    try:
        audio_file = request.files['audio']
        target_language = request.form.get('language', 'es')
        
        # Convert to AudioData format
        with sr.AudioFile(audio_file) as source:
            audio_data = language_app.recognizer.record(source)
        
        # Process voice
        text = language_app.process_voice_input(audio_data, target_language)
        
        return jsonify({
            'success': True,
            'transcribed_text': text
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

### Progress Analytics

```python
class ProgressTracker:
    def __init__(self):
        self.user_data = {}
    
    def track_conversation(self, user_id, message, response, language):
        """Track conversation for progress analysis"""
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'total_messages': 0,
                'languages': {},
                'session_times': [],
                'vocabulary_used': set(),
                'grammar_points': []
            }
        
        data = self.user_data[user_id]
        data['total_messages'] += 1
        
        if language not in data['languages']:
            data['languages'][language] = {
                'messages': 0,
                'complexity_scores': [],
                'topics_covered': set()
            }
        
        data['languages'][language]['messages'] += 1
        
        # Analyze message complexity (simplified)
        complexity = self._analyze_complexity(message)
        data['languages'][language]['complexity_scores'].append(complexity)
    
    def _analyze_complexity(self, text):
        """Simple complexity analysis"""
        words = text.split()
        sentences = text.split('.')
        
        # Basic complexity score
        avg_sentence_length = len(words) / max(len(sentences), 1)
        unique_words = len(set(words.lower()))
        
        return min(avg_sentence_length + unique_words / 10, 10)
    
    def get_progress_report(self, user_id):
        """Generate progress report"""
        if user_id not in self.user_data:
            return {'error': 'No data found for user'}
        
        data = self.user_data[user_id]
        
        report = {
            'total_messages': data['total_messages'],
            'languages_practiced': list(data['languages'].keys()),
            'improvement_trend': self._calculate_improvement(data),
            'recommendations': self._generate_recommendations(data)
        }
        
        return report
    
    def _calculate_improvement(self, data):
        """Calculate improvement trend"""
        trends = {}
        for lang, lang_data in data['languages'].items():
            scores = lang_data['complexity_scores']
            if len(scores) >= 5:
                recent_avg = sum(scores[-5:]) / 5
                early_avg = sum(scores[:5]) / 5
                trends[lang] = recent_avg - early_avg
            else:
                trends[lang] = 0
        return trends
    
    def _generate_recommendations(self, data):
        """Generate learning recommendations"""
        recommendations = []
        
        for lang, lang_data in data['languages'].items():
            avg_complexity = sum(lang_data['complexity_scores']) / len(lang_data['complexity_scores'])
            
            if avg_complexity < 3:
                recommendations.append(f"Try using more complex sentences in {lang}")
            elif avg_complexity > 7:
                recommendations.append(f"Great progress in {lang}! Consider advanced topics")
            else:
                recommendations.append(f"Good steady progress in {lang}")
        
        return recommendations
```

## Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  language-tutor:
    build: .
    ports:
      - "5001:5001"
    environment:
      - UNIVERSAL_AI_BASE_URL=http://host.docker.internal:8000
    depends_on:
      - ai-platform
  
  ai-platform:
    build: ../../
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
```

### Production Configuration

```python
# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    UNIVERSAL_AI_URL = os.environ.get('UNIVERSAL_AI_URL') or 'http://localhost:8000'
    UNIVERSAL_AI_API_KEY = os.environ.get('UNIVERSAL_AI_API_KEY')
    
    # Session settings
    SESSION_TIMEOUT = 30 * 60  # 30 minutes
    MAX_SESSIONS_PER_USER = 3
    
    # Language settings
    SUPPORTED_LANGUAGES = {
        'Spanish': 'es',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portuguese': 'pt'
    }
    
    # Feature flags
    VOICE_ENABLED = os.environ.get('VOICE_ENABLED', 'false').lower() == 'true'
    PROGRESS_TRACKING = os.environ.get('PROGRESS_TRACKING', 'true').lower() == 'true'
```

## Usage Tips

### Best Practices

1. **Start Simple**: Begin with text-only conversations before adding voice
2. **Set Clear Goals**: Define specific learning objectives for each session
3. **Regular Practice**: Consistent short sessions are better than long infrequent ones
4. **Track Progress**: Monitor improvement through conversation complexity
5. **Use Real Scenarios**: Practice practical conversations for real-world use

### Common Issues

1. **Session Timeouts**: Implement proper session management
2. **Voice Quality**: Ensure good audio input for voice features
3. **Language Detection**: Be explicit about target language settings
4. **Error Handling**: Provide graceful fallbacks for API failures

---

**Next**: Try the [Emergency Services Example](/examples/language-learning) or learn about [Custom Adapters](/examples/language-learning).