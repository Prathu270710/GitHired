import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

from modules.resume_parser import parse_resume
from modules.jd_parser import parse_job_description
from modules.github_analyzer import get_analyzed_github_projects, analyze_projects_from_document
from modules.matcher import run_full_match
from modules.cover_letter import generate_cover_letter, generate_resume_suggestions

load_dotenv()

# Page config
st.set_page_config(
    page_title="GitHired",
    page_icon="🚀",
    layout="wide"
)

# Title
st.title("🚀 GitHired")
st.subheader("Match your resume to any job description using your GitHub projects")
st.divider()

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📄 Upload Your Resume")
    resume_file = st.file_uploader(
        "Upload PDF or DOCX",
        type=["pdf", "docx"]
    )

with col2:
    st.markdown("### 💼 Job Description")
    jd_text = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="Paste the full job description..."
    )

st.markdown("### 🐙 Projects Source")
source_option = st.radio(
    "How would you like to provide your projects?",
    ["GitHub Username", "Upload Project Document"],
    horizontal=True
)

github_username = ""
project_document = None

if source_option == "GitHub Username":
    github_username = st.text_input(
        "Enter your GitHub username",
        placeholder="e.g. torvalds"
    )
else:
    st.info("Upload a PDF or DOCX file listing your projects, portfolio, or any document describing your work.")
    project_document = st.file_uploader(
        "Upload Project Document",
        type=["pdf", "docx"],
        key="project_doc"
    )

st.divider()

# Analyze Button
analyze_button = st.button(
    "🔍 Analyze My Profile",
    type="primary",
    use_container_width=True
)

