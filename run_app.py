#!/usr/bin/env python3
"""
Complete working integration of UI + AI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import sys
from dotenv import load_dotenv
import threading
import subprocess
import time
import uuid
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Add AI module paths correctly - each module in its own subdirectory
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'career-guidance-ai'))
sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'course-recommender'))
sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'job-scraper'))
sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'resume-generator'))
sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'learning-roadmap'))

print("🔧 Loading AI modules...")

# Import modules with proper error handling
try:
    from ai_course_core import CourseRecommender, get_course_recommendations
    print("✅ Course recommender loaded")
except Exception as e:
    print(f"❌ Course recommender error: {e}")
    CourseRecommender = None
    get_course_recommendations = None

try:
    from ai_roadmap_core import AIRoadmapGenerator  
    print("✅ Roadmap generator loaded")
except Exception as e:
    print(f"❌ Roadmap generator error: {e}")
    AIRoadmapGenerator = None

try:
    from ai_job_scraper import AIJobScraper
    print("✅ Job scraper loaded")
except Exception as e:
    print(f"❌ Job scraper error: {e}")
    AIJobScraper = None

# Import career guidance with forced reload
AICareerGuidance = None
try:
    # Force reload by clearing any cached modules
    if 'ai_career_guidance' in sys.modules:
        del sys.modules['ai_career_guidance']
    
    from ai_career_guidance import AICareerGuidance
    print("✅ Career guidance loaded")
    
    # Verify the function signature immediately after import
    import inspect
    sig = inspect.signature(AICareerGuidance().get_complete_analysis)
    print(f"✅ Verified function signature: {sig}")
    
except Exception as e:
    print(f"❌ Career guidance error: {e}")
    AICareerGuidance = None

try:
    from ai_resume_core import AIResumeCore
    print("✅ Resume generator loaded")
except Exception as e:
    print(f"❌ Resume generator error: {e}")
    AIResumeCore = None

# Import AVA Voice Interview System
try:
    sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'AVA_voice'))
    
    # Set the correct API key for voice interview
    os.environ["GOOGLE_API_KEY"] = os.getenv('GEMINI_API_KEY')
    
    from voice_final import OptimizedVoiceInterview
    print("✅ AVA Voice Interview loaded")
except Exception as e:
    print(f"❌ AVA Voice Interview error: {e}")
    OptimizedVoiceInterview = None

# Import WebSocket Voice Interview Handler
try:
    from voice_interview_handler import WebSocketVoiceInterviewHandler
    voice_handler = WebSocketVoiceInterviewHandler(socketio)
    print("✅ WebSocket Voice Interview Handler loaded")
except Exception as e:
    print(f"❌ WebSocket Voice Interview Handler error: {e}")
    voice_handler = None

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'AI API running'})

@app.route('/api/courses/recommend', methods=['POST'])
def recommend_courses():
    try:
        if get_course_recommendations is None:
            return jsonify({'success': False, 'error': 'Course recommender module not available'}), 500
            
        data = request.get_json()
        print(f"🎓 Generating course recommendations for: {data.get('interests', '')}")
        
        # Use the main API function from the course recommender
        result = get_course_recommendations(
            interests=data.get('interests', ''),
            skills=data.get('skills', ''),
            goals=data.get('goals', '')
        )
        
        print(f"✅ Course recommendations generated: {result.get('success', False)}")
        if result.get('success'):
            courses_count = len(result.get('data', {}).get('course_recommendations', []))
            print(f"   🎓 Found {courses_count} courses")
            
        return jsonify(result)
    except Exception as e:
        print(f"❌ Course recommendation error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/roadmap/create', methods=['POST'])  
def create_roadmap():
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        current_skills = data.get('currentSkills', '')
        goals = data.get('goals', '')
        
        print(f"🎯 Creating integrated roadmap + courses for: {subject}")
        
        # Try to use the enhanced course recommender first
        if get_course_recommendations is not None:
            print("✅ Using CourseRecommender for integrated roadmap+courses")
            
            # Use the course recommender which generates both roadmap and courses
            result = get_course_recommendations(
                interests=subject,
                skills=current_skills,
                goals=goals
            )
            
            if result.get('success'):
                print(f"✅ Integrated roadmap+courses generated successfully")
                courses_count = len(result.get('data', {}).get('course_recommendations', []))
                steps_count = len(result.get('data', {}).get('roadmap', {}).get('steps', []))
                print(f"   📚 {steps_count} learning steps")
                print(f"   🎓 {courses_count} courses with URLs")
                return jsonify(result)
            else:
                print("⚠️ Course recommender failed, falling back to basic roadmap")
        
        # Fallback to basic roadmap generator if course recommender fails
        if AIRoadmapGenerator is not None:
            print("⚠️ Using fallback AIRoadmapGenerator")
            generator = AIRoadmapGenerator()
            result = generator.create_complete_plan(
                subject=subject,
                current_skills=current_skills,
                goals=goals
            )
            return jsonify({'success': True, 'data': result})
        
        # If both methods fail
        return jsonify({
            'success': False, 
            'error': 'No roadmap generation modules available'
        }), 500
        
    except Exception as e:
        print(f"❌ Roadmap creation error: {e}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/search', methods=['POST'])
def search_jobs():
    try:
        if AIJobScraper is None:
            return jsonify({'success': False, 'error': 'Job scraper module not available'}), 500
            
        print("🔍 Job search request received")
        data = request.get_json()
        print(f"📝 Request data: {data}")
        
        scraper = AIJobScraper()
        result = scraper.search_jobs(
            query=data.get('query', ''),
            location=data.get('location', 'Remote')
        )
        
        print(f"✅ Job search completed: Found {result.get('total_found', 0)} jobs")
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print(f"❌ Job search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/career/analyze', methods=['POST'])
def analyze_career():
    try:
        # Check if AICareerGuidance is available
        if AICareerGuidance is None:
            return jsonify({
                'success': False, 
                'error': 'Career guidance module is not available. Please check the server logs for import errors.'
            }), 500
        
        data = request.get_json()
        print(f"📝 Received data: {data}")  # Debug log
        
        guidance = AICareerGuidance()
        
        # Debug: Check the function signature
        import inspect
        sig = inspect.signature(guidance.get_complete_analysis)
        print(f"🔍 Function signature: {sig}")  # Debug log
        
        # Only use domain interest and resume file - simplified inputs
        print("🚀 Calling get_complete_analysis with simplified parameters...")
        result = guidance.get_complete_analysis(
            domain_interest=data.get('domainInterest', ''),
            resume_path=data.get('resumeFile')  # Handle resume file if provided
        )
        print("✅ Career analysis completed successfully")
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        print(f"❌ Career analysis error: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/resume/generate', methods=['POST'])
def generate_resume():
    try:
        if AIResumeCore is None:
            return jsonify({'success': False, 'error': 'Resume generator module not available'}), 500
            
        data = request.get_json()
        generator = AIResumeCore()
        
        user_data = {
            'full_name': data.get('personalInfo', {}).get('fullName', ''),
            'email': data.get('personalInfo', {}).get('email', ''),
            'phone': data.get('personalInfo', {}).get('phone', ''),
            'location': data.get('personalInfo', {}).get('location', ''),
            'summary': data.get('personalInfo', {}).get('summary', ''),
            'experience': '\n'.join([f"{exp.get('position', '')} at {exp.get('company', '')}" for exp in data.get('experience', [])]),
            'education': '\n'.join([f"{edu.get('degree', '')} - {edu.get('institution', '')}" for edu in data.get('education', [])]),
            'skills': ', '.join(data.get('skills', []))
        }
        
        result = generator.generate_resume(user_data, data.get('jobDescription', ''))
        return jsonify({'success': True, 'data': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interview/voice', methods=['POST'])
def start_voice_interview():
    try:
        data = request.get_json()
        job_description = data.get('jobDescription', '')
        
        print(f"🎙️ Voice interview request received")
        print(f"📝 Job description length: {len(job_description)}")
        
        # Simple response without trying to import the problematic module
        result = {
            'session_id': f"interview_{int(time.time())}",
            'status': 'ready',
            'interview_structure': {
                'total_questions': 15,
                'fixed_questions': [
                    'Introduce yourself',
                    'Why are you interested in this role and company?',
                    'What\'s your biggest weakness and how are you improving it?'
                ]
            }
        }
        
        print("✅ Voice interview session prepared successfully")
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print(f"❌ Voice interview error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/interview/voice/start', methods=['POST'])
def execute_voice_interview():
    try:
        # Return terminal execution instructions
        result = {
            'status': 'terminal_execution',
            'instructions': [
                '1. Open terminal in ai-modules/AVA_voice/',
                '2. Run: python3 voice_final.py',
                '3. Follow voice prompts for interview',
                '4. Results saved automatically'
            ],
            'note': 'Voice interview runs in terminal for microphone access'
        }
        
        print("✅ Voice interview execution instructions provided")
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print(f"❌ Voice interview execution error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# WebSocket Event Handlers for Live Voice Interview
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"✅ Client connected: {request.sid}")
    emit('connected', {'status': 'connected', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('create_interview_session')
def handle_create_session(data):
    """Create a new voice interview session"""
    try:
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = str(uuid.uuid4())
        job_description = data.get('jobDescription', '')
        resume_path = data.get('resumePath', 'resume.pdf')

        print(f"🎙️ Creating interview session: {session_id}")

        result = voice_handler.create_session(session_id, job_description, resume_path)

        if result['success']:
            join_room(session_id)
            emit('session_created', {
                'session_id': session_id,
                'resume_data': result['resume_data'],
                'total_questions': result['total_questions'],
                'fixed_questions': result['fixed_starter_questions']
            })
            print(f"✅ Session created successfully: {session_id}")
        else:
            emit('error', {'message': result['error']})
            print(f"❌ Failed to create session: {result['error']}")

    except Exception as e:
        print(f"❌ Error creating session: {e}")
        emit('error', {'message': str(e)})

@socketio.on('get_next_question')
def handle_get_question(data):
    """Get the next interview question"""
    try:
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return

        print(f"📝 Getting next question for session: {session_id}")

        result = voice_handler.get_next_question(session_id)

        if result['success']:
            emit('next_question', result, room=session_id)
            print(f"✅ Question {result['question_number']} sent")
        else:
            emit('error', {'message': result['error'], 'completed': result.get('completed', False)}, room=session_id)

    except Exception as e:
        print(f"❌ Error getting question: {e}")
        emit('error', {'message': str(e)})

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """Process incoming audio chunk"""
    try:
        print(f"🎵 Received audio_chunk event")
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = data.get('session_id')
        audio_b64 = data.get('audio_data')
        mime_type = data.get('mime_type', 'audio/webm')  # Default to webm if not provided

        print(f"🔑 Session ID: {session_id}")
        print(f"📊 Audio data length: {len(audio_b64) if audio_b64 else 0}")
        print(f"🎧 MIME type: {mime_type}")

        if not session_id or not audio_b64:
            emit('error', {'message': 'Session ID and audio data required'})
            return

        # Decode audio data
        audio_bytes = base64.b64decode(audio_b64)

        # Process audio chunk with MIME type
        print(f"🎤 Processing audio chunk...")
        voice_handler.process_audio_chunk(session_id, audio_bytes, mime_type)
        print(f"✅ Audio chunk processed successfully")

        # Acknowledge receipt
        emit('audio_received', {'status': 'received'}, room=session_id)

    except Exception as e:
        print(f"❌ Error processing audio chunk: {e}")
        emit('error', {'message': str(e)})

@socketio.on('finish_recording')
def handle_finish_recording(data):
    """Process complete audio recording"""
    try:
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return

        print(f"🎤 Finishing recording for session: {session_id}")

        result = voice_handler.finish_recording(session_id)

        if result['success']:
            emit('recording_processed', result, room=session_id)
            print(f"✅ Recording processed for question {result['question_number']}")

            # Start polling for transcription
            emit('transcription_started', {'question_number': result['question_number']}, room=session_id)
        else:
            emit('error', {'message': result['error']}, room=session_id)

    except Exception as e:
        print(f"❌ Error finishing recording: {e}")
        emit('error', {'message': str(e)})

@socketio.on('get_transcription')
def handle_get_transcription(data):
    """Get transcription for the current answer"""
    try:
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return

        result = voice_handler.get_transcription(session_id)

        if result['success']:
            emit('transcription_ready', result, room=session_id)
            print(f"✅ Transcription ready for question {result['question_number']}")
        else:
            emit('transcription_pending', {'message': result['error']}, room=session_id)

    except Exception as e:
        print(f"❌ Error getting transcription: {e}")
        emit('error', {'message': str(e)})

@socketio.on('get_session_status')
def handle_get_status(data):
    """Get current session status"""
    try:
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return

        result = voice_handler.get_session_status(session_id)

        if result['success']:
            emit('session_status', result, room=session_id)
        else:
            emit('error', {'message': result['error']})

    except Exception as e:
        print(f"❌ Error getting session status: {e}")
        emit('error', {'message': str(e)})

@socketio.on('end_interview')
def handle_end_interview(data):
    """End the interview session"""
    try:
        if voice_handler is None:
            emit('error', {'message': 'Voice interview handler not available'})
            return

        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return

        print(f"🏁 Ending interview session: {session_id}")

        result = voice_handler.end_session(session_id)

        if result['success']:
            emit('interview_completed', result, room=session_id)
            leave_room(session_id)
            print(f"✅ Interview completed: {result['total_questions_asked']} questions")
        else:
            emit('error', {'message': result['error']})

    except Exception as e:
        print(f"❌ Error ending interview: {e}")
        emit('error', {'message': str(e)})

def start_frontend():
    """Start the React frontend"""
    time.sleep(3)  # Wait for API to start
    print("🎨 Starting React frontend...")
    os.chdir('web-ui')
    subprocess.run(['npm', 'run', 'dev'])

if __name__ == '__main__':
    print("🚀 Starting Unified AI Tools")
    print(f"🔑 Using API keys from .env")
    
    # Start frontend in separate thread
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    print("📡 Starting API server with WebSocket support on http://localhost:8001")
    socketio.run(app, debug=False, host='0.0.0.0', port=8001)
