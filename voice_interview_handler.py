#!/usr/bin/env python3
"""
WebSocket-based Voice Interview Handler
Integrates the existing voice interview system with real-time WebSocket communication
"""

import os
import sys
import asyncio
import json
import base64
import tempfile
import wave
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add AI module paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_dir, 'ai-modules', 'AVA_voice'))

from voice_final import OptimizedVoiceInterview


class WebSocketVoiceInterviewHandler:
    """
    Handles WebSocket-based voice interviews with real-time audio streaming
    """

    def __init__(self, socketio):
        self.socketio = socketio
        self.sessions = {}  # session_id -> interview_instance
        self.audio_chunks = {}  # session_id -> audio_data_buffer
        self.audio_mime_types = {}  # session_id -> mime_type

    def create_session(self, session_id: str, job_description: str, resume_path: str = "resume.pdf"):
        """Initialize a new interview session"""
        try:
            # Create new interview instance
            interview = OptimizedVoiceInterview()

            # Ensure absolute path for resume
            if not os.path.isabs(resume_path):
                resume_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), resume_path)

            # Extract and parse resume
            resume_text = interview.extract_pdf_text(resume_path)
            if not resume_text:
                return {"success": False, "error": f"Could not read resume PDF at {resume_path}"}

            interview.resume_data = interview.parse_resume(resume_text)
            interview.job_data = interview.analyze_job_description(job_description)

            # Pre-load fixed starter questions
            interview.preload_fixed_starter_questions()

            # Store session
            self.sessions[session_id] = interview
            self.audio_chunks[session_id] = []
            self.audio_mime_types[session_id] = 'audio/webm'  # Default MIME type

            return {
                "success": True,
                "session_id": session_id,
                "resume_data": interview.resume_data,
                "job_data": interview.job_data,
                "total_questions": interview.max_questions,
                "fixed_starter_questions": [q["text"] for q in interview.fixed_starter_questions]
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_next_question(self, session_id: str) -> Dict[str, Any]:
        """Get the next question for the session"""
        print(f"🎯 Getting next question for session: {session_id}")

        if session_id not in self.sessions:
            print(f"❌ Session {session_id} not found")
            return {"success": False, "error": "Session not found"}

        interview = self.sessions[session_id]

        try:
            print(f"📊 Current interview state: questions_asked={interview.questions_asked}, max={interview.max_questions}")

            # Check if we have more questions
            if interview.questions_asked >= interview.max_questions:
                print(f"✅ Interview completed - no more questions")
                return {"success": False, "error": "Interview completed", "completed": True}

            question_data = None

            # For first 3 questions, get from fixed starters
            if interview.questions_asked < 3:
                print(f"📋 Getting fixed question #{interview.questions_asked + 1}")
                try:
                    question_data = interview.audio_queue.get_nowait()
                    print(f"✅ Retrieved question from audio queue")
                except:
                    # Fallback to fixed questions text
                    fixed_q = interview.fixed_starter_questions[interview.questions_asked]
                    question_data = {
                        "question": fixed_q["text"],
                        "audio": None,
                        "type": fixed_q["type"],
                        "source": "fixed_starter",
                        "order": fixed_q["order"]
                    }
                    print(f"⚠️ Audio queue empty, using text fallback: {fixed_q['text'][:50]}...")
            else:
                # For questions 4-15, generate dynamically
                print(f"🔄 Generating dynamic question #{interview.questions_asked + 1}")
                question_data = self._generate_dynamic_question(session_id)

            if question_data:
                question_number = interview.questions_asked + 1

                result = {
                    "success": True,
                    "question_number": question_number,
                    "question_text": question_data["question"],
                    "question_type": question_data.get("type", "unknown"),
                    "has_audio": question_data.get("audio") is not None,
                    "total_questions": interview.max_questions
                }

                # Add audio data if available
                if question_data.get("audio"):
                    result["audio_data"] = base64.b64encode(question_data["audio"]).decode('utf-8')
                    print(f"✅ Question includes audio data")
                else:
                    print(f"ℹ️ Question is text-only")

                print(f"✅ Successfully prepared question {question_number}: {question_data['question'][:50]}...")
                return result
            else:
                print(f"❌ No question data generated")
                return {"success": False, "error": "Could not generate question"}

        except Exception as e:
            print(f"❌ Error in get_next_question: {e}")
            import traceback
            print(f"🔍 Full error trace: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def _generate_dynamic_question(self, session_id: str) -> Dict[str, Any]:
        """Generate a dynamic question for questions 4-15"""
        try:
            print(f"🔄 Starting dynamic question generation for session {session_id}")

            if session_id not in self.sessions:
                raise Exception(f"Session {session_id} not found")

            interview = self.sessions[session_id]

            print(f"📊 Session state: questions_asked={interview.questions_asked}, max_questions={interview.max_questions}")
            print(f"📋 Resume data available: {bool(interview.resume_data)}")
            print(f"🎯 Skills discussed: {len(interview.skills_discussed)}")
            print(f"🗂️ Projects discussed: {len(interview.projects_discussed)}")

            # Get unused resume elements for personalization
            try:
                unused_skills, unused_projects = interview.get_unused_resume_elements()
                print(f"🔍 Found unused skills: {len(unused_skills)}, unused projects: {len(unused_projects)}")
                if unused_skills:
                    print(f"   Skills: {list(unused_skills)[:3]}")  # Show first 3
                if unused_projects:
                    print(f"   Projects: {list(unused_projects)[:3]}")  # Show first 3
            except Exception as e:
                print(f"⚠️ Error getting resume elements: {e}")
                unused_skills, unused_projects = set(), set()

            # Generate question based on current progress
            question_text = None
            question_type = "behavioral"  # default

            if unused_skills and len(unused_skills) > 0:
                skill = list(unused_skills)[0]  # Convert to list to get first item
                question_text = f"Tell me about your experience with {skill} and how you've applied it in your projects."
                interview.skills_discussed.add(skill)
                question_type = "technical_skills"
                print(f"✅ Generated skill-based question about: {skill}")

            elif unused_projects and len(unused_projects) > 0:
                project = list(unused_projects)[0]  # Convert to list to get first item
                question_text = f"Can you walk me through your {project} project and the challenges you faced?"
                interview.projects_discussed.add(project)
                question_type = "projects_deep_dive"
                print(f"✅ Generated project-based question about: {project}")

            else:
                # Behavioral/situational questions as fallback
                behavioral_questions = [
                    "Describe a time when you had to work under pressure. How did you handle it?",
                    "Tell me about a challenging technical problem you solved recently.",
                    "How do you stay updated with new technologies in your field?",
                    "Describe your approach to debugging complex issues.",
                    "Tell me about a time you disagreed with a team member. How did you resolve it?",
                    "What's your process for learning a new technology or framework?",
                    "Describe a project where you had to work with unclear requirements.",
                    "How do you ensure code quality in your projects?",
                    "Tell me about a time you had to explain a technical concept to a non-technical person.",
                    "What motivates you to work in this field?",
                    "How do you approach testing your code?",
                    "Describe a time when you had to optimize performance in an application."
                ]

                question_index = min(interview.questions_asked - 3, len(behavioral_questions) - 1)
                question_text = behavioral_questions[question_index]
                question_type = "behavioral"
                print(f"✅ Generated behavioral question #{question_index + 1}")

            if not question_text:
                raise Exception("Failed to generate question text")

            print(f"📝 Generated question: {question_text[:50]}...")

            # Try to generate TTS audio for the question (optional)
            audio_data = None
            try:
                print(f"🎵 Attempting TTS audio generation...")
                audio_data = interview.generate_tts_audio(question_text)
                if audio_data:
                    print(f"✅ TTS audio generated successfully")
                else:
                    print(f"ℹ️ No TTS audio - question will be text-only")
            except Exception as e:
                print(f"⚠️ TTS generation error (continuing without audio): {e}")
                audio_data = None

            result = {
                "question": question_text,
                "audio": audio_data,
                "type": question_type,
                "source": "generated"
            }

            print(f"✅ Dynamic question generation completed successfully")
            return result

        except Exception as e:
            print(f"❌ Critical error in dynamic question generation: {e}")
            import traceback
            print(f"🔍 Full error trace: {traceback.format_exc()}")

            # Return a safe fallback question to prevent the system from crashing
            fallback_question = f"Tell me about a project you're proud of and what you learned from it."
            print(f"🚨 Using fallback question: {fallback_question}")

            return {
                "question": fallback_question,
                "audio": None,
                "type": "fallback",
                "source": "error_fallback"
            }

    def process_audio_chunk(self, session_id: str, audio_data: bytes, mime_type: str = 'audio/webm'):
        """Process incoming audio chunk from client"""
        if session_id not in self.audio_chunks:
            self.audio_chunks[session_id] = []

        # Store or update MIME type for this session
        self.audio_mime_types[session_id] = mime_type

        self.audio_chunks[session_id].append(audio_data)

    def finish_recording(self, session_id: str) -> Dict[str, Any]:
        """Process complete audio recording and get transcription"""
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}

        if session_id not in self.audio_chunks or not self.audio_chunks[session_id]:
            return {"success": False, "error": "No audio data received"}

        interview = self.sessions[session_id]

        try:
            # Combine all audio chunks
            combined_audio = b''.join(self.audio_chunks[session_id])

            # Clear audio buffer
            self.audio_chunks[session_id] = []

            # Get current question info
            question_number = interview.questions_asked + 1
            current_question = "Current question"  # We'll track this properly

            # Get MIME type for this session
            mime_type = self.audio_mime_types.get(session_id, 'audio/webm')

            # Start transcription in background with MIME type
            interview.transcribe_in_background(combined_audio, question_number, current_question, mime_type)

            # Increment questions asked
            interview.questions_asked += 1

            return {
                "success": True,
                "message": "Audio processed, transcription in progress",
                "question_number": question_number
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_transcription(self, session_id: str) -> Dict[str, Any]:
        """Get the latest transcription if available"""
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}

        interview = self.sessions[session_id]

        try:
            # Check if transcription is ready
            transcription_data = interview.transcription_queue.get_nowait()

            # Add to QA history
            interview.qa_history.append(transcription_data)

            return {
                "success": True,
                "transcription": transcription_data["answer"],
                "question_number": transcription_data["question_number"],
                "timestamp": transcription_data["timestamp"]
            }

        except:
            return {"success": False, "error": "Transcription not ready"}

    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End the interview session and generate final report"""
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}

        interview = self.sessions[session_id]

        try:
            # Generate final evaluation report
            final_report = interview.generate_final_report()

            # Save interview to file
            saved_file = interview.save_interview_to_file()

            # Clean up session
            del self.sessions[session_id]
            if session_id in self.audio_chunks:
                del self.audio_chunks[session_id]
            if session_id in self.audio_mime_types:
                del self.audio_mime_types[session_id]

            return {
                "success": True,
                "final_report": final_report,
                "saved_file": saved_file,
                "qa_history": interview.qa_history,
                "total_questions_asked": len(interview.qa_history)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of the interview session"""
        if session_id not in self.sessions:
            return {"success": False, "error": "Session not found"}

        interview = self.sessions[session_id]

        return {
            "success": True,
            "session_id": session_id,
            "questions_asked": interview.questions_asked,
            "total_questions": interview.max_questions,
            "progress_percent": (interview.questions_asked / interview.max_questions) * 100,
            "skills_discussed": list(interview.skills_discussed),
            "projects_discussed": list(interview.projects_discussed),
            "is_complete": interview.questions_asked >= interview.max_questions
        }