if analyze_button:

    # Validate inputs
    if not resume_file:
        st.error("Please upload your resume")
        st.stop()

    if not jd_text.strip():
        st.error("Please paste a job description")
        st.stop()

    if source_option == "GitHub Username" and not github_username.strip():
        st.error("Please enter your GitHub username")
        st.stop()

    if source_option == "Upload Project Document" and not project_document:
        st.error("Please upload your project document")
        st.stop()

    # Save uploaded resume temporarily
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(resume_file.name)[1]
    ) as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name

    try:
        # Step 1 - Parse Resume
        with st.spinner("📄 Reading your resume..."):
            resume_text, error = parse_resume(tmp_path)
            if error:
                st.error(error)
                st.stop()

        # Step 2 - Parse Job Description
        with st.spinner("💼 Analyzing job description..."):
            jd_analysis, error = parse_job_description(jd_text)
            if error:
                st.error(error)
                st.stop()

        # Step 3 - Analyze Projects
        if source_option == "GitHub Username":
            with st.spinner("🐙 Scanning your GitHub projects..."):
                github_projects, error = get_analyzed_github_projects(github_username)
                if error:
                    st.error(error)
                    st.stop()
        else:
            with st.spinner("📂 Analyzing your project document..."):
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=os.path.splitext(project_document.name)[1]
                ) as tmp_proj:
                    tmp_proj.write(project_document.read())
                    tmp_proj_path = tmp_proj.name

                github_projects, error = analyze_projects_from_document(tmp_proj_path)
                os.unlink(tmp_proj_path)

                if error:
                    st.error(error)
                    st.stop()

        # Step 4 - Run Matching
        with st.spinner("🔍 Running analysis..."):
            match_results = run_full_match(
                resume_text,
                jd_analysis,
                github_projects
            )

        # Step 5 - Generate Cover Letter
        with st.spinner("✍️ Writing cover letter..."):
            cover_letter, error = generate_cover_letter(
                resume_text,
                jd_analysis,
                match_results
            )

        # Step 6 - Generate Resume Suggestions
        with st.spinner("💡 Generating resume improvements..."):
            suggestions, error = generate_resume_suggestions(
                resume_text,
                jd_analysis,
                match_results
            )

        st.success("✅ Analysis Complete!")
        st.divider()

        # ── RESULTS SECTION ──

        # Dual ATS Score
        st.markdown("## 🎯 ATS Score")
        ats = match_results["ats_score"]
        ats_reality = ats["ats_reality_score"]
        true_match = ats["true_match_score"]
        gap = ats["optimization_gap"]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🤖 ATS Reality Score")
            st.caption("What Taleo / Workday / Greenhouse actually gives you — exact keyword matching only")
            if ats_reality >= 70:
                st.success(f"## {ats_reality}%")
            elif ats_reality >= 50:
                st.warning(f"## {ats_reality}%")
            else:
                st.error(f"## {ats_reality}%")

        with col2:
            st.markdown("### 🧠 True Match Score")
            st.caption("What you actually know based on experience and projects")
            if true_match >= 70:
                st.success(f"## {true_match}%")
            elif true_match >= 50:
                st.warning(f"## {true_match}%")
            else:
                st.error(f"## {true_match}%")

        # Optimization gap message
        if gap > 15:
            st.warning(
                f"⚠️ **{gap} point gap detected** — You have the skills but your resume "
                f"wording is losing you {gap} points with real ATS systems. "
                f"Fix the missing keywords below to close this gap."
            )
        elif gap > 0:
            st.info(
                f"ℹ️ **{gap} point gap** — Minor wording improvements "
                f"could boost your ATS score by {gap} points."
            )
        else:
            st.success("✅ Your resume wording matches your actual skills perfectly!")

        st.divider()

        # Score Breakdown Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Required Skills",
                f"{ats['matched_required_skills']}/{ats['total_required_skills']}"
            )
        with col2:
            st.metric(
                "ATS Keywords",
                f"{ats['matched_keywords']}/{ats['total_keywords']}"
            )
        with col3:
            st.metric(
                "Tech Stack",
                f"{ats['matched_tech']}/{ats['total_tech']}"
            )

        # ATS Reality Keyword Breakdown
        st.markdown("### 🔍 ATS Reality Keyword Breakdown")
        st.caption("Based on exact string matching — what real ATS systems actually find")

        tab1, tab2, tab3 = st.tabs(["Required Skills", "ATS Keywords", "Tech Stack"])

        with tab1:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Found in Resume (ATS sees these)**")
                matched = ats.get("matched_required_list", [])
                if matched:
                    for item in matched:
                        st.success(f"✅ {item}")
                else:
                    st.info("None found")
            with col2:
                st.markdown("**❌ Missing from Resume (ATS won't find these)**")
                missing = ats.get("missing_required_list", [])
                if missing:
                    for item in missing:
                        st.error(f"❌ {item}")
                else:
                    st.success("All present!")

        with tab2:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Found in Resume (ATS sees these)**")
                matched = ats.get("matched_keywords_list", [])
                if matched:
                    for item in matched:
                        st.success(f"✅ {item}")
                else:
                    st.info("None found")
            with col2:
                st.markdown("**❌ Missing from Resume (ATS won't find these)**")
                missing = ats.get("missing_keywords_list", [])
                if missing:
                    for item in missing:
                        st.error(f"❌ {item}")
                else:
                    st.success("All present!")

        with tab3:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Found in Resume (ATS sees these)**")
                matched = ats.get("matched_tech_list", [])
                if matched:
                    for item in matched:
                        st.success(f"✅ {item}")
                else:
                    st.info("None found")
            with col2:
                st.markdown("**❌ Missing from Resume (ATS won't find these)**")
                missing = ats.get("missing_tech_list", [])
                if missing:
                    for item in missing:
                        st.error(f"❌ {item}")
                else:
                    st.success("All present!")

        # True Match Breakdown
        st.markdown("### 🧠 True Match Breakdown")
        st.caption("Based on semantic understanding — what you actually know")

        tab4, tab5, tab6 = st.tabs(["Required Skills", "ATS Keywords", "Tech Stack"])

        with tab4:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ You Actually Have These**")
                matched = ats.get("truly_matched_required", [])
                if matched:
                    for item in matched:
                        st.success(f"✅ {item}")
                else:
                    st.info("None matched")
            with col2:
                st.markdown("**❌ You Actually Lack These**")
                missing = ats.get("truly_missing_required", [])
                if missing:
                    for item in missing:
                        st.error(f"❌ {item}")
                else:
                    st.success("All covered!")

        with tab5:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ You Actually Have These**")
                matched = ats.get("truly_matched_keywords", [])
                if matched:
                    for item in matched:
                        st.success(f"✅ {item}")
                else:
                    st.info("None matched")
            with col2:
                st.markdown("**❌ You Actually Lack These**")
                missing = ats.get("truly_missing_keywords", [])
                if missing:
                    for item in missing:
                        st.error(f"❌ {item}")
                else:
                    st.success("All covered!")

        with tab6:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ You Actually Have These**")
                matched = ats.get("truly_matched_tech", [])
                if matched:
                    for item in matched:
                        st.success(f"✅ {item}")
                else:
                    st.info("None matched")
            with col2:
                st.markdown("**❌ You Actually Lack These**")
                missing = ats.get("truly_missing_tech", [])
                if missing:
                    for item in missing:
                        st.error(f"❌ {item}")
                else:
                    st.success("All covered!")

        st.divider()

        # Skill Gaps
        st.markdown("## ❌ Skill Gaps")
        st.caption("Based on ATS Reality — exact phrases missing from your resume")
        gaps = match_results["gaps"]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Missing Required Skills**")
            if gaps["missing_required"]:
                for skill in gaps["missing_required"]:
                    st.error(f"❌ {skill}")
            else:
                st.success("✅ No missing required skills!")

        with col2:
            st.markdown("**Missing Nice to Have**")
            if gaps["missing_nice_to_have"]:
                for skill in gaps["missing_nice_to_have"]:
                    st.warning(f"⚠️ {skill}")
            else:
                st.success("✅ All nice to have skills covered!")

        st.divider()

        # Project Recommendations
        st.markdown("## 🐙 Project Recommendations")
        github_recs = match_results["github_recommendations"]

        if github_recs:
            st.markdown("**Add these projects to your resume:**")
            for rec in github_recs:
                with st.expander(
                    f"✅ {rec['project_name']} — Impact: {rec.get('impact', 'high').upper()}"
                ):
                    st.markdown(f"**Fills gap for:** {', '.join(rec.get('fills_gap_for', []))}")
                    st.markdown(f"**Why:** {rec.get('reason', '')}")
        else:
            st.info("Your current projects already cover the job requirements well!")

        st.divider()

        # Weak Projects
        st.markdown("## 🗑️ Projects to Remove")
        weak_projects = match_results["weak_projects"]

        if weak_projects:
            st.markdown("**Remove or de-emphasize these from your resume:**")
            for proj in weak_projects:
                with st.expander(f"❌ {proj['project_name']}"):
                    st.markdown(f"**Why:** {proj.get('reason', '')}")
                    st.markdown(f"**Suggestion:** {proj.get('suggestion', '')}")
        else:
            st.success("All your projects are relevant for this role!")

        st.divider()

        # Resume Suggestions
        st.markdown("## 💡 Resume Improvements")
        if suggestions:
            st.markdown(suggestions)

        st.divider()

        # Cover Letter
        st.markdown("## ✍️ Cover Letter")
        st.info(
            "This is a starting point. Use the personalization notes "
            "at the bottom to make it uniquely yours before sending."
        )
        if cover_letter:
            st.markdown(cover_letter)

    finally:
        os.unlink(tmp_path)

# ── ABOUT ME (always visible at bottom, outside the analyze block) ──
st.divider()
with st.expander("About Me"):
    st.markdown("**Prathamesh Parab**")
    st.markdown("M.S in Computer Science")
    st.markdown("Syracuse University")
    st.markdown("Syracuse, New York")
    st.markdown("prparab@syr.edu")
    st.markdown("")
    st.markdown(
        "[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin)]"
        "(https://www.linkedin.com/in/prathameshparab27/)"
        "  "
        "[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?logo=github)]"
        "(https://github.com/Prathu270710)"
    )
    st.markdown("")
    st.markdown("---")
    st.markdown("**Motivation**")
    st.markdown(
        "As a new grad navigating hundreds of job applications, I wanted a tool "
        "that gives honest feedback and actually helps optimize a resume the way "
        "real ATS systems evaluate it. Most tools sugarcoat your score — GitHired "
        "shows you the brutal truth and tells you exactly what to fix."
    )
    st.markdown("")
    st.markdown("Built by Prathamesh Parab — Open to SDE roles")