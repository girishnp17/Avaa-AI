# AI Voice Interview System

A high-performance voice interview system with zero-lag delivery and real-time transcription.

## Features

- **Zero-lag delivery**: First 3 questions are pre-loaded for instant playback
- **Dynamic questioning**: Questions 4-15 are personalized based on resume and job description
- **Voice interaction**: Spacebar-controlled recording with AI voice responses
- **Real-time transcription**: Background processing using Google's Gemini API
- **Comprehensive evaluation**: Detailed analysis and scoring of interview performance

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your Google API key:
```
GOOGLE_API_KEY=your_api_key_here
```

3. Place your resume as `resume.pdf` in the same directory

## Usage

Run the interview system:
```bash
sudo python3 voice_final.py
```

**Controls:**
- Press **SPACEBAR** to start recording your answer
- Press **SPACEBAR** again to stop recording
- Follow the on-screen prompts

## Requirements

- Python 3.7+
- Google API key with Gemini access
- Resume in PDF format
- Microphone and speakers
- macOS (for audio playback)

## Output

- Real-time interview session
- Saved transcript with timestamp
- Comprehensive evaluation report
- Performance scoring and recommendations

## Frontend/Backend Integration

This system is designed to be easily integrated with web frontends and backend APIs. Here are the key integration points:

### Main Class: `OptimizedVoiceInterview`

#### Core Methods for Integration:

**1. Initialization & Setup**
```python
interviewer = OptimizedVoiceInterview()
```

**2. Resume Processing**
```python
# Extract text from PDF
resume_text = interviewer.extract_pdf_text(pdf_path)

# Parse resume into structured data
resume_data = interviewer.parse_resume(resume_text)
# Returns: {"name", "skills", "certifications", "projects", "experience", "education", "soft_skills"}
```

**3. Job Analysis**
```python
# Analyze job description
job_data = interviewer.analyze_job_description(job_description_text)
# Returns: {"job_title", "required_skills", "preferred_skills", "experience_level", "key_responsibilities"}
```

**4. Audio Generation**
```python
# Generate TTS audio for questions
audio_bytes = interviewer.generate_tts_audio(question_text)
# Returns: Audio bytes or None
```

**5. Audio Recording (for voice interfaces)**
```python
# Record audio from microphone
audio_data = interviewer.record_with_spacebar()
# Returns: Raw audio bytes
```

**6. Audio Transcription**
```python
# Transcribe audio to text (background processing)
interviewer.transcribe_in_background(audio_data, question_number, question_text)
# Adds result to transcription_queue
```

**7. Main Interview Flow**
```python
# Run complete interview
result = await interviewer.run_optimized_interview()
# Returns: {
#   "report": evaluation_report,
#   "saved_file": filename,
#   "qa_history": questions_and_answers,
#   "resume_data": parsed_resume,
#   "job_data": parsed_job
# }
```

**8. Evaluation & Reporting**
```python
# Generate final evaluation report
report = interviewer.generate_final_report()
# Returns: {
#   "overall_score": 1-10,
#   "selected": true/false,
#   "selection_reason": "text",
#   "strengths": ["list"],
#   "improvement_areas": ["list"],
#   "recommendations": ["list"],
#   "technical_competency": "poor/fair/good/excellent",
#   "communication_skills": "poor/fair/good/excellent",
#   "problem_solving": "poor/fair/good/excellent",
#   "cultural_fit": "poor/fair/good/excellent",
#   "summary": "text"
# }
```

### Integration Patterns:

**For Web APIs:**
- Use `extract_pdf_text()` and `parse_resume()` for resume upload endpoints
- Use `analyze_job_description()` for job posting analysis
- Use `generate_final_report()` for evaluation endpoints
- Store `qa_history` in database for interview records

**For Real-time Applications:**
- Use the queue system (`audio_queue`, `transcription_queue`) for async processing
- Implement WebSocket connections for real-time question delivery
- Use `generate_tts_audio()` for dynamic audio generation

**For Mobile/Desktop Apps:**
- Replace `record_with_spacebar()` with platform-specific audio recording
- Use `play_audio()` method as reference for audio playback implementation
- Adapt file I/O methods for app-specific storage

### Key Data Structures:

**Question Object:**
```python
{
    "question": "Question text",
    "audio": audio_bytes,
    "type": "question_type",
    "source": "fixed_starter|generated",
    "order": 1
}
```

**Transcription Object:**
```python
{
    "question_number": 1,
    "question": "Question text",
    "answer": "Transcribed answer",
    "timestamp": "ISO timestamp"
}
```

**Interview State:**
- `resume_data`: Parsed resume information
- `job_data`: Analyzed job requirements  
- `qa_history`: Complete question-answer pairs
- `questions_asked`: Current progress counter
- `covered_topics`: Set of discussed topics