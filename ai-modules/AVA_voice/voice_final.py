import asyncio
import threading
import queue
import concurrent.futures
import time
import json
import re
import os
import tempfile
import wave
import subprocess
import PyPDF2
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
import google.generativeai as text_genai
import pyaudio
import keyboard
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure APIs
GEMINI_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
text_genai.configure(api_key=GEMINI_API_KEY)

# Audio settings
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

class OptimizedVoiceInterview:
    """High-performance voice interview system with fixed starter questions"""
    
    def __init__(self):
        # Core models
        self.text_model = text_genai.GenerativeModel('gemini-1.5-pro')
        self.client = genai.Client()
        
        # Interview state
        self.resume_data = {}
        self.job_data = {}
        self.qa_history = []
        self.questions_asked = 0
        self.max_questions = 15
        
        # Enhanced question tracking for diversity
        self.question_types_used = {
            "introduction": [],
            "technical_skills": [],
            "projects_deep_dive": [],
            "certifications": [],
            "behavioral": [],
            "situational": [],
            "leadership": [],
            "problem_solving": [],
            "communication": [],
            "career_goals": []
        }
        
        self.covered_topics = set()
        self.projects_discussed = set()
        self.skills_discussed = set()
        
        # Performance optimization queues
        self.audio_queue = queue.Queue()
        self.transcription_queue = queue.Queue()
        self.question_queue = queue.Queue()
        
        # Thread pools for parallel processing
        self.tts_executor = concurrent.futures.ThreadPoolExecutor(max_workers=3, thread_name_prefix="TTS")
        self.transcribe_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="Transcribe")
        
        # FIXED first 3 questions - always the same for zero lag
        self.fixed_starter_questions = [
            {"text": "Introduce yourself.", "type": "introduction", "order": 1},
            {"text": "Why are you interested in this role and company?", "type": "behavioral", "order": 2},
            {"text": "What's your biggest weakness and how are you improving it?", "type": "behavioral", "order": 3}
        ]
        
        # Recording state
        self.is_recording = False
        
    def extract_pdf_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            return ""
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume using text Gemini API"""
        prompt = f"""
        Analyze this resume and extract structured information as JSON:
        
        {resume_text}
        
        Return ONLY a JSON object with this exact structure:
        {{
            "name": "candidate name",
            "skills": ["technical skill 1", "technical skill 2", "skill 3", "skill 4", "skill 5"],
            "certifications": ["certification 1", "certification 2"],
            "projects": [
                {{
                    "name": "project name",
                    "description": "brief description",
                    "technologies": ["tech1", "tech2"],
                    "key_features": ["feature1", "feature2"]
                }}
            ],
            "experience": [
                {{
                    "company": "company name",
                    "role": "job title",
                    "duration": "time period",
                    "achievements": ["achievement1", "achievement2"]
                }}
            ],
            "education": [
                {{
                    "degree": "degree name",
                    "institution": "school name",
                    "year": "graduation year"
                }}
            ],
            "soft_skills": ["leadership", "teamwork", "communication"]
        }}
        """
        
        try:
            response = self.text_model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse resume"}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description"""
        prompt = f"""
        Analyze this job description and extract key requirements as JSON:
        
        {job_description}
        
        Return ONLY a JSON object:
        {{
            "job_title": "job title",
            "required_skills": ["skill1", "skill2", "skill3", "skill4"],
            "preferred_skills": ["pref1", "pref2"],
            "experience_level": "junior/mid/senior",
            "key_responsibilities": ["responsibility1", "responsibility2"],
            "soft_skills_needed": ["teamwork", "leadership", "communication"],
            "interview_focus_areas": ["area1", "area2", "area3"]
        }}
        """
        
        try:
            response = self.text_model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse job description"}
        except Exception as e:
            return {"error": str(e)}
    
    def determine_next_question_type(self) -> str:
        """Smart question type selection for maximum variety (for questions 4-15)"""
        # Count how many of each type we've used
        type_counts = {k: len(v) for k, v in self.question_types_used.items()}
        
        # Questions 4-15 strategy (first 3 are fixed)
        if self.questions_asked <= 6:
            # Early questions: technical skills and projects
            available_types = ["technical_skills", "projects_deep_dive"]
            return min(available_types, key=lambda x: type_counts[x])
        elif self.questions_asked <= 10:
            # Middle questions: certifications and problem-solving
            available_types = ["problem_solving", "certifications", "situational"]
            return min(available_types, key=lambda x: type_counts[x])
        elif self.questions_asked <= 13:
            # Later questions: leadership and communication
            available_types = ["leadership", "communication"]
            return min(available_types, key=lambda x: type_counts[x])
        else:
            # Final questions: career goals
            return "career_goals"
    
    def get_unused_resume_elements(self):
        """Get resume elements not yet discussed"""
        all_skills = set(self.resume_data.get('skills', []))
        all_projects = {p.get('name', '') for p in self.resume_data.get('projects', [])}
        
        unused_skills = all_skills - self.skills_discussed
        unused_projects = all_projects - self.projects_discussed
        
        return list(unused_skills), list(unused_projects)
    
    def generate_tts_audio(self, question_text: str) -> Optional[bytes]:
        """Generate TTS audio in background thread"""
        try:
            print(f"🎙️ Calling Gemini TTS API for: {question_text[:50]}...")

            response = self.client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=f"Please read this interview question in a professional, clear interviewer voice: {question_text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Aoede"
                            )
                        )
                    )
                )
            )

            print(f"🔍 TTS Response received, checking candidates...")

            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                print(f"✅ Found candidate, checking content...")

                if candidate.content and candidate.content.parts:
                    print(f"📦 Found {len(candidate.content.parts)} parts, checking for audio...")

                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            audio_data = part.inline_data.data
                            print(f"🎵 Raw audio data found! Size: {len(audio_data)} bytes")

                            # Convert audio to browser-compatible format (MP3)
                            try:
                                converted_audio = self.convert_tts_audio_for_browser(audio_data)
                                if converted_audio:
                                    print(f"✅ Audio converted for browser! Size: {len(converted_audio)} bytes")
                                    return converted_audio
                                else:
                                    print(f"⚠️ Audio conversion failed, returning raw data")
                                    return audio_data
                            except Exception as e:
                                print(f"⚠️ Audio conversion error: {e}, returning raw data")
                                return audio_data

                    print(f"⚠️ No inline_data found in parts")
                else:
                    print(f"⚠️ No content or parts found in candidate")
            else:
                print(f"⚠️ No candidates found in TTS response")

            return None

        except Exception as e:
            print(f"❌ TTS generation error: {e}")
            import traceback
            print(f"🔍 TTS error trace: {traceback.format_exc()}")
            return None

    def convert_tts_audio_for_browser(self, audio_data: bytes) -> Optional[bytes]:
        """Convert Gemini TTS audio to browser-compatible MP3 format"""
        try:
            print(f"🔄 Converting {len(audio_data)} bytes of TTS audio to MP3...")

            # Create temporary files for conversion
            with tempfile.NamedTemporaryFile(delete=False) as raw_file:
                raw_file.write(audio_data)
                raw_path = raw_file.name

            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as mp3_file:
                mp3_path = mp3_file.name

            try:
                # Try converting assuming it's WAV format first
                subprocess.run([
                    'ffmpeg', '-y', '-i', raw_path,
                    '-codec:a', 'mp3',
                    '-b:a', '128k',
                    mp3_path
                ], check=True, capture_output=True)

                # Read the converted MP3 file
                with open(mp3_path, 'rb') as f:
                    mp3_data = f.read()

                print(f"✅ Successfully converted to MP3: {len(mp3_data)} bytes")
                return mp3_data

            except subprocess.CalledProcessError:
                # If WAV conversion fails, try as raw PCM
                print(f"🔄 WAV conversion failed, trying as raw PCM...")
                subprocess.run([
                    'ffmpeg', '-y', '-f', 's16le', '-ar', '16000', '-ac', '1', '-i', raw_path,
                    '-codec:a', 'mp3',
                    '-b:a', '128k',
                    mp3_path
                ], check=True, capture_output=True)

                with open(mp3_path, 'rb') as f:
                    mp3_data = f.read()

                print(f"✅ Successfully converted PCM to MP3: {len(mp3_data)} bytes")
                return mp3_data

            finally:
                # Clean up temporary files
                try:
                    os.unlink(raw_path)
                    os.unlink(mp3_path)
                except:
                    pass

        except Exception as e:
            print(f"❌ Audio conversion failed: {e}")
            return None

    def preload_fixed_starter_questions(self):
        """Preload the fixed first 3 questions IMMEDIATELY for zero lag"""
        print(f"🎵 Starting preload of {len(self.fixed_starter_questions)} fixed starter questions...")

        def load_fixed_question(question_data):
            question_text = question_data["text"]
            question_type = question_data["type"]
            order = question_data["order"]

            print(f"🎤 Generating TTS for question #{order}: {question_text[:30]}...")

            try:
                audio_data = self.generate_tts_audio(question_text)

                if audio_data:
                    print(f"✅ TTS generated successfully for question #{order}")
                    self.audio_queue.put({
                        "question": question_text,
                        "audio": audio_data,
                        "type": question_type,
                        "source": "fixed_starter",
                        "order": order
                    })
                else:
                    print(f"⚠️ TTS failed for question #{order}, adding without audio")
                    self.audio_queue.put({
                        "question": question_text,
                        "audio": None,
                        "type": question_type,
                        "source": "fixed_starter",
                        "order": order
                    })
            except Exception as e:
                print(f"❌ Error generating TTS for question #{order}: {e}")
                self.audio_queue.put({
                    "question": question_text,
                    "audio": None,
                    "type": question_type,
                    "source": "fixed_starter",
                    "order": order
                })

        # Generate all 3 starter questions immediately with better logging
        for question_data in self.fixed_starter_questions:
            print(f"📋 Submitting TTS task for: {question_data['text'][:30]}...")
            self.tts_executor.submit(load_fixed_question, question_data)

        print(f"🚀 All {len(self.fixed_starter_questions)} TTS tasks submitted to executor")
    
    def generate_next_question_async(self):
        """Generate dynamic questions 4-15 with enhanced diversity"""
        def generate_and_convert():
            if self.questions_asked >= self.max_questions:
                return
            
            # Skip if we're still in the first 3 questions (they're fixed)
            if self.questions_asked < 3:
                return
            
            # Determine what type of question to ask (for questions 4-15)
            question_type = self.determine_next_question_type()
            unused_skills, unused_projects = self.get_unused_resume_elements()
            
            # Build comprehensive context for dynamic questions
            prompt = f"""
            Generate interview question #{self.questions_asked + 1} of 15 for a voice interview.
            
            CANDIDATE RESUME:
            {json.dumps(self.resume_data, indent=2)}
            
            JOB REQUIREMENTS:
            {json.dumps(self.job_data, indent=2)}
            
            ALL PREVIOUS QUESTIONS AND ANSWERS:
            {json.dumps(self.qa_history, indent=2)}
            
            QUESTION TYPE TO FOCUS ON: {question_type}
            
            TOPICS ALREADY COVERED: {list(self.covered_topics)}
            SKILLS ALREADY DISCUSSED: {list(self.skills_discussed)}
            PROJECTS ALREADY DISCUSSED: {list(self.projects_discussed)}
            
            UNUSED SKILLS TO EXPLORE: {unused_skills[:3]}
            UNUSED PROJECTS TO EXPLORE: {unused_projects[:2]}
            
            QUESTION TYPES USED SO FAR: {json.dumps(self.question_types_used, indent=2)}
            
            IMPORTANT CONTEXT:
            - Questions 1-3 were: "Introduce yourself", "Why interested in role", "Biggest weakness"
            - This is question #{self.questions_asked + 1}, so make it DIFFERENT from the first 3
            - Focus on technical depth, specific projects, or situational scenarios
            
            STRICT REQUIREMENTS:
            1. Do NOT repeat any topics, skills, or projects already covered
            2. Focus specifically on the question type: {question_type}
            3. Reference UNUSED elements from their resume
            4. Make it conversational and professional for voice delivery
            5. Be specific and detailed, not generic
            6. Ensure the question explores NEW territory not covered in first 3 questions
            
            QUESTION TYPE GUIDELINES:
            - technical_skills: Deep dive into specific unused technologies/skills
            - projects_deep_dive: Detailed exploration of unused projects and challenges
            - certifications: Application of certification knowledge in real scenarios
            - situational: Hypothetical job-relevant scenarios and problem-solving
            - leadership: Leadership experiences, mentoring, team management
            - problem_solving: Approach to technical challenges and debugging
            - communication: Explaining complex concepts, documentation
            - career_goals: Future aspirations, learning goals, career direction
            
            Generate ONE specific, unique, technical interview question.
            """
            
            try:
                response = self.text_model.generate_content(prompt)
                question_text = response.text.strip()
                
                # Generate audio for this question
                audio_data = self.generate_tts_audio(question_text)
                
                # Track this question type
                self.question_types_used[question_type].append(self.questions_asked + 1)
                
                # Add to queue
                self.audio_queue.put({
                    "question": question_text,
                    "audio": audio_data,
                    "type": question_type,
                    "source": "generated",
                    "question_number": self.questions_asked + 1
                })
                
            except Exception as e:
                pass
        
        # Submit to executor
        self.tts_executor.submit(generate_and_convert)
    
    def update_covered_topics(self, question: str, answer: str):
        """Update tracking of covered topics, skills, and projects"""
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # Track skills mentioned
        for skill in self.resume_data.get('skills', []):
            if skill.lower() in question_lower or skill.lower() in answer_lower:
                self.skills_discussed.add(skill)
        
        # Track projects mentioned  
        for project in self.resume_data.get('projects', []):
            project_name = project.get('name', '').lower()
            if project_name and (project_name in question_lower or project_name in answer_lower):
                self.projects_discussed.add(project.get('name', ''))
        
        # Track general topics
        topic_keywords = {
            'leadership': ['lead', 'manage', 'team', 'mentor'],
            'challenges': ['challenge', 'problem', 'difficult', 'issue'],
            'learning': ['learn', 'new', 'study', 'research'],
            'teamwork': ['team', 'collaborate', 'work together'],
            'communication': ['explain', 'present', 'communicate', 'document']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in question_lower or keyword in answer_lower for keyword in keywords):
                self.covered_topics.add(topic)
    
    def play_audio(self, audio_data):
        """Play AI audio response"""
        if not audio_data:
            return
            
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
                with wave.open(temp_path, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(24000)
                    wav_file.writeframes(audio_data)
            
            subprocess.run(['afplay', temp_path], check=True, capture_output=True)
            os.unlink(temp_path)
            
        except Exception as e:
            pass
    
    def record_with_spacebar(self):
        """Record with spacebar start/stop control"""
        
        # Wait for first spacebar
        keyboard.wait('space')
        time.sleep(0.2)  # Debounce
        
        # Start recording
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        frames = []
        self.is_recording = True
        
        def stop_on_spacebar():
            keyboard.wait('space')
            time.sleep(0.2)  # Debounce
            self.is_recording = False
        
        # Start spacebar listener in background
        spacebar_thread = threading.Thread(target=stop_on_spacebar)
        spacebar_thread.daemon = True
        spacebar_thread.start()
        
        # Record until spacebar pressed
        while self.is_recording:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        return b''.join(frames)
    
    def transcribe_in_background(self, audio_data: bytes, question_number: int, question_text: str, mime_type: str = 'audio/wav'):
        """Submit transcription to background thread with WebM to WAV conversion support"""
        def transcribe_worker():
            try:
                print(f"🎵 Starting transcription for question {question_number}")
                print(f"🎧 Audio data size: {len(audio_data)} bytes")
                print(f"📝 MIME type: {mime_type}")

                # Create temporary file for audio processing
                with tempfile.NamedTemporaryFile(delete=False) as temp_input_file:
                    temp_input_path = temp_input_file.name
                    temp_input_file.write(audio_data)

                # Create final WAV file for Gemini
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav_file:
                    temp_wav_path = temp_wav_file.name

                # Convert WebM/other formats to WAV using ffmpeg if needed
                if mime_type in ['audio/webm', 'audio/mp4', 'audio/ogg']:
                    print(f"🔄 Converting {mime_type} to WAV using ffmpeg...")
                    try:
                        # Use ffmpeg to convert to WAV with specific format for Gemini
                        subprocess.run([
                            'ffmpeg', '-y', '-i', temp_input_path,
                            '-ar', '16000',  # 16kHz sample rate
                            '-ac', '1',      # Mono
                            '-c:a', 'pcm_s16le',  # 16-bit PCM
                            temp_wav_path
                        ], check=True, capture_output=True)
                        print(f"✅ Successfully converted to WAV")
                    except subprocess.CalledProcessError as e:
                        print(f"❌ ffmpeg conversion failed: {e}")
                        raise Exception(f"Audio conversion failed: {e}")
                    except FileNotFoundError:
                        print(f"❌ ffmpeg not found, trying direct processing...")
                        # Fallback: try to use the raw data as WAV (may not work)
                        with wave.open(temp_wav_path, 'wb') as wav_file:
                            wav_file.setnchannels(1)
                            wav_file.setsampwidth(2)
                            wav_file.setframerate(16000)
                            wav_file.writeframes(audio_data)
                else:
                    print(f"🎵 Processing as WAV directly...")
                    # Assume it's already WAV or compatible
                    with wave.open(temp_wav_path, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)
                        wav_file.setframerate(RATE)
                        wav_file.writeframes(audio_data)

                print(f"📤 Uploading audio file to Gemini...")
                # Upload and transcribe using Gemini (original CLI approach)
                uploaded_file = text_genai.upload_file(temp_wav_path)
                print(f"✅ File uploaded successfully")

                print(f"🤖 Requesting transcription from Gemini...")
                response = self.text_model.generate_content([
                    uploaded_file,
                    "Please transcribe the audio exactly as spoken. Only provide the transcription text, nothing else."
                ])

                transcription = response.text.strip()
                print(f"✅ Transcription received: {transcription[:50]}...")

                # Update covered topics tracking
                self.update_covered_topics(question_text, transcription)

                # Add to transcription queue
                self.transcription_queue.put({
                    "question_number": question_number,
                    "question": question_text,
                    "answer": transcription,
                    "timestamp": datetime.now().isoformat()
                })

                print(f"✅ Transcription completed for question {question_number}")

                # Clean up temporary files
                os.unlink(temp_input_path)
                os.unlink(temp_wav_path)

            except Exception as e:
                print(f"❌ Transcription error for question {question_number}: {e}")
                import traceback
                print(f"🔍 Full error trace: {traceback.format_exc()}")

                self.transcription_queue.put({
                    "question_number": question_number,
                    "question": question_text,
                    "answer": f"[Transcription failed: {e}]",
                    "timestamp": datetime.now().isoformat()
                })

                # Clean up on error
                try:
                    if 'temp_input_path' in locals():
                        os.unlink(temp_input_path)
                    if 'temp_wav_path' in locals():
                        os.unlink(temp_wav_path)
                except:
                    pass

        # Submit to transcription executor
        self.transcribe_executor.submit(transcribe_worker)
    
    def save_interview_to_file(self):
        """Save all Q&A to text file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_session_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write("=" * 80 + "\n")
                f.write("AI VOICE INTERVIEW SESSION - OPTIMIZED VERSION\n")
                f.write("=" * 80 + "\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Candidate: {self.resume_data.get('name', 'Unknown')}\n")
                f.write(f"Total Questions: {len(self.qa_history)}\n")
                f.write(f"Skills Discussed: {', '.join(self.skills_discussed)}\n")
                f.write(f"Projects Discussed: {', '.join(self.projects_discussed)}\n")
                f.write(f"Topics Covered: {', '.join(self.covered_topics)}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("QUESTION STRUCTURE:\n")
                f.write("Questions 1-3: Fixed starter questions for zero lag\n")
                f.write("Questions 4-15: Dynamic personalized questions\n\n")
                
                # Question type summary
                f.write("QUESTION TYPES BREAKDOWN:\n")
                f.write("-" * 30 + "\n")
                for q_type, questions in self.question_types_used.items():
                    if questions:
                        f.write(f"{q_type.replace('_', ' ').title()}: Questions {', '.join(map(str, questions))}\n")
                f.write("\n")
                
                # Full Q&A
                for qa in self.qa_history:
                    f.write(f"QUESTION {qa['question_number']}:\n")
                    f.write(f"{qa['question']}\n\n")
                    f.write(f"ANSWER:\n{qa['answer']}\n")
                    f.write("-" * 60 + "\n\n")
                
                f.write("=" * 80 + "\n")
                f.write("END OF OPTIMIZED INTERVIEW SESSION\n")
                f.write("=" * 80 + "\n")
            
            return filename
            
        except Exception as e:
            return None
    
    async def run_optimized_interview(self):
        """Run the optimized interview with fixed starters + dynamic questions"""
        
        # Step 1: IMMEDIATELY start preloading fixed questions
        self.preload_fixed_starter_questions()
        
        pdf_path = "resume.pdf"
        
        resume_text = self.extract_pdf_text(pdf_path)
        if not resume_text:
            return {"error": "Could not read resume PDF"}
        
        # Step 2: Parse resume (while starter audio generates)
        self.resume_data = self.parse_resume(resume_text)
        
        # Step 3: Get job description (starter audio should be ready soon)
        job_description = input("Please paste the job description:\n")
        
        # Step 4: Analyze job 
        self.job_data = self.analyze_job_description(job_description)
        
        # Step 5: Generate questions 4-15 in background
        for i in range(7):  # Generate several dynamic questions
            self.generate_next_question_async()
        
        # Step 6: Wait for starter questions to be ready
        time.sleep(2)  # Give TTS a moment to finish
        
        # Step 7: Start interview
        input("Press ENTER when ready for instant interview start...")
        
        # Step 8: Interview loop
        for i in range(15):
            
            # Get next question from queue
            question_data = None
            try:
                question_data = self.audio_queue.get_nowait()
            except queue.Empty:
                # Fallback for questions 4-15
                if i >= 3:
                    unused_skills, unused_projects = self.get_unused_resume_elements()
                    if unused_skills:
                        question_text = f"Tell me about your experience with {unused_skills[0]} and how you've applied it in your projects."
                    else:
                        question_text = "Describe your approach to learning new technologies and staying updated in your field."
                else:
                    # Fallback for first 3 (should never happen)
                    question_text = self.fixed_starter_questions[i]["text"]
                
                question_data = {
                    "question": question_text,
                    "audio": None,
                    "type": "fallback"
                }
            
            current_question = question_data["question"]
            current_audio = question_data.get("audio")
            question_type = question_data.get("type", "unknown")
            question_source = question_data.get("source", "unknown")
            
            # Play audio instantly (should be ready for first 3)
            if current_audio:
                self.play_audio(current_audio)
            
            # Record answer
            audio_answer = self.record_with_spacebar()
            
            # Submit transcription to background
            self.questions_asked += 1
            self.transcribe_in_background(audio_answer, self.questions_asked, current_question)
            
            # Generate next question in background (for questions 4-15)
            if self.questions_asked < 15 and self.questions_asked >= 3:
                self.generate_next_question_async()
        
        # Step 9: Wait for transcriptions
        collected_transcriptions = {}
        timeout_count = 0
        
        while len(collected_transcriptions) < 15 and timeout_count < 30:
            try:
                transcription = self.transcription_queue.get(timeout=2)
                collected_transcriptions[transcription["question_number"]] = transcription
            except queue.Empty:
                timeout_count += 1
        
        # Build final Q&A history
        for i in range(1, 16):
            if i in collected_transcriptions:
                self.qa_history.append(collected_transcriptions[i])
        
        # Step 10: Save interview
        saved_file = self.save_interview_to_file()
        
        # Step 11: Generate final evaluation report
        final_report = self.generate_final_report()
        
        return {
            "report": final_report,
            "saved_file": saved_file,
            "qa_history": self.qa_history,
            "resume_data": self.resume_data,
            "job_data": self.job_data
        }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Generate evaluation report by ANALYZING ALL USER RESPONSES"""
        prompt = f"""
        You are an expert interviewer evaluating a candidate's interview performance. 
        Analyze the complete interview conversation and provide a comprehensive assessment.
        
        COMPLETE INTERVIEW TRANSCRIPT:
        {json.dumps(self.qa_history, indent=2)}
        
        CANDIDATE PROFILE:
        {json.dumps(self.resume_data, indent=2)}
        
        JOB REQUIREMENTS:
        {json.dumps(self.job_data, indent=2)}
        
        INTERVIEW ANALYTICS:
        - Skills Discussed: {list(self.skills_discussed)}
        - Projects Covered: {list(self.projects_discussed)}
        - Topics Explored: {list(self.covered_topics)}
        
        EVALUATION INSTRUCTIONS:
        Analyze EACH answer the candidate gave. Look for:
        1. Technical accuracy and depth of knowledge
        2. Communication clarity and professionalism
        3. Problem-solving approach and critical thinking
        4. Relevant experience and examples provided
        5. Cultural fit and soft skills demonstrated
        6. Honesty and self-awareness (especially in weakness question)
        7. Enthusiasm and genuine interest in the role
        
        Base your evaluation ENTIRELY on what the candidate actually said in their responses.
        Do NOT make assumptions - only evaluate based on the transcribed answers.
        
        Return ONLY JSON:
        {{
            "overall_score": <integer 1-10>,
            "selected": <boolean true/false>,
            "selection_reason": "detailed justification based on specific answers given",
            "strengths": ["specific strength based on their responses"],
            "improvement_areas": ["specific areas where answers were weak"],
            "recommendations": ["actionable advice based on interview performance"],
            "technical_competency": "poor/fair/good/excellent",
            "communication_skills": "poor/fair/good/excellent", 
            "problem_solving": "poor/fair/good/excellent",
            "cultural_fit": "poor/fair/good/excellent",
            "answer_quality": "assessment of how well they answered questions",
            "summary": "4-5 sentence summary of their actual interview performance"
        }}
        """
        
        try:
            response = self.text_model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"overall_score": 5, "selected": False, "summary": response.text}
        except Exception as e:
            return {"overall_score": 5, "selected": False, "summary": f"Report error: {e}"}
    
    def display_results(self, report: Dict[str, Any], saved_file: Optional[str]):
        """Display results"""
        print("\n" + "⚡" * 30)
        print("🏆 VOICE INTERVIEW EVALUATION RESULTS")
        print("⚡" * 30)
        
        if saved_file:
            print(f"📁 Interview saved to: {saved_file}")
        
        # Selection Decision
        selected = report.get('selected', False)
        selection_emoji = "✅ SELECTED FOR NEXT ROUND" if selected else "❌ NOT SELECTED"
        print(f"\n{selection_emoji}")
        print(f"📋 {report.get('selection_reason', 'No reason provided')}")
        
        score = report.get('overall_score', 'N/A')
        print(f"\n🏆 **OVERALL SCORE: {score}/10**")
        
        # Competency breakdown
        print(f"\n📊 **COMPETENCY ASSESSMENT:**")
        print(f"   • Technical Skills: {report.get('technical_competency', 'N/A').title()}")
        print(f"   • Communication: {report.get('communication_skills', 'N/A').title()}")
        print(f"   • Problem Solving: {report.get('problem_solving', 'N/A').title()}")
        print(f"   • Cultural Fit: {report.get('cultural_fit', 'N/A').title()}")
        print(f"   • Answer Quality: {report.get('answer_quality', 'N/A').title()}")
        
        print(f"\n✅ **DEMONSTRATED STRENGTHS:**")
        for strength in report.get('strengths', []):
            print(f"   • {strength}")
        
        print(f"\n🔧 **AREAS FOR IMPROVEMENT:**")
        for area in report.get('improvement_areas', []):
            print(f"   • {area}")
        
        print(f"\n💡 **DEVELOPMENT RECOMMENDATIONS:**")
        for rec in report.get('recommendations', []):
            print(f"   • {rec}")
        
        print(f"\n📈 **INTERVIEW COVERAGE:**")
        print(f"   • Skills Explored: {len(self.skills_discussed)} skills")
        print(f"   • Projects Discussed: {len(self.projects_discussed)} projects")
        print(f"   • Question Types: {len([t for t, qs in self.question_types_used.items() if qs])} different types")
        
        print(f"\n📋 **PERFORMANCE SUMMARY:**")
        print(f"   {report.get('summary', 'Summary not available')}")
        
        print("\n" + "⚡" * 30)
        print("🚀 ZERO-LAG INTERVIEW COMPLETED!")
        print("⚡" * 30)
    
    def __del__(self):
        """Cleanup executors"""
        try:
            self.tts_executor.shutdown(wait=False)
            self.transcribe_executor.shutdown(wait=False)
        except:
            pass

async def main():
    """Main function"""
    if not os.getenv('GOOGLE_API_KEY'):
        return {"error": "Please set GOOGLE_API_KEY in your .env file"}
    
    interviewer = OptimizedVoiceInterview()
    result = await interviewer.run_optimized_interview()
    return result

if __name__ == "__main__":
    asyncio.run(main())
