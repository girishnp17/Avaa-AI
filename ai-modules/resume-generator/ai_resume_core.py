#!/usr/bin/env python3
"""
AI Resume Generator - Core AI functionality only
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from ai.resume_generator import AIResumeGenerator

class AIResumeCore:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key required")
    
    def generate_resume(self, user_data, job_description="", template_type="tech"):
        """Generate AI-optimized resume"""
        try:
            generator = AIResumeGenerator(api_key=self.api_key, template_type=template_type)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = generator.generate_resume(user_data, job_description, f"resume_{timestamp}")
            
            if pdf_path and os.path.exists(pdf_path):
                return {
                    'success': True,
                    'pdf_path': pdf_path,
                    'message': 'Resume generated successfully'
                }
            else:
                return {
                    'success': False,
                    'pdf_path': None,
                    'message': 'Resume generation failed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'pdf_path': None,
                'message': f'Error: {str(e)}'
            }
    
    def optimize_for_job(self, user_data, job_description):
        """Optimize resume content for specific job"""
        generator = AIResumeGenerator(api_key=self.api_key)
        return generator.optimize_content(user_data, job_description)
    
    def analyze_resume_strength(self, user_data):
        """Analyze resume strength and provide suggestions"""
        generator = AIResumeGenerator(api_key=self.api_key)
        return generator.analyze_resume(user_data)

if __name__ == "__main__":
    # Example usage
    resume_core = AIResumeCore()
    
    sample_data = {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "+1-555-0123",
        "location": "San Francisco, CA",
        "summary": "Experienced software engineer with 5+ years in full-stack development",
        "experience": "Senior Developer at TechCorp\n2020-Present\nBuilt scalable web applications",
        "education": "BS Computer Science\nStanford University\n2018",
        "skills": "Python, JavaScript, React, AWS"
    }
    
    result = resume_core.generate_resume(sample_data)
    print(f"Resume generation: {result['message']}")
