import os
import json
import base64
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_github_projects(username):
    """Fetch all public repos from GitHub username"""
    
    try:
        url = f"https://api.github.com/users/{username}/repos?per_page=50&sort=updated"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 404:
            return None, "GitHub username not found. Please check the username."
        
        if response.status_code != 200:
            return None, f"GitHub API error: {response.status_code}"
        
        repos = response.json()
        
        if not repos:
            return None, "No public repositories found for this username."
        
        projects = []
        for repo in repos:
            # Skip forked repos - they dont show your skills
            if repo.get('fork', False):
                continue
                
            readme_text = get_readme(username, repo['name'])
            
            projects.append({
                "name": repo['name'],
                "description": repo.get('description', '') or '',
                "language": repo.get('language', 'Unknown') or 'Unknown',
                "stars": repo.get('stargazers_count', 0),
                "readme": readme_text[:1500]
            })
        
        return projects, None
    
    except Exception as e:
        return None, f"Error fetching GitHub projects: {str(e)}"

def get_readme(username, repo_name):
    """Fetch README content for a specific repo"""
    
    try:
        url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            content = response.json().get('content', '')
            decoded = base64.b64decode(content).decode('utf-8')
            return decoded
        
        return "No README found"
    
    except Exception:
        return "Could not fetch README"

def analyze_projects_with_llm(projects):
    """Use Groq to understand what each project demonstrates"""
    
    if not projects:
        return None, "No projects to analyze"
    
    projects_text = ""
    for i, project in enumerate(projects):
        projects_text += f"""
Project {i+1}: {project['name']}
Language: {project['language']}
Description: {project['description']}
README: {project['readme'][:800]}
---
"""
    
    prompt = f"""
    You are a technical recruiter analyzing GitHub projects.
    
    For each project extract the following and return as JSON array:
    
    [
        {{
            "name": "project name",
            "tech_stack": ["technology1", "technology2"],
            "skills_demonstrated": ["skill1", "skill2"],
            "project_type": "web app / mobile / API / data science / devops / other",
            "complexity": "simple / medium / complex",
            "description": "one line description of what it does"
        }}
    ]
    
    Rules:
    - Return JSON array only, no explanation, no markdown
    - Be thorough with tech stack - include frameworks, databases, tools
    - Skills demonstrated should map to real job requirements
    - If README is missing make your best guess from the project name and language
    
    Projects:
    {projects_text}
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
        
        analyzed = json.loads(raw)
        return analyzed, None
    
    except json.JSONDecodeError:
        return None, "Failed to analyze projects. Try again."
    except Exception as e:
        return None, f"Error analyzing projects: {str(e)}"

def get_analyzed_github_projects(username):
    """Main function - fetch and analyze all projects"""
    
    projects, error = get_github_projects(username)
    if error:
        return None, error
    
    analyzed, error = analyze_projects_with_llm(projects)
    if error:
        return None, error
    
    return analyzed, None

def analyze_projects_from_document(file_path):
    """Analyze projects from an uploaded document instead of GitHub"""
    
    import PyPDF2
    import docx as docx_lib
    
    try:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        
        elif ext == '.docx':
            doc = docx_lib.Document(file_path)
            text = "\n".join([p.text for p in doc.paragraphs])
        
        else:
            return None, "Unsupported file format. Use PDF or DOCX."
        
        if not text.strip():
            return None, "Could not extract text from document."
        
        prompt = f"""
        You are a technical recruiter analyzing a candidate's project portfolio document.
        
        Extract all projects mentioned in this document and return as JSON array:
        
        [
            {{
                "name": "project name",
                "tech_stack": ["technology1", "technology2"],
                "skills_demonstrated": ["skill1", "skill2"],
                "project_type": "web app / mobile / API / data science / devops / other",
                "complexity": "simple / medium / complex",
                "description": "one line description of what it does"
            }}
        ]
        
        Rules:
        - Return JSON array only, no explanation, no markdown
        - Extract every project mentioned even if details are limited
        - Infer tech stack from context if not explicitly stated
        - If no clear projects found, extract any technical experience as projects
        
        Document:
        {text[:3000]}
        """
        
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
        
        analyzed = json.loads(raw)
        return analyzed, None
    
    except json.JSONDecodeError:
        return None, "Failed to analyze document. Try again."
    except Exception as e:
        return None, f"Error analyzing document: {str(e)}"