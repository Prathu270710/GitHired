import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

def generate_cover_letter(resume_text, jd_analysis, match_results):
    """Generate a human-sounding cover letter outline"""
    
    job_title = jd_analysis.get("job_title", "the role")
    company_name = jd_analysis.get("company_name", "your company")
    required_skills = jd_analysis.get("required_skills", [])
    responsibilities = jd_analysis.get("key_responsibilities", [])
    github_recommendations = match_results.get("github_recommendations", [])
    
    # Build context about strong projects to mention
    projects_to_mention = ""
    for proj in github_recommendations[:3]:
        projects_to_mention += f"- {proj['project_name']}: {proj['reason']}\n"
    
    prompt = f"""
    You are an expert career coach writing a cover letter for a software developer.
    
    Job Title: {job_title}
    Company: {company_name}
    Required Skills: {', '.join(required_skills[:10])}
    Key Responsibilities: {', '.join(responsibilities[:5])}
    
    Candidate Resume Summary:
    {resume_text[:1500]}
    
    Strong Projects to Mention:
    {projects_to_mention if projects_to_mention else "Use projects from resume"}
    
    Write a cover letter following these strict rules:
    
    1. TONE - Write like a real human, not an AI. Use natural conversational 
       language. Avoid corporate buzzwords like "leverage", "synergy", 
       "passionate", "dynamic", "rockstar"
       
    2. STRUCTURE - Four paragraphs only:
       - Opening: Why this specific company and role (not generic)
       - Skills paragraph: Connect 2-3 specific skills to specific responsibilities
       - Project paragraph: Mention 1-2 specific projects and what they achieved
       - Closing: Clear call to action, one sentence
       
    3. LENGTH - Maximum 250 words. Recruiters don't read long cover letters.
    
    4. SPECIFICITY - Every sentence must be specific to this role and company.
       Zero generic statements.
       
    5. AVOID - Do not use these phrases:
       - "I am passionate about"
       - "I would be a great fit"  
       - "I am a fast learner"
       - "leverage my skills"
       - "I am excited to apply"
       - Any variation of these
    
    6. HUMAN FEEL - Add one small specific detail that makes it feel personal
       and real, not AI generated
    
    After the cover letter add this section:

    ---PERSONALIZATION NOTES---
    List 3 specific things the candidate should manually customize:
    1. [specific thing to add about the company]
    2. [specific experience to mention]  
    3. [specific achievement to add with numbers]
    
    This will make the cover letter uniquely theirs and undetectable as AI.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip(), None
    
    except Exception as e:
        return None, f"Error generating cover letter: {str(e)}"

def generate_resume_suggestions(resume_text, jd_analysis, match_results):
    """Generate specific suggestions to improve resume for this job"""
    
    gaps = match_results.get("gaps", {})
    missing_required = gaps.get("missing_required", [])
    ats_score = match_results.get("ats_score", {})
    weak_projects = match_results.get("weak_projects", [])
    github_recs = match_results.get("github_recommendations", [])
    
    prompt = f"""
    You are an expert ATS optimization specialist.
    
    Current ATS Score: {ats_score.get('total_score', 0)}%
    Missing Required Skills: {', '.join(missing_required)}
    Weak Projects to Remove: {', '.join([p['project_name'] for p in weak_projects])}
    Projects to Add: {', '.join([p['project_name'] for p in github_recs])}
    
    Resume:
    {resume_text[:1500]}
    
    Give exactly 5 specific, actionable resume improvements.
    
    Format each as:
    CHANGE [number]: [what to change]
    WHY: [why this improves ATS score]
    HOW: [exactly how to rewrite it]
    
    Rules:
    - Be extremely specific, not generic
    - Focus on ATS optimization
    - Each suggestion must directly improve the score
    - No fluff, no encouragement, just actionable changes
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip(), None
    
    except Exception as e:
        return None, f"Error generating suggestions: {str(e)}"