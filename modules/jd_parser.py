import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def parse_job_description(jd_text):
    """Extract structured information from job description"""
    
    prompt = f"""
    You are an expert ATS system and technical recruiter.
    
    Analyze this job description and extract the following in JSON format:
    
    {{
        "job_title": "exact job title",
        "company_name": "company name if mentioned",
        "required_skills": ["skill1", "skill2"],
        "nice_to_have_skills": ["skill1", "skill2"],
        "experience_required": "X years",
        "education_required": "degree requirement if any",
        "key_responsibilities": ["responsibility1", "responsibility2"],
        "ats_keywords": ["keyword1", "keyword2"],
        "tech_stack": ["technology1", "technology2"],
        "soft_skills": ["skill1", "skill2"]
    }}
    
    Rules:
    - Return JSON only, no explanation, no markdown
    - ATS keywords should be exact phrases from the job description
    - Be thorough with required skills, miss nothing
    - If something is not mentioned put an empty list
    
    Job Description:
    {jd_text}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        raw = response.choices[0].message.content.strip()
        
        # Clean response if LLM adds markdown
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        
        return json.loads(raw), None
    
    except json.JSONDecodeError:
        return None, "Failed to parse job description. Try again."
    except Exception as e:
        return None, f"Error analyzing job description: {str(e)}"