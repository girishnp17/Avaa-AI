import requests
import os
from dotenv import load_dotenv
import time
import re

load_dotenv()

def search_google_with_api(query, num_results=10, location="United States"):
    """Search Google using Google Custom Search API for job-related content."""
    api_key = os.getenv('GOOGLE_API_KEY')
    search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        print("Warning: Google API key or Search Engine ID not found. Using fallback search.")
        return fallback_search_results(query, num_results)

    base_url = "https://www.googleapis.com/customsearch/v1"

    # Enhance query with location for better job results
    enhanced_query = f"{query} {location}" if location and location.lower() not in query.lower() else query

    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': enhanced_query,
        'num': min(num_results, 10),  # Google API max is 10 per request
        'lr': 'lang_en',
        'safe': 'off'
    }

    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []

        # Extract search results
        if 'items' in data:
            for item in data['items']:
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'displayLink': item.get('displayLink', ''),
                    'position': len(results) + 1
                })

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error during Google Search API request: {e}")
        return fallback_search_results(query, num_results)
    except Exception as e:
        print(f"Unexpected error during search: {e}")
        return fallback_search_results(query, num_results)

def fallback_search_results(query, num_results):
    """Provide fallback search results when API is not available."""
    domain_keywords = query.lower().split()
    
    # Generate mock results based on common job patterns
    fallback_results = []
    job_titles = [
        "Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer",
        "Machine Learning Engineer", "Backend Developer", "Frontend Developer",
        "Full Stack Developer", "Data Analyst", "Business Analyst", "UX Designer",
        "Cloud Engineer", "Security Engineer", "Mobile Developer", "AI Engineer"
    ]
    
    for i, title in enumerate(job_titles[:num_results]):
        if any(keyword in title.lower() for keyword in domain_keywords):
            fallback_results.append({
                'title': f"{title} - Remote/Hybrid Opportunities",
                'link': f"https://example-jobs.com/{title.lower().replace(' ', '-')}",
                'snippet': f"Explore {title} positions with competitive salaries and growth opportunities. Required skills include relevant technical expertise.",
                'displayLink': "careers.example.com",
                'position': i + 1
            })
    
    return fallback_results

def search_multiple_queries(queries, num_results_per_query=10, location="United States"):
    """Search multiple queries and combine results."""
    all_results = []

    for query in queries:
        try:
            results = search_google_with_api(query, num_results_per_query, location)
            all_results.extend(results)
            # Rate limiting for API
            time.sleep(0.1)
        except Exception as e:
            print(f"Error searching query '{query}': {e}")
            continue

    return all_results

def extract_job_positions(search_results):
    """Extract and analyze job positions from Google Search results."""
    job_positions = []

    for result in search_results:
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        combined_text = f"{title} {snippet}"

        # Look for job-related keywords
        job_keywords = [
            'job', 'position', 'role', 'career', 'hiring', 'vacancy', 'opening',
            'employment', 'work', 'opportunity', 'engineer', 'developer', 'analyst',
            'manager', 'specialist', 'consultant', 'scientist', 'architect'
        ]

        # Check if result contains job-related content
        has_job_keywords = any(keyword in combined_text for keyword in job_keywords)

        if has_job_keywords:
            # Extract potential job titles
            extracted_titles = extract_job_titles_from_text(combined_text)
            job_positions.extend(extracted_titles)

    # Remove duplicates and return unique positions
    unique_positions = list(set(job_positions))
    return unique_positions[:20]  # Limit to top 20 positions

