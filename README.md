# 🤖 Unified AI Tools Suite - AI Core Only

A comprehensive collection of AI-powered career and job tools with **pure AI functionality** - all UI components removed for clean integration.

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   cd unified-ai-tools
   pip install -r requirements.txt
   ```

2. **Run the AI Core**:
   ```bash
   python main_launcher.py
   ```

## 🛠️ Available AI Modules

### 1. 🔍 AI Job Scraper
- Multi-source job search with AI analysis
- CrewAI-powered job relevance scoring
- **File**: `job-scraper/ai_job_scraper.py`

### 2. 🎓 AI Course Recommender  
- AI-powered course suggestions
- Personalized learning recommendations
- **File**: `course-recommender/ai_course_core.py`

### 3. 💼 AI Career Guidance
- Resume analysis and career advice
- Job market intelligence
- **File**: `career-guidance/ai_career_guidance.py`

### 4. 📄 AI Resume Generator
- AI-powered resume builder
- ATS optimization
- **File**: `resume-generator/ai_resume_core.py`

### 5. 🗺️ AI Learning Roadmap
- 8-step progression roadmaps
- Career outcome predictions
- **File**: `learning-roadmap/ai_roadmap_core.py`

### 6. 🔧 Unified AI Interface
- Single interface for all AI tools
- **File**: `ai_core.py`

## 📋 Setup Requirements

- Python 3.8+
- Google Gemini API key
- SerpAPI key (for career guidance)

## 🔧 Usage Examples

```python
from ai_core import UnifiedAITools

# Initialize AI tools
ai_tools = UnifiedAITools()

# Course recommendations
courses = ai_tools.recommend_courses(
    interests="Machine Learning",
    skills="Python, Statistics", 
    goals="Data Scientist"
)

# Learning roadmap
roadmap = ai_tools.create_learning_roadmap(
    subject="Web Development",
    current_skills="HTML, CSS",
    goals="Full Stack Developer"
)

# Career analysis
analysis = ai_tools.analyze_career(
    domain_interest="AI/ML",
    experience_years=3,
    current_skills=["Python", "TensorFlow"],
    location="San Francisco"
)

# Resume generation
resume_data = {
    "full_name": "John Doe",
    "email": "john@example.com",
    "skills": "Python, AI, Machine Learning"
}
resume = ai_tools.generate_resume(resume_data)

# Job search
jobs = ai_tools.search_jobs(
    query="Python Developer",
    location="Remote",
    user_skills=["Python", "Django"]
)
```

## 🌟 Features

- **Pure AI Functionality**: No UI components, clean integration
- **AI-Powered**: Uses Google Gemini AI for intelligent recommendations
- **Professional Output**: High-quality results for career development
- **Easy Integration**: Simple Python API for all tools
- **Modular Design**: Each AI module works independently

## 📁 Project Structure

```
unified-ai-tools/
├── main_launcher.py          # Main AI core launcher
├── ai_core.py               # Unified AI interface
├── requirements.txt          # All dependencies
├── README.md                # This file
├── job-scraper/
│   └── ai_job_scraper.py    # AI job scraping core
├── course-recommender/
│   └── ai_course_core.py    # AI course recommendation core
├── career-guidance/
│   ├── ai_career_guidance.py # AI career guidance core
│   └── utils/               # Utility modules
├── resume-generator/
│   ├── ai_resume_core.py    # AI resume generation core
│   └── src/                 # Source modules
└── learning-roadmap/
    └── ai_roadmap_core.py   # AI roadmap generation core
```

## 🔑 API Keys Setup

Create `.env` files in respective directories:

```bash
# For course recommender and learning roadmap
GEMINI_API_KEY_1=your_gemini_key_here
GEMINI_API_KEY_2=your_second_key_here

# For resume generator
GEMINI_API_KEY=your_gemini_key_here

# For career guidance
SERP_API_KEY=your_serp_api_key_here
```

---

**Built with ❤️ using AI for career development - Pure AI Core Version**