# 🚀 GitHired — AI-Powered Resume & Job Description Matcher

GitHired is an LLM-powered ATS resume scorer. Paste any job description, upload your resume, and instantly see your real ATS match score — the same way Taleo, Workday, and Greenhouse actually scan it. No sugarcoating. Just your exact score, what keywords are missing, and precisely what to change to get past the filter.

---

## What It Does

- **ATS Reality Score** — pure exact keyword matching like Taleo, Workday, Greenhouse
- **True Match Score** — LLM-powered semantic analysis of your actual skills
- **Optimization Gap** — exact points you are losing because of wording not skills
- **GitHub Analyzer** — scans your repos and recommends which projects to highlight
- **Project Document Upload** — no GitHub? Upload a PDF or DOCX portfolio instead
- **Gap Analysis** — exact phrases the ATS is scanning for that you are missing
- **Cover Letter Generator** — human-sounding, role-specific, not flagged as AI
- **Resume Improvements** — 5 specific actionable changes to boost your score

---

## Tech Stack

- **Python** — core backend
- **Streamlit** — frontend UI
- **Groq API (Llama 3.1)** — LLM inference, fast and free
- **GitHub API** — repository and README analysis
- **PyPDF2 / python-docx** — resume and document parsing

---

## Live Demo

[huggingface.co/spaces/prparab2707/GitHired](https://huggingface.co/spaces/prparab2707/GitHired)

---

## Run Locally
```bash
git clone https://github.com/Prathu270710/GitHired.git
cd GitHired
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

GROQ_API_KEY=your_groq_key_here
GITHUB_TOKEN=your_github_token_here

Run:
```bash
streamlit run app.py
```

---

## Get Your Free API Keys

- **Groq API Key** — [console.groq.com](https://console.groq.com)
- **GitHub Token** — GitHub Settings → Developer Settings → Personal Access Tokens → check `public_repo`

---

## Built By

**Prathamesh Parab**
M.S in Computer Science — Syracuse University, Syracuse New York

- Email: prparab@syr.edu
- LinkedIn: [linkedin.com/in/prathameshparab27](https://www.linkedin.com/in/prathameshparab27/)
- GitHub: [github.com/Prathu270710](https://github.com/Prathu270710)

---

*Open to SDE roles — feel free to reach out.*