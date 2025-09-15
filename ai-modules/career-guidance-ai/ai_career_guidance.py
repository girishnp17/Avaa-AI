#!/usr/bin/env python3
"""
AI Career Guidance - Core module for integration with main UI
Replaces Streamlit app with API-compatible functions
"""

import os
import sys
import json
from typing import Dict, List, Optional

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from utils.resume_parser import extract_text_from_resume, parse_resume
    from utils.google_search import search_multiple_queries, extract_job_positions, get_job_market_trends
    from utils.gemini_client import generate_career_recommendations
    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Utils import failed: {e}")
    UTILS_AVAILABLE = False

class AICareerGuidance:
    def __init__(self):
        self.user_data = {}
        self.last_analysis = None
        
    def analyze_resume(self, resume_file_path: Optional[str] = None, resume_text: Optional[str] = None) -> Dict:
        """Extract and parse resume data from file or text"""
        try:
            if resume_text:
                resume_content = resume_text
            elif resume_file_path:
                if UTILS_AVAILABLE:
                    resume_content = extract_text_from_resume(resume_file_path)
                else:
                    return self._get_fallback_resume_data()
            else:
                return self._get_fallback_resume_data()

            if UTILS_AVAILABLE and resume_content.strip():
                parsed_data = parse_resume(resume_content)
                print(f"✅ Resume parsed successfully: {len(parsed_data.get('technical_skills', []))} skills found")
                return parsed_data
            else:
                return self._get_fallback_resume_data()
                
        except Exception as e:
            print(f"❌ Resume analysis failed: {e}")
            return self._get_fallback_resume_data()
    
    def _get_fallback_resume_data(self) -> Dict:
        """Fallback resume data when parsing fails"""
        return {
            "technical_skills": [],
            "experience_years": 0,
            "education_level": "Unknown",
            "domain_expertise": [],
            "current_role": "Unknown",
            "certifications": []
        }
    
    def get_job_market_data(self, domain: str, location: str = "United States") -> Dict:
        """Get current job market trends and data"""
        try:
            if UTILS_AVAILABLE:
                print(f"🔍 Fetching job market data for {domain} in {location}...")
                
                # Enhanced search queries for better market analysis
                search_queries = [
                    f"{domain} jobs 2025 trends",
                    f"{domain} engineer salary 2025",
                    f"{domain} developer remote positions",
                    f"best {domain} careers 2025",
                    f"{domain} job market demand",
                    f"hiring {domain} professionals {location}"
                ]
                
                search_results = search_multiple_queries(search_queries, num_results_per_query=10, location=location)
                job_positions = extract_job_positions(search_results)
                market_trends = get_job_market_trends(domain, location)
                
                print(f"✅ Found {len(search_results)} search results, {len(job_positions)} job positions")
                
                return {
                    "search_results": search_results,
                    "job_positions": job_positions,
                    "market_trends": market_trends,
                    "domain": domain,
                    "location": location
                }
            else:
                return self._get_fallback_market_data(domain, location)
                
        except Exception as e:
            print(f"❌ Job market data retrieval failed: {e}")
            return self._get_fallback_market_data(domain, location)
    
    def _get_fallback_market_data(self, domain: str, location: str) -> Dict:
        """Fallback market data when search fails"""
        return {
            "search_results": [],
            "job_positions": [f"{domain} Engineer", f"Senior {domain} Developer", f"{domain} Specialist"],
            "market_trends": {
                "domain": domain,
                "location": location,
                "market_analysis": {"market_demand": "High", "trend_score": 5},
                "trending_skills": ["Python", "JavaScript", "Cloud Computing"],
                "salary_insights": {"sample_ranges": ["$70,000 - $120,000"]},
                "remote_opportunities": {"remote_percentage": 60}
            },
            "domain": domain,
            "location": location
        }
    
    def generate_recommendations(self, user_profile: Dict, job_market_data: Dict) -> Dict:
        """Generate AI-powered career recommendations"""
        try:
            if UTILS_AVAILABLE:
                print("🤖 Generating AI career recommendations...")
                
                # Prepare data for AI analysis
                search_results = job_market_data.get('search_results', [])
                recommendations = generate_career_recommendations(user_profile, search_results[:50])
                
                print("✅ AI recommendations generated successfully")
                return recommendations
            else:
                return self._get_fallback_recommendations(user_profile, job_market_data)
                
        except Exception as e:
            print(f"❌ AI recommendation generation failed: {e}")
            return self._get_fallback_recommendations(user_profile, job_market_data)
    
    def _get_fallback_recommendations(self, user_profile: Dict, job_market_data: Dict) -> Dict:
        """Fallback recommendations when AI generation fails - Generate 5-10 roles"""
        domain = user_profile.get('domain_interest', 'Technology')
        experience_years = user_profile.get('experience_years', 0)
        
        # Get all job positions from market data
        all_job_positions = job_market_data.get('job_positions', [])
        
        # Generate experience-based parameters
        if experience_years < 2:
            level = "Junior"
            salary_range = "$50,000 - $75,000"
            base_skills = ["Python", "JavaScript", "Problem Solving", "Git"]
        elif experience_years < 5:
            level = "Mid-Level"
            salary_range = "$75,000 - $100,000"
            base_skills = ["Python", "JavaScript", "Cloud Computing", "System Design", "Team Collaboration"]
        else:
            level = "Senior"
            salary_range = "$100,000 - $150,000"
            base_skills = ["Python", "JavaScript", "Cloud Computing", "System Architecture", "Leadership", "Mentoring"]
        
        recommendations = []
        
        # If we have job positions from market data, use them all (ensure 5-10 roles)
        if all_job_positions:
            for idx, position in enumerate(all_job_positions):
                # Ensure we have at least 5 and at most 10 positions
                if len(recommendations) >= 10:
                    break
                    
                # Generate role-specific details
                role_skills = base_skills.copy()
                if "data" in position.lower():
                    role_skills.extend(["SQL", "Machine Learning", "Statistics", "Data Visualization"])
                elif "backend" in position.lower() or "api" in position.lower():
                    role_skills.extend(["REST APIs", "Database Design", "Microservices"])
                elif "frontend" in position.lower() or "ui" in position.lower():
                    role_skills.extend(["React", "TypeScript", "CSS", "User Experience"])
                elif "devops" in position.lower() or "cloud" in position.lower():
                    role_skills.extend(["AWS", "Docker", "Kubernetes", "CI/CD"])
                elif "mobile" in position.lower():
                    role_skills.extend(["React Native", "iOS", "Android", "Mobile UI"])
                
                recommendations.append({
                    "job_title": position,
                    "description": f"Exciting opportunity as {position} in {domain} with focus on modern technologies and innovation. Perfect for professionals with {experience_years} years of experience.",
                    "required_skills": role_skills[:6],  # Limit to 6 skills for readability
                    "market_demand": "High demand in current market",
                    "salary_range": salary_range,
                    "transition_strategy": f"Focus on building practical {domain.lower()} projects and gaining relevant certifications. Strengthen skills in {', '.join(role_skills[:3])}."
                })
        
        # If we don't have enough positions, generate standard ones to reach minimum 5
        default_positions = [
            f"{level} {domain} Engineer",
            f"{domain} Developer",
            f"{domain} Specialist",
            f"Full Stack {domain} Developer",
            f"{domain} Software Engineer",
            f"{level} {domain} Architect",
            f"{domain} Technical Lead",
            f"Principal {domain} Engineer",
            f"{domain} Product Engineer",
            f"{domain} Platform Engineer"
        ]
        
        while len(recommendations) < 5:
            for position in default_positions:
                if len(recommendations) >= 10:
                    break
                if not any(rec['job_title'] == position for rec in recommendations):
                    recommendations.append({
                        "job_title": position,
                        "description": f"Exciting opportunities in {domain} with focus on modern technologies and innovation. Ideal for {experience_years} years of experience.",
                        "required_skills": base_skills[:5],
                        "market_demand": "High demand in current market",
                        "salary_range": salary_range,
                        "transition_strategy": "Focus on building practical projects and gaining relevant certifications"
                    })
                if len(recommendations) >= 5:
                    break
        
        return {
            "recommendations": recommendations,
            "total_positions_found": len(all_job_positions),
            "skills_gap_analysis": f"Based on your {experience_years} years of experience in {domain}, focus on developing modern frameworks and cloud technologies to stay competitive. Market analysis found {len(all_job_positions)} relevant positions.",
            "career_roadmap": f"1. Strengthen core {domain} skills\n2. Learn in-demand technologies\n3. Build portfolio projects\n4. Network with industry professionals\n5. Apply for {level.lower()} positions\n6. Explore {len(all_job_positions)} available market opportunities"
        }
    
    def get_complete_analysis(self, 
                            domain_interest: str = "",
                            resume_path: Optional[str] = None,
                            resume_text: Optional[str] = None) -> Dict:
        """Complete career analysis pipeline - Only domain and resume inputs"""
            
        if not domain_interest.strip():
            raise Exception("Domain interest is required for career analysis")
            
        print(f"🎯 Starting complete career analysis for {domain_interest}")
        
        # Step 1: Parse resume if provided (optional)
        resume_data = {}
        if resume_path or resume_text:
            resume_data = self.analyze_resume(resume_path, resume_text)
            print(f"📄 Resume analysis completed")
        
        # Step 2: Build user profile with only domain and resume data
        user_profile = {
            "domain_interest": domain_interest,
            "parsed_resume": resume_data,
            **resume_data  # Merge resume data into profile
        }
        
        # Use default values for other fields
        user_profile.setdefault("experience_years", resume_data.get("experience_years", 0))
        user_profile.setdefault("current_skills", resume_data.get("technical_skills", []))
        user_profile.setdefault("career_goals", f"Advance in {domain_interest} field")
        user_profile.setdefault("location", "United States")
        user_profile.setdefault("work_preference", "Remote")
        user_profile.setdefault("salary_expectations", "")
        
        # Update stored user data
        self.user_data = user_profile
        
        # Step 3: Get job market data
        market_data = self.get_job_market_data(domain_interest, user_profile["location"])
        
        # Step 4: Generate AI recommendations
        recommendations = self.generate_recommendations(user_profile, market_data)
        
        # Step 5: Compile complete analysis
        complete_analysis = {
            "user_profile": user_profile,
            "market_data": market_data,
            "recommendations": recommendations,
            "analysis_summary": {
                "domain": domain_interest,
                "experience_level": f"{user_profile['experience_years']} years",
                "skills_count": len(user_profile['current_skills']),
                "market_demand": market_data.get('market_trends', {}).get('market_analysis', {}).get('market_demand', 'Unknown'),
                "recommended_positions": len(recommendations.get('recommendations', [])),
                "analysis_timestamp": self._get_current_timestamp()
            }
        }
        
        # Store for future reference
        self.last_analysis = complete_analysis
        
        print("✅ Complete career analysis finished successfully")
        return complete_analysis
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp for analysis tracking"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def export_analysis_report(self, format_type: str = "json") -> str:
        """Export the last analysis as a formatted report"""
        if not self.last_analysis:
            return "No analysis available to export"
        
        if format_type.lower() == "json":
            return json.dumps(self.last_analysis, indent=2)
        elif format_type.lower() == "text":
            return self._format_text_report(self.last_analysis)
        else:
            return "Unsupported format type"
    
    def _format_text_report(self, analysis: Dict) -> str:
        """Format analysis as a readable text report"""
        user_profile = analysis.get('user_profile', {})
        recommendations = analysis.get('recommendations', {})
        market_data = analysis.get('market_data', {})
        
        report = f"""
# AI Career Guidance Report

## User Profile
- Domain Interest: {user_profile.get('domain_interest', 'N/A')}
- Experience: {user_profile.get('experience_years', 0)} years
- Current Skills: {', '.join(user_profile.get('current_skills', []))}
- Career Goals: {user_profile.get('career_goals', 'Not specified')}
- Work Preference: {user_profile.get('work_preference', 'Not specified')}

## Market Analysis
- Market Demand: {market_data.get('market_trends', {}).get('market_analysis', {}).get('market_demand', 'Unknown')}
- Job Positions Found: {len(market_data.get('job_positions', []))}
- Remote Opportunities: {market_data.get('market_trends', {}).get('remote_opportunities', {}).get('remote_percentage', 'N/A')}%

## Career Recommendations
"""
        
        for i, rec in enumerate(recommendations.get('recommendations', []), 1):
            report += f"""
### {i}. {rec.get('job_title', 'Unknown Position')}
- **Description:** {rec.get('description', 'No description available')}
- **Required Skills:** {', '.join(rec.get('required_skills', []))}
- **Market Demand:** {rec.get('market_demand', 'Not specified')}
- **Salary Range:** {rec.get('salary_range', 'N/A')}
- **Transition Strategy:** {rec.get('transition_strategy', 'Not specified')}
"""
        
        report += f"""
## Skills Gap Analysis
{recommendations.get('skills_gap_analysis', 'No analysis available')}

## Career Roadmap
{recommendations.get('career_roadmap', 'No roadmap available')}

---
Report generated on: {analysis.get('analysis_summary', {}).get('analysis_timestamp', 'Unknown')}
        """
        
        return report

