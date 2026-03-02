import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def calculate_ats_score(resume_text, jd_analysis):
    """
    Calculate TWO scores:
    1. ATS Reality Score - exact matching like real Taleo/Workday/Greenhouse systems
    2. True Match Score - semantic understanding of actual skills
    """

    required_skills = jd_analysis.get("required_skills", [])
    ats_keywords = jd_analysis.get("ats_keywords", [])
    tech_stack = jd_analysis.get("tech_stack", [])
    resume_lower = resume_text.lower()

    # ── SCORE 1: ATS REALITY (exact string match like real ATS) ──
    exact_matched_required = []
    exact_missing_required = []
    for skill in required_skills:
        if skill.lower() in resume_lower:
            exact_matched_required.append(skill)
        else:
            exact_missing_required.append(skill)

    exact_matched_keywords = []
    exact_missing_keywords = []
    for keyword in ats_keywords:
        if keyword.lower() in resume_lower:
            exact_matched_keywords.append(keyword)
        else:
            exact_missing_keywords.append(keyword)

    exact_matched_tech = []
    exact_missing_tech = []
    for tech in tech_stack:
        if tech.lower() in resume_lower:
            exact_matched_tech.append(tech)
        else:
            exact_missing_tech.append(tech)

    # Weighted ATS reality score
    skills_score = (len(exact_matched_required) / len(required_skills) * 50) if required_skills else 25
    keywords_score = (len(exact_matched_keywords) / len(ats_keywords) * 30) if ats_keywords else 15
    tech_score = (len(exact_matched_tech) / len(tech_stack) * 20) if tech_stack else 10
    ats_reality_score = round(skills_score + keywords_score + tech_score)

    # ── SCORE 2: TRUE MATCH (semantic - what you actually know) ──
    prompt = f"""
    You are a senior technical recruiter with 10 years experience.

    Evaluate if this resume TRULY demonstrates each skill through:
    - Direct mention (exact words)
    - Related experience (built X which requires Y)
    - Coursework or education
    - Project work

    Required Skills: {', '.join(required_skills)}
    ATS Keywords: {', '.join(ats_keywords)}
    Tech Stack: {', '.join(tech_stack)}

    Resume:
    {resume_text[:2000]}

    Return JSON only:
    {{
        "truly_matched_required": ["skill1", "skill2"],
        "truly_missing_required": ["skill3"],
        "truly_matched_keywords": ["keyword1"],
        "truly_missing_keywords": ["keyword2"],
        "truly_matched_tech": ["tech1"],
        "truly_missing_tech": ["tech2"]
    }}

    Rules:
    - Return JSON only, no markdown, no explanation
    - Only mark as matched if there is REAL evidence in the resume
    - Do NOT give benefit of the doubt without evidence
    - Be honest and strict
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        semantic = json.loads(raw)

        true_matched_req = len(semantic.get("truly_matched_required", []))
        true_matched_kw = len(semantic.get("truly_matched_keywords", []))
        true_matched_tech = len(semantic.get("truly_matched_tech", []))

        true_skills_score = (true_matched_req / len(required_skills) * 50) if required_skills else 25
        true_keywords_score = (true_matched_kw / len(ats_keywords) * 30) if ats_keywords else 15
        true_tech_score = (true_matched_tech / len(tech_stack) * 20) if tech_stack else 10
        true_match_score = round(true_skills_score + true_keywords_score + true_tech_score)

    except Exception:
        semantic = {}
        true_match_score = ats_reality_score

    return {
        # ATS Reality (exact match)
        "ats_reality_score": ats_reality_score,
        "total_score": ats_reality_score,
        "matched_required_skills": len(exact_matched_required),
        "total_required_skills": len(required_skills),
        "matched_keywords": len(exact_matched_keywords),
        "total_keywords": len(ats_keywords),
        "matched_tech": len(exact_matched_tech),
        "total_tech": len(tech_stack),
        "matched_required_list": exact_matched_required,
        "missing_required_list": exact_missing_required,
        "matched_keywords_list": exact_matched_keywords,
        "missing_keywords_list": exact_missing_keywords,
        "matched_tech_list": exact_matched_tech,
        "missing_tech_list": exact_missing_tech,

        # True Match (semantic)
        "true_match_score": true_match_score,
        "truly_matched_required": semantic.get("truly_matched_required", []),
        "truly_missing_required": semantic.get("truly_missing_required", []),
        "truly_matched_keywords": semantic.get("truly_matched_keywords", []),
        "truly_missing_keywords": semantic.get("truly_missing_keywords", []),
        "truly_matched_tech": semantic.get("truly_matched_tech", []),
        "truly_missing_tech": semantic.get("truly_missing_tech", []),

        # Gap = optimization opportunity
        "optimization_gap": true_match_score - ats_reality_score
    }


def find_skill_gaps(resume_text, jd_analysis, ats_score_details=None):
    """Find what skills are missing - uses ATS reality results for consistency"""

    # Use exact matching results from ATS reality score
    if ats_score_details:
        missing_required = ats_score_details.get("missing_required_list", [])
    else:
        resume_lower = resume_text.lower()
        required_skills = jd_analysis.get("required_skills", [])
        missing_required = [
            skill for skill in required_skills
            if skill.lower() not in resume_lower
        ]

    # Nice to have uses basic matching
    resume_lower = resume_text.lower()
    nice_to_have = jd_analysis.get("nice_to_have_skills", [])
    missing_nice = [
        skill for skill in nice_to_have
        if skill.lower() not in resume_lower
    ]

    return {
        "missing_required": missing_required,
        "missing_nice_to_have": missing_nice
    }


def match_github_to_gaps(gaps, github_projects):
    """Find which GitHub projects fill the skill gaps"""

    if not github_projects or not gaps["missing_required"]:
        return []

    missing_skills_text = ", ".join(gaps["missing_required"])

    projects_text = ""
    for project in github_projects:
        projects_text += f"""
