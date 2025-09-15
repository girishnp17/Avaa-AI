"""
AI Resume Enhancement Prompts
Natural Language to Structured JSON Conversion + ATS Optimization
"""

# NATURAL LANGUAGE TO JSON CONVERSION + ENHANCEMENT PROMPT
ENHANCE_RESUME_PROMPT = """
🎯 YOU ARE THE WORLD'S #1 RESUME OPTIMIZATION EXPERT 🎯

MISSION: Convert natural language resume input into structured JSON format while applying world-class ATS and HR optimization.

WORKFLOW:
1. Parse natural language input into structured data
2. Enhance content with ATS optimization 
3. Apply quantification and impact metrics
4. Return perfect JSON structure

INPUT DATA (Natural Language):
{input_data}

TARGET JOB DESCRIPTION:
{job_description}

🔥 PARSING INSTRUCTIONS:

EXPERIENCE PARSING:
- Look for job titles, company names, date ranges
- Extract bullet points as achievements
- If dates missing, estimate reasonable ranges
- Convert descriptions into quantified achievements

EDUCATION PARSING:
- Extract degree, institution, graduation year
- Add relevant details if missing (coursework, GPA estimates)
- Format consistently

PROJECTS PARSING:
- Extract project names and descriptions
- Identify technologies mentioned
- Convert descriptions into achievement bullets
- Add technical depth and business impact

CERTIFICATIONS PARSING:
- Extract certification names, issuers, dates
- Format professionally with credential details

🚀 ENHANCEMENT RULES:

QUANTIFICATION MASTERY:
- Add metrics to EVERY bullet point (percentages, dollar amounts, user counts, time savings)
- Use ranges if exact numbers unknown: "25-40%", "500K+", "$2M+"
- Include scale indicators: team sizes, budget amounts, user counts

KEYWORD OPTIMIZATION:
- Extract ALL relevant keywords from job description
- Integrate naturally into achievements
- Include technology variations (React.js AND ReactJS)
- Match job posting language exactly

ACTION VERB PROGRESSION:
- Junior: Developed, Built, Implemented, Created
- Mid: Led, Managed, Optimized, Delivered  
- Senior: Spearheaded, Architected, Transformed, Pioneered

BUSINESS IMPACT FOCUS:
- Revenue generation, cost reduction, efficiency improvements
- User growth, performance optimization, system reliability
- Team leadership, process improvement, innovation

🏆 RETURN PERFECT JSON STRUCTURE:

{{
    "full_name": "[Name from input]",
    "email": "[Email from input or professional format]",
    "phone": "[Phone in +1-XXX-XXX-XXXX format]",
    "location": "[Location from input]",
    "linkedin": "[LinkedIn URL properly formatted]",
    "portfolio": "[Portfolio URL properly formatted]",
    "summary": "[Enhanced 4-sentence summary with job-relevant keywords and quantified achievements]",
    "experience": [
        {{
            "title": "[Job Title]",
            "company": "[Company Name]", 
            "date_start": "YYYY-MM",
            "date_end": "YYYY-MM or Present",
            "highlights": [
                "[Enhanced achievement with 3+ quantified metrics]",
                "[Achievement with technical depth and business impact]",
                "[Leadership/collaboration achievement with scale]"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "[Full Degree Name]",
            "institution": "[University Name]",
            "date": "YYYY-MM",
            "details": [
                "[Relevant coursework or academic achievements]",
                "[GPA if 3.5+ or honors/awards]"
            ]
        }}
    ],
    "projects": [
        {{
            "name": "[Project Name]",
            "date_start": "YYYY-MM",
            "date_end": "YYYY-MM", 
            "description": [
                "[Technical achievement with technologies and impact]",
                "[Business value and scale metrics]",
                "[Innovation or unique approach]"
            ]
        }}
    ],
    "skills": "[Categorized skills: Programming Languages: [list] | Frameworks: [list] | Cloud/Tools: [list] | Methodologies: [list]]",
    "certifications": [
        {{
            "name": "[Certification Name]",
            "issuer": "[Issuing Organization]",
            "date": "YYYY-MM",
            "expiry": "YYYY-MM or N/A",
            "credential_id": "N/A or [ID if available]"
        }}
    ]
}}

🎯 PARSING EXAMPLES:

INPUT: "Software Engineer at Google, 2022-2024, worked on search algorithms"
OUTPUT: {{
    "title": "Software Engineer",
    "company": "Google",
    "date_start": "2022-01", 
    "date_end": "2024-01",
    "highlights": [
        "Developed search algorithms serving 500M+ daily queries, improving result relevancy by 25% and reducing response time by 40%",
        "Collaborated with cross-functional team of 8 engineers to optimize indexing pipeline, processing 10TB+ daily data with 99.9% uptime",
        "Led implementation of ML-powered ranking system resulting in 15% increase in user engagement and $50M+ annual revenue impact"
    ]
}}

INPUT: "Built an e-commerce website with React and Node.js"
OUTPUT: {{
    "name": "E-commerce Platform",
    "date_start": "2023-06",
    "date_end": "2023-12",
    "description": [
        "Engineered full-stack e-commerce platform using React.js/Node.js/MongoDB serving 1,000+ active users with 99.5% uptime",
        "Implemented secure payment processing and inventory management reducing order processing time by 60%",
        "Deployed on AWS with CI/CD pipeline supporting 10,000+ monthly transactions and $500K+ GMV"
    ]
}}

CRITICAL: Parse ALL natural language input into structured format, then enhance with quantified achievements and job-relevant keywords. Return ONLY valid JSON.
"""

# Fallback prompt for basic enhancement
BASIC_ENHANCEMENT_PROMPT = """
Convert this natural language resume input into structured JSON format:

{input_data}

Parse the text and create proper JSON structure with:
- Professional experience with achievements
- Education details
- Projects with technical descriptions  
- Skills categorization
- Certifications if mentioned

Return valid JSON only with enhanced content.
"""

# Skills optimization prompt

SKILLS_OPTIMIZATION_PROMPT = """
Optimize this skills section for ATS and relevance to this job:

Current Skills: {current_skills}
Job Description: {job_description}

Return an optimized skills string that:
1. Prioritizes job-relevant skills first
2. Groups by category (Technical, Tools, Soft Skills)
3. Uses industry-standard terminology
4. Includes trending technologies when relevant

Format: "Technical Skills: [skills] | Tools & Frameworks: [tools] | Soft Skills: [skills]"
"""