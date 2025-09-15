"""
AI Resume Generator - Clean implementation
"""

import json
import re
import os
import subprocess
import tempfile
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from prompts.enhancement_prompts import ENHANCE_RESUME_PROMPT, BASIC_ENHANCEMENT_PROMPT
from templates.latex_templates import MINIMAL_TECH_TEMPLATE

class AIResumeGenerator:
    def __init__(self, api_key: str = None, template_type: str = "tech"):
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.template = MINIMAL_TECH_TEMPLATE
        
    def enhance_resume_with_ai(self, raw_data: Dict[str, Any], job_description: str = "") -> Dict[str, Any]:
        try:
            input_data_str = self._format_input_data(raw_data)
            prompt = ENHANCE_RESUME_PROMPT.format(
                input_data=input_data_str,
                job_description=job_description or "No specific job description provided"
            )
            
            response = self.model.generate_content(prompt)
            enhanced_data = self._extract_json_from_response(response.text.strip())
            
            if enhanced_data:
                return enhanced_data
            else:
                return self._fallback_enhancement(raw_data)
                
        except Exception as e:
            return self._fallback_enhancement(raw_data)
    
    def _format_input_data(self, raw_data: Dict[str, Any]) -> str:
        formatted_lines = []
        for key, value in raw_data.items():
            if isinstance(value, (list, dict)):
                formatted_lines.append(f"{key.title()}: {json.dumps(value, indent=2)}")
            else:
                formatted_lines.append(f"{key.title()}: {value}")
        return "\n".join(formatted_lines)
    
    def _extract_json_from_response(self, content: str) -> Optional[Dict[str, Any]]:
        try:
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            
            if not json_match:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
            
            return json.loads(content)
        except json.JSONDecodeError:
            return None
    
    def _fallback_enhancement(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = BASIC_ENHANCEMENT_PROMPT.format(input_data=str(raw_data))
            response = self.model.generate_content(prompt)
            enhanced_data = self._extract_json_from_response(response.text)
            if enhanced_data:
                return enhanced_data
        except:
            pass
        
        return self._clean_raw_data(raw_data)
    
    def _clean_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "full_name": raw_data.get("full_name", "Your Name"),
            "email": raw_data.get("email", "your.email@example.com"),
            "phone": raw_data.get("phone", "+1-xxx-xxx-xxxx"),
            "location": raw_data.get("location", "Your Location"),
            "linkedin": raw_data.get("linkedin", "linkedin.com/in/yourprofile"),
            "portfolio": raw_data.get("portfolio", "yourportfolio.com"),
            "summary": raw_data.get("summary", "Professional summary"),
            "experience": raw_data.get("experience", []),
            "education": raw_data.get("education", []),
            "projects": raw_data.get("projects", []),
            "skills": raw_data.get("skills", "Skills"),
            "certifications": raw_data.get("certifications", [])
        }
    
    def generate_latex_content(self, enhanced_data: Dict[str, Any]) -> str:
        escaped_data = self._escape_latex_data(enhanced_data)
        
        template_vars = {
            "full_name": escaped_data.get("full_name", "Your Name"),
            "email": escaped_data.get("email", "your.email@example.com"),
            "phone": escaped_data.get("phone", "+1-xxx-xxx-xxxx"),
            "location": escaped_data.get("location", "Your Location"),
            "linkedin_url": self._format_url(escaped_data.get("linkedin", "")),
            "portfolio_url": self._format_url(escaped_data.get("portfolio", "")),
            "summary": escaped_data.get("summary", "Professional summary"),
            "experience_section": self._format_experience_section(escaped_data.get("experience", [])),
            "education_section": self._format_education_section(escaped_data.get("education", [])),
            "projects_section": self._format_projects_section(escaped_data.get("projects", [])),
            "skills": escaped_data.get("skills", "Skills"),
            "certifications_section": self._format_certifications_section(escaped_data.get("certifications", []))
        }
        
        return self.template.format(**template_vars)
    
    def _escape_latex_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        escaped = {}
        for key, value in data.items():
            if isinstance(value, str):
                escaped[key] = self._escape_latex_string(value)
            elif isinstance(value, list):
                escaped[key] = [
                    self._escape_latex_dict(item) if isinstance(item, dict) 
                    else self._escape_latex_string(str(item))
                    for item in value
                ]
            else:
                escaped[key] = value
        return escaped
    
    def _escape_latex_string(self, text: str) -> str:
        if not text:
            return text
        
        # Simple and safe LaTeX escaping
        latex_special_chars = {
            '&': r'\&',
            '%': r'\%', 
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
        }
        
        for char, replacement in latex_special_chars.items():
            text = text.replace(char, replacement)
        
        return text
    
    def _escape_latex_dict(self, item: Dict[str, Any]) -> Dict[str, Any]:
        escaped = {}
        for k, v in item.items():
            if isinstance(v, str):
                escaped[k] = self._escape_latex_string(v)
            elif isinstance(v, list):
                escaped[k] = [self._escape_latex_string(str(x)) for x in v]
            else:
                escaped[k] = v
        return escaped
    
    def _format_url(self, url: str) -> str:
        if not url:
            return "https://example.com"
        if url.startswith("http"):
            return url
        return f"https://{url}"
    
    def _format_experience_section(self, experience_list: list) -> str:
        if not experience_list:
            return "\\sectiontitle{Professional Experience}\n\\noindent No experience provided.\\\\[5pt]\n"
        
        content = "\\sectiontitle{Professional Experience}\n"
        for exp in experience_list:
            title = exp.get("title", "Job Title")
            company = exp.get("company", "Company Name")
            date_start = exp.get("date_start", "Start")
            date_end = exp.get("date_end", "End")
            
            content += f"\\jobtitle{{{title}}}{{{company}}}{{{date_start}}}{{{date_end}}}\n"
            
            for highlight in exp.get("highlights", []):
                content += f"\\achievement{{{highlight}}}\n"
            
            content += "\\vspace{{5pt}}\n"
        
        return content
    
    def _format_education_section(self, education_list: list) -> str:
        if not education_list:
            return "\\sectiontitle{Education}\n\\noindent Education information to be provided.\\\\[5pt]\n"
        
        content = "\\sectiontitle{Education}\n"
        for edu in education_list:
            degree = edu.get("degree", "Degree")
            institution = edu.get("institution", "Institution")
            date = edu.get("date", "Date")
            
            content += f"\\education{{{degree}}}{{{institution}}}{{{date}}}\n"
            
            for detail in edu.get("details", []):
                content += f"\\achievement{{{detail}}}\n"
            
            content += "\\vspace{{5pt}}\n"
        
        return content
    
    def _format_projects_section(self, projects_list: list) -> str:
        if not projects_list:
            return "\\sectiontitle{Key Projects}\n\\noindent Key projects to be added.\\\\[5pt]\n"
        
        content = "\\sectiontitle{Key Projects}\n"
        for proj in projects_list:
            name = proj.get("name", "Project Name")
            date_range = f"{proj.get('date_start', 'Start')} - {proj.get('date_end', 'End')}"
            tech_stack = ", ".join(proj.get("technologies", [])) if proj.get("technologies") else ""
            
            content += f"\\projectheader{{{name}}}{{{date_range}}}{{{tech_stack}}}\n"
            
            for desc in proj.get("description", []):
                content += f"\\achievement{{{desc}}}\n"
            
            content += "\\vspace{{5pt}}\n"
        
        return content
    
    def _format_certifications_section(self, certifications_list: list) -> str:
        if not certifications_list:
            return ""
        
        content = "\\sectiontitle{Certifications}\n"
        for cert in certifications_list:
            name = cert.get("name", "Certification Name")
            issuer = cert.get("issuer", "Issuing Organization")
            date = cert.get("date", "Date")
            
            content += f"\\noindent\\textbf{{{name} - {issuer}}} \\hfill \\textit{{{date}}}\\\\[2pt]\n"
        
        return content
    
    def compile_latex_to_pdf(self, latex_content: str, output_name: str = "resume") -> Optional[str]:
        """Compile LaTeX to PDF with better error handling"""
        try:
            # Create output directory if it doesn't exist
            os.makedirs("output", exist_ok=True)
            
            # Write LaTeX file directly to output directory
            tex_file = f"output/{output_name}.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            print(f"✅ LaTeX file written: {tex_file}")
            
            # Compile with simpler approach
            try:
                result = subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory=output',
                    tex_file
                ], capture_output=True, text=True, timeout=30, cwd=os.getcwd())
                
                pdf_file = f"output/{output_name}.pdf"
                
                if os.path.exists(pdf_file):
                    # Copy to main directory for easier access
                    final_pdf = f"{output_name}.pdf"
                    import shutil
                    shutil.copy2(pdf_file, final_pdf)
                    print(f"✅ PDF created: {final_pdf}")
                    return final_pdf
                else:
                    print(f"❌ PDF not created. LaTeX errors:")
                    print(result.stdout[-500:] if result.stdout else "No stdout")
                    print(result.stderr[-500:] if result.stderr else "No stderr")
                    return None
                    
            except subprocess.TimeoutExpired:
                print("❌ LaTeX compilation timed out")
                return None
            except FileNotFoundError:
                print("❌ pdflatex not found. Please install LaTeX.")
                return None
                
        except Exception as e:
            print(f"❌ PDF compilation error: {str(e)}")
            return None
    
    def generate_resume(self, raw_data: Dict[str, Any], job_description: str = "", 
                       output_name: str = "resume") -> Optional[str]:
        enhanced_data = self.enhance_resume_with_ai(raw_data, job_description)
        latex_content = self.generate_latex_content(enhanced_data)
        return self.compile_latex_to_pdf(latex_content, output_name)