def extract_job_titles_from_text(text):
    """Extract job titles from text using advanced pattern matching."""
    job_titles = []

    # Enhanced job title patterns with regex
    patterns = [
        # Specific role patterns
        r'\b(?:senior|junior|lead|principal|staff)?\s*(?:software|data|machine learning|ai|ml)\s+(?:engineer|scientist|developer)\b',
        r'\b(?:frontend|backend|full.?stack|web)\s+developer\b',
        r'\b(?:devops|cloud|security|network|systems)\s+engineer\b',
        r'\b(?:product|project|engineering|data|marketing|sales)\s+manager\b',
        r'\b(?:data|business|financial|systems|cybersecurity)\s+analyst\b',
        r'\b(?:ux|ui|graphic|web)\s+designer\b',
        r'\b(?:software|solution|enterprise|cloud)\s+architect\b',
        
        # General patterns
        r'\b\w+\s+(?:engineer|developer|analyst|manager|specialist|scientist|designer|architect|consultant)\b',
        r'\b(?:engineer|developer|analyst|manager|specialist|scientist|designer|architect|consultant)\b',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            clean_title = ' '.join(match.split()).title()
            if len(clean_title) > 3 and clean_title not in job_titles:
                job_titles.append(clean_title)

    # Additional extraction for common job titles
    common_titles = [
        'Software Engineer', 'Data Scientist', 'Product Manager', 'DevOps Engineer',
        'Machine Learning Engineer', 'Backend Developer', 'Frontend Developer',
        'Full Stack Developer', 'Data Analyst', 'Business Analyst', 'UX Designer',
        'Cloud Engineer', 'Security Engineer', 'Mobile Developer', 'AI Engineer',
        'Site Reliability Engineer', 'Platform Engineer', 'Quality Assurance Engineer'
    ]

    for title in common_titles:
        if title.lower() in text.lower() and title not in job_titles:
            job_titles.append(title)

    return job_titles

def get_job_market_trends(domain, location="United States"):
    """Get comprehensive job market trends for a specific domain."""
    enhanced_queries = [
        f"{domain} jobs 2025 trends",
        f"{domain} engineer salary 2025",
        f"{domain} developer remote jobs",
        f"best {domain} careers 2025",
        f"{domain} specialist positions",
        f"{domain} job market demand",
        f"hiring {domain} professionals"
    ]

    print(f"🔍 Searching job market trends for {domain}...")
    search_results = search_multiple_queries(enhanced_queries, num_results_per_query=8, location=location)
    job_positions = extract_job_positions(search_results)

    # Analyze trends from search results
    trend_analysis = analyze_market_trends(search_results, domain)

    return {
        'domain': domain,
        'location': location,
        'search_results': search_results,
        'job_positions': job_positions,
        'total_results': len(search_results),
        'unique_positions': len(job_positions),
        'trending_skills': extract_trending_skills(search_results, domain),
        'market_analysis': trend_analysis,
        'salary_insights': extract_salary_insights(search_results),
        'remote_opportunities': count_remote_opportunities(search_results)
    }

def analyze_market_trends(search_results, domain):
    """Analyze market trends from search results."""
    demand_indicators = ['high demand', 'growing field', 'increasing', 'expanding', 'hot job']
    skill_indicators = ['required skills', 'must have', 'essential', 'preferred']
    
    trend_score = 0
    for result in search_results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        for indicator in demand_indicators:
            if indicator in text:
                trend_score += 1
    
    if trend_score >= 5:
        market_demand = "Very High"
    elif trend_score >= 3:
        market_demand = "High"
    elif trend_score >= 1:
        market_demand = "Moderate"
    else:
        market_demand = "Emerging"
    
    return {
        'market_demand': market_demand,
        'trend_score': trend_score,
        'growth_indicators': trend_score
    }

def extract_trending_skills(search_results, domain):
    """Extract trending skills from search results."""
    tech_skills = [
        'python', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker', 
        'kubernetes', 'tensorflow', 'pytorch', 'sql', 'mongodb', 'redis',
        'machine learning', 'ai', 'data science', 'cloud computing', 'devops'
    ]
    
    skill_mentions = {}
    for result in search_results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        for skill in tech_skills:
            if skill in text:
                skill_mentions[skill] = skill_mentions.get(skill, 0) + 1
    
    # Return top 10 trending skills
    sorted_skills = sorted(skill_mentions.items(), key=lambda x: x[1], reverse=True)
    return [skill for skill, count in sorted_skills[:10]]

def extract_salary_insights(search_results):
    """Extract salary information from search results."""
    salary_pattern = r'\$[\d,]+(?:\s*-\s*\$[\d,]+)?'
    salaries = []
    
    for result in search_results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        salary_matches = re.findall(salary_pattern, text)
        salaries.extend(salary_matches)
    
    return {
        'salary_mentions': len(salaries),
        'sample_ranges': salaries[:5] if salaries else ['Data not available']
    }

def count_remote_opportunities(search_results):
    """Count remote work opportunities from search results."""
    remote_keywords = ['remote', 'work from home', 'distributed', 'anywhere', 'virtual']
    remote_count = 0
    
    for result in search_results:
        text = f"{result.get('title', '')} {result.get('snippet', '')}".lower()
        if any(keyword in text for keyword in remote_keywords):
            remote_count += 1
    
    total_results = len(search_results)
    remote_percentage = (remote_count / total_results * 100) if total_results > 0 else 0
    
    return {
        'remote_jobs_found': remote_count,
        'total_jobs': total_results,
        'remote_percentage': round(remote_percentage, 1)
    }
