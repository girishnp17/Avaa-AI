import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def parse_resume_with_gemini(resume_text):
    """Parse resume text using Gemini API and return structured data."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Analyze this resume and extract key information in JSON format:
    {resume_text}

    IMPORTANT: Return ONLY a valid JSON object with this exact structure:
    {{
        "technical_skills": ["skill1", "skill2"],
        "experience_years": 5,
        "education_level": "Bachelor's Degree",
        "domain_expertise": ["domain1", "domain2"],
        "current_role": "Software Engineer",
        "certifications": ["cert1", "cert2"]
    }}

    Do not include any text before or after the JSON. Do not wrap in markdown code blocks.
    """

    try:
        response = model.generate_content(prompt)
        
        # Debug: print the raw response
        print(f"Raw response: {response.text[:200]}...")
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse JSON
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(f"Response text: {response_text}")
            # Try to extract JSON from the response if it contains extra text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except:
                    pass
            
            # If all else fails, return default structure
            return {
                "technical_skills": [],
                "experience_years": 0,
                "education_level": "Unknown",
                "domain_expertise": [],
                "current_role": "Unknown",
                "certifications": []
            }
            
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return {
            "technical_skills": [],
            "experience_years": 0,
            "education_level": "Unknown",
            "domain_expertise": [],
            "current_role": "Unknown",
            "certifications": []
        }

def generate_career_recommendations(user_profile, search_results):
    """Generate personalized career recommendations using Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = f"""
    Based on this user profile: {json.dumps(user_profile)}
    And these trending job search results: {json.dumps(search_results)}

    Generate personalized career recommendations in JSON format with this exact structure:
    {{
        "recommendations": [
            {{
                "job_title": "Software Engineer",
                "description": "Detailed job description",
                "required_skills": ["Python", "JavaScript"],
                "market_demand": "High demand in tech industry",
                "salary_range": "$80,000 - $120,000",
                "transition_strategy": "Learn required skills through online courses"
            }}
        ],
        "skills_gap_analysis": "Analysis of skills gap",
        "career_roadmap": "Step-by-step career transition plan"
    }}

    IMPORTANT REQUIREMENTS:
    1. Generate a MINIMUM of 5 and MAXIMUM of 10 role recommendations
    2. Include ALL relevant job positions found in the search results
    3. Each recommendation should be unique and tailored to the user's profile
    4. Return ONLY the JSON object without any explanatory text, markdown formatting, or code blocks
    5. Make sure all job titles are different and cover various seniority levels
    """

    try:
        response = model.generate_content(prompt)
        
        # Debug: print the raw response
        print(f"Raw response: {response.text[:200]}...")
        
        # Clean the response text
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        # Try to parse JSON
        try:
            result = json.loads(response_text)
            
            # Ensure we have at least 5 recommendations
            recommendations = result.get('recommendations', [])
            if len(recommendations) < 5:
                print(f"Warning: Only {len(recommendations)} recommendations generated, expected 5-10")
                
            return result
        except json.JSONDecodeError as json_error:
            print(f"JSON parsing error: {json_error}")
            print(f"Response text: {response_text}")
            # Try to extract JSON from the response if it contains extra text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    return result
                except:
                    pass
            
            # If all else fails, return default structure
            return {
                "recommendations": [],
                "skills_gap_analysis": "Unable to analyze skills gap due to response parsing error",
                "career_roadmap": "Unable to generate roadmap due to response parsing error"
            }
            
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        return {
            "recommendations": [],
            "skills_gap_analysis": "Unable to analyze skills gap",
            "career_roadmap": "Unable to generate roadmap"
        }
