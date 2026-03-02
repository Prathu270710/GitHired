# 🚀 GitHired — AI-Powered Resume & Job Description Matcher

GitHired is an LLM-powered ATS resume scorer. Paste any job description, upload your resume, and instantly see your real ATS match score, the same way Taleo, Workday, and Greenhouse actually scan it. No sugarcoating. 
Just your exact score, what keywords are missing, and precisely what to change to get past the filter.

---

## What It Does

- **ATS Reality Score** — pure exact keyword matching, the same way Taleo, Workday, and Greenhouse actually evaluate your resume. No sugarcoating.
- **True Match Score** — LLM-powered semantic analysis of what you actually know based on your experience and projects.
- **Optimization Gap** — the difference between the two scores tells you exactly how many points you're losing purely because of wording, not skills.
- **GitHub Analyzer** — connects to your GitHub, reads your READMEs, and recommends which projects to highlight or remove for a specific role.
- **Project Document Upload** — no GitHub? Upload a PDF or DOCX of your portfolio instead.
- **Gap Analysis** — identifies missing required skills and nice-to-haves with exact phrases the ATS is scanning for.
- **Cover Letter Generator** — generates a human-sounding, role-specific cover letter outline that won't get flagged as AI-written.
- **Resume Improvements** — 5 specific, actionable changes to boost your ATS score immediately.

---

## Tech Stack

- **Python** — core backend
- **Streamlit** — frontend UI
- **Groq API (Llama 3.1)** — LLM inference, fast and free
- **GitHub API** — repository and README analysis
- **PyPDF2 / python-docx** — resume and document parsing

---

## Run Locally

```bash
git clone https://github.com/Prathu270710/githired.git
cd githired
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root:

```
GROQ_API_KEY=your_groq_key_here
GITHUB_TOKEN=your_github_token_here
```

Run the app:

```bash
streamlit run app.py
```

---

## Get Your Free API Keys

- **Groq API Key** — [console.groq.com](https://console.groq.com) — free tier, no credit card
- **GitHub Token** — GitHub Settings → Developer Settings → Personal Access Tokens → check `public_repo`

---

## Built By

**Prathamesh Parab**
M.S in Computer Science — Syracuse University
Syracuse, New York

- Email: prparab@syr.edu
- LinkedIn: [linkedin.com/in/prathameshparab27](https://www.linkedin.com/in/prathameshparab27/)
- GitHub: [github.com/Prathu270710](https://github.com/Prathu270710)

---

*Open to SDE roles — feel free to reach out.*