Project: {project['name']}
Tech Stack: {', '.join(project.get('tech_stack', []))}
Skills: {', '.join(project.get('skills_demonstrated', []))}
Description: {project.get('description', '')}
---
"""

    prompt = f"""
    You are an expert technical recruiter.

    A candidate is missing these required skills for a job:
    {missing_skills_text}

    Here are their GitHub projects:
    {projects_text}

    Find which projects demonstrate the missing skills and recommend
    which to ADD to their resume with specific reasons.

    Return as JSON array:
    [
        {{
            "project_name": "name",
            "fills_gap_for": ["skill1", "skill2"],
            "reason": "specific explanation of why this project demonstrates these skills",
            "impact": "high / medium / low"
        }}
    ]

    Rules:
    - Return JSON array only, no explanation, no markdown
    - Only recommend projects that genuinely fill a gap
    - Be specific in the reason
    - If no projects fill the gaps return empty array []
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw)

    except Exception:
        return []


def get_weak_projects(resume_text, jd_analysis, github_projects):
    """Find projects on resume that are irrelevant to this job"""

    if not github_projects:
        return []

    jd_tech = jd_analysis.get("tech_stack", [])
    jd_skills = jd_analysis.get("required_skills", [])

    projects_text = ""
    for project in github_projects:
        projects_text += f"""
Project: {project['name']}
Tech Stack: {', '.join(project.get('tech_stack', []))}
Skills: {', '.join(project.get('skills_demonstrated', []))}
---
"""

    prompt = f"""
    You are an expert technical recruiter reviewing a candidate's GitHub projects
    for a specific job role.

    Job requires these skills: {', '.join(jd_skills)}
    Job tech stack: {', '.join(jd_tech)}

    Candidate's projects:
    {projects_text}

    Identify projects that are WEAK or IRRELEVANT for this specific job.

    Return as JSON array:
    [
        {{
            "project_name": "name",
            "reason": "why this project is weak/irrelevant for this role",
            "suggestion": "what to do instead"
        }}
    ]

    Rules:
    - Return JSON array only, no explanation, no markdown
    - Only flag genuinely irrelevant projects
    - Be constructive in suggestions
    - If all projects are relevant return empty array []
    """

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        return json.loads(raw)

    except Exception:
        return []


def run_full_match(resume_text, jd_analysis, github_projects):
    """Master function - runs complete matching analysis"""

    # Step 1 - ATS Score (both reality and semantic)
    ats_score = calculate_ats_score(resume_text, jd_analysis)

    # Step 2 - Find gaps using ATS reality results
    gaps = find_skill_gaps(resume_text, jd_analysis, ats_score)

    # Step 3 - Match GitHub projects to gaps
    github_recommendations = match_github_to_gaps(gaps, github_projects)

    # Step 4 - Find weak projects
    weak_projects = get_weak_projects(resume_text, jd_analysis, github_projects)

    return {
        "ats_score": ats_score,
        "gaps": gaps,
        "github_recommendations": github_recommendations,
        "weak_projects": weak_projects
    }