# Main execution and user input interface
if __name__ == "__main__":
    guidance = AICareerGuidance()
    
    print("=" * 60)
    print("🎯 AI CAREER GUIDANCE - INTERACTIVE MODE")
    print("=" * 60)
    print("Welcome! Let's analyze your career path with AI-powered insights.")
    print()
    
    try:
        # Get user inputs - ONLY domain and resume
        print("📝 Please provide the following information:")
        print()
        
        # Required: Domain of Interest
        while True:
            domain_interest = input("🎯 Domain of Interest (required): ").strip()
            if domain_interest:
                break
            print("❌ Domain of interest is required. Please enter a field like 'Data Science', 'Software Development', etc.")
        
        # Optional: Resume file
        print()
        resume_path = input("📄 Resume file path (optional, press Enter to skip): ").strip()
        if resume_path and not os.path.exists(resume_path):
            print(f"⚠️  Resume file not found: {resume_path}. Continuing without resume...")
            resume_path = None
        
        print()
        print("🚀 Starting career analysis...")
        print("=" * 60)
        
        # Run the analysis with ONLY domain and resume inputs
        result = guidance.get_complete_analysis(
            domain_interest=domain_interest,
            resume_path=resume_path
        )
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 CAREER ANALYSIS RESULTS")
        print("=" * 60)
        
        analysis_summary = result.get('analysis_summary', {})
        print(f"🎯 Domain: {analysis_summary.get('domain', 'N/A')}")
        print(f"📈 Market Demand: {analysis_summary.get('market_demand', 'N/A')}")
        print(f"💼 Recommended Positions: {analysis_summary.get('recommended_positions', 0)}")
        print(f"🛠️  Skills Analyzed: {analysis_summary.get('skills_count', 0)}")
        print(f"⏰ Analysis Time: {analysis_summary.get('analysis_timestamp', 'N/A')}")
        
        # Show recommendations summary
        recommendations = result.get('recommendations', {}).get('recommendations', [])
        if recommendations:
            print(f"\n🎯 TOP CAREER RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
                job_title = rec.get('job_title', f'Recommendation {i}')
                salary = rec.get('salary_range', 'Not specified')
                print(f"   {i}. {job_title} - {salary}")
        
        # Ask if user wants detailed report
        print()
        show_detailed = input("📄 Would you like to see the detailed report? (y/n): ").strip().lower()
        if show_detailed in ['y', 'yes']:
            text_report = guidance.export_analysis_report("text")
            print("\n" + "=" * 60)
            print("📋 DETAILED CAREER ANALYSIS REPORT")
            print("=" * 60)
            print(text_report)
        
        # Ask if user wants to save report
        print()
        save_report = input("💾 Save report to file? (y/n): ").strip().lower()
        if save_report in ['y', 'yes']:
            filename = f"career_analysis_{domain_interest.replace(' ', '_')}_{analysis_summary.get('analysis_timestamp', 'unknown').replace(' ', '_').replace(':', '-')}.txt"
            try:
                with open(filename, 'w') as f:
                    f.write(guidance.export_analysis_report("text"))
                print(f"✅ Report saved as: {filename}")
            except Exception as e:
                print(f"❌ Failed to save report: {e}")
        
        print("\n🎉 Career analysis completed successfully!")
        print("Thank you for using AI Career Guidance!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Analysis interrupted by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please check your inputs and try again.")
    
    print("\n" + "=" * 60)