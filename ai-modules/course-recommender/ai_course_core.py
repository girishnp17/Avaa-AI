#!/usr/bin/env python3
"""
AI Course Recommender - Pure AI Generation with Gemini
Generates 8-step learning roadmaps with real course recommendations
"""

import google.generativeai as genai
import json
import time
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CourseRecommender:
    """Pure AI-powered 8-Step Learning Roadmap Generator"""

    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        print("✅ Course Recommender initialized with pure AI generation")

    def _generate_content(self, prompt: str) -> str:
        """Generate content using Gemini with basic error handling"""
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")

    def _extract_json(self, text: str) -> dict:
        """Extract and parse JSON from AI response with improved handling"""
        # Clean markdown formatting
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        # Find JSON boundaries more precisely
        text = text.strip()
        
        # Try to find the start and end of JSON object
        start_idx = text.find('{')
        if start_idx == -1:
            raise Exception("No JSON object found in AI response")
        
        # Find the matching closing brace
        brace_count = 0
        end_idx = -1
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                brace_count += 1
            elif text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        
        if end_idx == -1:
            raise Exception("Could not find complete JSON object in AI response")
        
        json_str = text[start_idx:end_idx + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # If still fails, try a more aggressive approach
            print(f"⚠️ JSON parsing failed, attempting cleanup...")
            # Remove any potential trailing content after the JSON
            lines = json_str.split('\n')
            cleaned_lines = []
            for line in lines:
                # Stop at any line that looks like it's not part of JSON
                if line.strip() and not any(char in line for char in '{}[]":,'):
                    break
                cleaned_lines.append(line)
            
            cleaned_json = '\n'.join(cleaned_lines)
            try:
                return json.loads(cleaned_json)
            except json.JSONDecodeError:
                raise Exception(f"Failed to parse AI response as JSON after cleanup: {str(e)}")

    def _extract_json_list(self, text: str) -> list:
        """Extract and parse JSON array from AI response"""
        # Clean markdown formatting
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        # Find JSON array boundaries
        text = text.strip()
        
        # Try to find the start and end of JSON array
        start_idx = text.find('[')
        if start_idx == -1:
            raise Exception("No JSON array found in AI response")
        
        # Find the matching closing bracket
        bracket_count = 0
        end_idx = -1
        for i in range(start_idx, len(text)):
            if text[i] == '[':
                bracket_count += 1
            elif text[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    end_idx = i
                    break
        
        if end_idx == -1:
            raise Exception("Could not find complete JSON array in AI response")
        
        json_str = text[start_idx:end_idx + 1]
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse AI response as JSON array: {str(e)}")

    def generate_8_step_roadmap(self, subject: str, current_skills: str = "", goals: str = "") -> Dict:
        """Generate 8-step learning roadmap using pure AI"""
        print(f"🤖 Generating 8-step roadmap for: {subject}")
        
        prompt = f"""
        Create a comprehensive 8-step learning roadmap for: {subject}
        Current skills: {current_skills or 'Beginner level'}
        Goals: {goals or 'Master the subject professionally'}

        Generate ONLY a valid JSON object with this exact structure:
        {{
            "roadmap_title": "Complete {subject} Learning Path",
            "subject": "{subject}",
            "steps": [
                {{
                    "step_number": 1,
                    "title": "Foundation & Prerequisites",
                    "description": "Detailed description of what to learn in this step",
                    "duration": "2-3 weeks",
                    "skills_to_learn": ["specific skill 1", "specific skill 2", "specific skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2", "objective 3"],
                    "difficulty_level": "Beginner"
                }},
                {{
                    "step_number": 2,
                    "title": "Core Fundamentals",
                    "description": "Build essential knowledge and understanding",
                    "duration": "3-4 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Beginner"
                }},
                {{
                    "step_number": 3,
                    "title": "Intermediate Concepts",
                    "description": "Advance your understanding with deeper concepts",
                    "duration": "4-5 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Intermediate"
                }},
                {{
                    "step_number": 4,
                    "title": "Practical Applications",
                    "description": "Apply knowledge through hands-on practice and projects",
                    "duration": "5-6 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Intermediate"
                }},
                {{
                    "step_number": 5,
                    "title": "Advanced Techniques",
                    "description": "Master advanced concepts and methodologies",
                    "duration": "6-7 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Advanced"
                }},
                {{
                    "step_number": 6,
                    "title": "Real-World Projects",
                    "description": "Build comprehensive portfolio projects",
                    "duration": "7-8 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Advanced"
                }},
                {{
                    "step_number": 7,
                    "title": "Industry Best Practices",
                    "description": "Learn professional standards and industry practices",
                    "duration": "3-4 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Advanced"
                }},
                {{
                    "step_number": 8,
                    "title": "Career Preparation",
                    "description": "Prepare for professional roles and career advancement",
                    "duration": "4-5 weeks",
                    "skills_to_learn": ["skill 1", "skill 2", "skill 3"],
                    "key_topics": ["topic 1", "topic 2", "topic 3"],
                    "learning_objectives": ["objective 1", "objective 2"],
                    "difficulty_level": "Professional"
                }}
            ],
            "total_duration": "8-12 months",
            "prerequisites": ["prerequisite 1", "prerequisite 2"],
            "career_outcomes": ["outcome 1", "outcome 2", "outcome 3"],
            "salary_range": "$X,000 - $Y,000"
        }}

        Requirements:
        1. Make each step specific to {subject}
        2. Ensure progressive difficulty from Beginner to Professional
        3. Include realistic durations and specific skills
        4. Focus on practical, career-relevant outcomes
        5. Return ONLY the JSON object, no additional text
        """

        response = self._generate_content(prompt)
        return self._extract_json(response)

    def search_courses_for_step(self, step_data: Dict, subject: str) -> List[Dict]:
        """Generate course recommendations for a specific step using AI"""
        step_title = step_data.get('title', '')
        skills = step_data.get('skills_to_learn', [])
        topics = step_data.get('key_topics', [])
        difficulty = step_data.get('difficulty_level', 'Intermediate')

        print(f"🔍 AI searching courses for: {step_title}")

        prompt = f"""
        Find the best online courses for this learning step:

        Subject: {subject}
        Step: {step_title}
        Skills to Learn: {', '.join(skills)}
        Key Topics: {', '.join(topics)}
        Difficulty Level: {difficulty}

        Search for real courses from top educational platforms:
        - Coursera (including free audit options)
        - edX (including free audit options)
        - FreeCodeCamp
        - Khan Academy
        - Codecademy
        - MIT OpenCourseWare
        - YouTube educational channels
        - Udacity
        - DataCamp
        - LinkedIn Learning

        Return ONLY a JSON array of 5 best real courses:
        [
            {{
                "title": "Exact course title from platform",
                "platform": "Platform name",
                "url": "Real course URL",
                "description": "Compelling 2-3 sentence description of what you'll learn",
                "duration": "Realistic duration (e.g., '6 weeks', '40 hours')",
                "price": "Actual price (Free, $49/month, Audit Free, etc.)",
                "instructor": "Real instructor name or institution",
                "rating": "Realistic rating (4.0-5.0)/5",
                "skills_gained": ["specific skill 1", "specific skill 2", "specific skill 3"],
                "level": "{difficulty.lower()}",
                "enrollment_count": "Number of students enrolled"
            }}
        ]

        Requirements:
        1. Find REAL, currently available courses
        2. Prioritize FREE or audit-free options
        3. Ensure courses match the {difficulty} level
        4. Include variety of platforms
        5. Provide accurate course details
        6. Focus on courses relevant to {subject}
        7. Return ONLY the JSON array, no additional text
        """

        response = self._generate_content(prompt)
        courses_data = self._extract_json_list(response)
        
        if not isinstance(courses_data, list):
            raise Exception("AI did not return a list of courses")

        # Enhance course data with metadata
        enhanced_courses = []
        for course in courses_data:
            enhanced_course = {
                **course,
                'source': 'AI Generated',
                'step_number': step_data.get('step_number'),
                'search_date': time.strftime('%Y-%m-%d'),
                'relevance_score': 0.9
            }
            enhanced_courses.append(enhanced_course)

        return enhanced_courses

    def create_complete_learning_plan(self, subject: str, current_skills: str = "", goals: str = "") -> Dict:
        """Generate complete 8-step learning plan with AI-powered course recommendations"""
        print(f"🎯 Creating complete AI-powered learning plan for: {subject}")

        # Step 1: Generate 8-step roadmap
        roadmap = self.generate_8_step_roadmap(subject, current_skills, goals)
        print(f"✅ Generated {len(roadmap.get('steps', []))} learning steps")

        # Step 2: Generate courses for each step
        all_courses = []
        courses_by_step = {}

        for step in roadmap.get('steps', []):
            step_courses = self.search_courses_for_step(step, subject)
            step_number = step.get('step_number')
            courses_by_step[f"step_{step_number}"] = step_courses
            all_courses.extend(step_courses)
            time.sleep(1)  # Rate limiting

        # Step 3: Categorize courses
        free_courses = [c for c in all_courses if 'free' in c.get('price', '').lower()]
        beginner_courses = [c for c in all_courses if c.get('level', '').lower() == 'beginner']
        intermediate_courses = [c for c in all_courses if c.get('level', '').lower() == 'intermediate']
        advanced_courses = [c for c in all_courses if c.get('level', '').lower() == 'advanced']

        # Step 4: Compile final result
        result = {
            'roadmap': roadmap,
            'course_recommendations': all_courses,
            'courses_by_step': courses_by_step,
            'courses': {
                'all': all_courses,
                'beginner': beginner_courses,
                'intermediate': intermediate_courses,
                'advanced': advanced_courses,
                'free': free_courses
            },
            'summary': {
                'subject': subject,
                'total_courses': len(all_courses),
                'total_steps': len(roadmap.get('steps', [])),
                'estimated_duration': roadmap.get('total_duration', '8-12 months'),
                'salary_range': roadmap.get('salary_range', 'Competitive'),
                'method': 'Pure AI Generation',
                'free_courses': len(free_courses),
                'platform_breakdown': self._analyze_platforms(all_courses)
            }
        }

        print(f"✅ Complete AI learning plan created:")
        print(f"   📚 {result['summary']['total_steps']} learning steps")
        print(f"   🎓 {result['summary']['total_courses']} AI-generated courses")
        print(f"   🆓 {result['summary']['free_courses']} free courses")
        print(f"   ⏱️ Duration: {result['summary']['estimated_duration']}")

        return result

    def _analyze_platforms(self, courses: List[Dict]) -> Dict[str, int]:
        """Analyze platform distribution in courses"""
        platform_count = {}
        for course in courses:
            platform = course.get('platform', 'Unknown')
            platform_count[platform] = platform_count.get(platform, 0) + 1
        return platform_count

# Main API function for web compatibility
def get_course_recommendations(interests: str, skills: str = "", goals: str = "") -> Dict:
    """
    Generate 8-step learning plan with pure AI course recommendations
    
    Args:
        interests (str): Subject or career interest
        skills (str): Current skills
        goals (str): Learning goals
        
    Returns:
        Dict: Complete AI-generated learning plan
    """
    try:
        recommender = CourseRecommender()
        result = recommender.create_complete_learning_plan(interests, skills, goals)
        
        return {
            'success': True,
            'data': result,
            'metadata': {
                'interests': interests,
                'skills': skills,
                'goals': goals,
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'method': 'Pure AI Generation'
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': {
                'roadmap': {},
                'course_recommendations': [],
                'courses_by_step': {},
                'courses': {'all': [], 'beginner': [], 'intermediate': [], 'advanced': [], 'free': []},
                'summary': {'total_courses': 0, 'total_steps': 0}
            }
        }

def main():
    """Main function for testing"""
    print("🎓 AI Course Recommender - Pure AI Generation")
    print("=" * 60)
    
    try:
        subject = input("What subject would you like to learn? ").strip()
        if not subject:
            print("❌ Please enter a subject to get recommendations.")
            return
            
        skills = input("What are your current skills? (optional) ").strip()
        goals = input("What are your learning goals? (optional) ").strip()
        
        result = get_course_recommendations(subject, skills, goals)
        
        if result['success']:
            data = result['data']
            roadmap = data['roadmap']
            
            print(f"\n📚 {roadmap.get('roadmap_title', 'Learning Plan')}")
            print(f"⏱️ Duration: {roadmap.get('total_duration', '8-12 months')}")
            print(f"💰 Salary Range: {roadmap.get('salary_range', 'Competitive')}")
            print(f"🎓 Total Courses: {data['summary']['total_courses']}")
            print(f"🆓 Free Courses: {data['summary']['free_courses']}")
            
            print(f"\n📖 Learning Steps:")
            for step in roadmap.get('steps', [])[:3]:  # Show first 3 steps
                print(f"   {step['step_number']}. {step['title']} ({step['duration']})")
                print(f"      Level: {step['difficulty_level']}")
                print(f"      Skills: {', '.join(step['skills_to_learn'][:3])}")
            
            print(f"\n🏆 Sample Courses:")
            for i, course in enumerate(data['course_recommendations'][:5], 1):
                print(f"   {i}. {course['title']}")
                print(f"      Platform: {course['platform']} | Price: {course['price']}")
                print(f"      Rating: {course['rating']} | Level: {course['level']}")
                
        else:
            print(f"❌ Error: {result['error']}")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
