"""
dashboard.py
------------
Streamlit Dashboard for Automated Resume Screening Tool
Run: streamlit run dashboard.py
"""

import os
import sys
import json
import tempfile
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ─── Path setup ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from text_extractor   import extract_text, load_all_resumes
from text_cleaner     import clean_text, extract_candidate_name, extract_email
from scorer           import score_resume
from report_generator import generate_csv_report, generate_json_report, generate_summary_stats

DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
JD_FILE    = os.path.join(DATA_DIR, "job_descriptions.json")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Screening Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }

    .main { background: #0a0e1a; }
    .stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0f1628 50%, #0a0e1a 100%); }

    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a1f35 0%, #141929 100%);
        border: 1px solid #2a3050;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4f6ef7, #7c3aed, #06b6d4);
    }
    .main-header h1 {
        color: #e2e8f0;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p {
        color: #64748b;
        margin: 0.5rem 0 0;
        font-size: 0.95rem;
    }

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1a1f35, #141929);
        border: 1px solid #2a3050;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    .metric-label {
        color: #64748b;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.25rem;
    }

    /* Candidate cards */
    .candidate-card {
        background: #1a1f35;
        border: 1px solid #2a3050;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 0.75rem;
        transition: border-color 0.2s;
    }
    .candidate-card:hover { border-color: #4f6ef7; }

    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-green  { background: #052e16; color: #4ade80; border: 1px solid #166534; }
    .badge-blue   { background: #0c1a3d; color: #60a5fa; border: 1px solid #1e3a8a; }
    .badge-yellow { background: #1c1204; color: #fbbf24; border: 1px solid #92400e; }
    .badge-red    { background: #1c0505; color: #f87171; border: 1px solid #991b1b; }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0d1120 !important;
    }

    /* Section headers */
    .section-title {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 1.5rem 0 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1e2740;
    }

    /* Skill chip */
    .skill-chip {
        display: inline-block;
        background: #0f2240;
        color: #60a5fa;
        border: 1px solid #1e3a8a;
        border-radius: 20px;
        padding: 0.2rem 0.65rem;
        font-size: 0.78rem;
        margin: 0.15rem;
    }
    .skill-chip-missing {
        background: #200a0a;
        color: #f87171;
        border-color: #7f1d1d;
    }

    /* Tables */
    .stDataFrame { border-radius: 12px; overflow: hidden; }

    /* Progress bars */
    .stProgress > div > div { background: linear-gradient(90deg, #4f6ef7, #7c3aed); }

    /* Upload zone */
    .uploadedFile {
        background: #1a1f35 !important;
        border: 1px dashed #2a3050 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_jobs():
    if not os.path.exists(JD_FILE):
        return []
    with open(JD_FILE, "r") as f:
        return json.load(f).get("jobs", [])


def decision_badge(decision: str) -> str:
    if "Strongly" in decision:
        cls = "badge-green"
    elif "Shortlisted" in decision:
        cls = "badge-blue"
    elif "Maybe" in decision:
        cls = "badge-yellow"
    else:
        cls = "badge-red"
    return f'<span class="score-badge {cls}">{decision}</span>'


def score_color(score: float) -> str:
    if score >= 75: return "#4ade80"
    elif score >= 55: return "#60a5fa"
    elif score >= 35: return "#fbbf24"
    else: return "#f87171"


def process_resumes(uploaded_files, job: dict) -> list:
    """Process uploaded files and return scored results."""
    results = []
    jd_text  = job["description"] + " " + " ".join(job["required_skills"])
    jd_clean = clean_text(jd_text)

    for uploaded_file in uploaded_files:
        # Save to temp file
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            raw_text = extract_text(tmp_path)
            if not raw_text.strip():
                continue

            candidate_name = extract_candidate_name(raw_text)
            email          = extract_email(raw_text)
            cleaned_text   = clean_text(raw_text)

            result = score_resume(
                resume_text     = raw_text,
                cleaned_resume  = cleaned_text,
                jd_text         = jd_clean,
                required_skills = job["required_skills"],
                candidate_name  = candidate_name,
                filename        = uploaded_file.name
            )
            result["email"]    = email
            result["raw_text"] = raw_text[:800] + "..." if len(raw_text) > 800 else raw_text
            results.append(result)
        except Exception as e:
            st.warning(f"Error processing {uploaded_file.name}: {e}")
        finally:
            os.unlink(tmp_path)

    return results


def process_sample_resumes(job: dict) -> list:
    """Process resumes from the resumes/ folder."""
    resume_dir = os.path.join(BASE_DIR, "resumes")
    raw_resumes = load_all_resumes(resume_dir)
    if not raw_resumes:
        return []

    results = []
    jd_text  = job["description"] + " " + " ".join(job["required_skills"])
    jd_clean = clean_text(jd_text)

    for filename, raw_text in raw_resumes.items():
        candidate_name = extract_candidate_name(raw_text)
        email          = extract_email(raw_text)
        cleaned_text   = clean_text(raw_text)

        result = score_resume(
            resume_text     = raw_text,
            cleaned_resume  = cleaned_text,
            jd_text         = jd_clean,
            required_skills = job["required_skills"],
            candidate_name  = candidate_name,
            filename        = filename
        )
        result["email"]    = email
        result["raw_text"] = raw_text[:800] + "..." if len(raw_text) > 800 else raw_text
        results.append(result)

    return results


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem;'>
        <div style='font-size:2.5rem;'>🎯</div>
        <div style='color:#e2e8f0; font-weight:700; font-size:1.1rem;'>Resume Screener</div>
        <div style='color:#4f6ef7; font-size:0.8rem;'>AI-Powered ATS System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Job Selection</div>', unsafe_allow_html=True)

    jobs = load_jobs()
    job_options = {f"{j['title']} — {j['company']}": j for j in jobs}
    job_options["+ Custom Job Description"] = None

    selected_job_key = st.selectbox("Select Job", list(job_options.keys()), label_visibility="collapsed")
    selected_job = job_options[selected_job_key]

    # Custom JD input
    if selected_job is None:
        st.markdown('<div class="section-title">Custom Job Description</div>', unsafe_allow_html=True)
        custom_title    = st.text_input("Job Title", "Software Developer")
        custom_company  = st.text_input("Company", "My Company")
        custom_desc     = st.text_area("Job Description", height=150,
                                       placeholder="Paste the full job description here...")
        custom_skills   = st.text_area("Required Skills (one per line)",
                                       "Python\nPandas\nSQL\nMachine Learning\nGit",
                                       height=120)
        if custom_title and custom_desc:
            selected_job = {
                "id": "CUSTOM",
                "title": custom_title,
                "company": custom_company,
                "description": custom_desc,
                "required_skills": [s.strip() for s in custom_skills.split("\n") if s.strip()]
            }

    st.markdown('<div class="section-title">Resume Source</div>', unsafe_allow_html=True)
    source = st.radio("", ["📁 Use Sample Resumes", "📤 Upload Resumes"], label_visibility="collapsed")

    uploaded_files = None
    if "Upload" in source:
        uploaded_files = st.file_uploader(
            "Upload Resumes",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

    st.markdown('<div class="section-title">Shortlist Threshold</div>', unsafe_allow_html=True)
    threshold = st.slider("", 30, 80, 55, label_visibility="collapsed")

    run_btn = st.button("🚀 Run Screening", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("""
    <div style='color:#4a5568; font-size:0.75rem; text-align:center;'>
        Built with Python · Scikit-learn · Streamlit<br>
        <a href='https://github.com' style='color:#4f6ef7;'>GitHub Repo</a>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="main-header">
    <h1>🎯 Automated Resume Screening Tool</h1>
    <p>AI-powered ATS system using TF-IDF vectorization & cosine similarity scoring</p>
</div>
""", unsafe_allow_html=True)

# ── Show selected JD details ──────────────────────────────────────────────────
if selected_job:
    with st.expander("📋 Job Description Details", expanded=False):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{selected_job['title']}** @ *{selected_job['company']}*")
            st.markdown(selected_job.get("description", "")[:400] + "...")
        with col2:
            st.markdown("**Required Skills:**")
            chips = "".join([f'<span class="skill-chip">{s}</span>' for s in selected_job["required_skills"]])
            st.markdown(chips, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# RUN SCREENING
# ─────────────────────────────────────────────────────────────────────────────
if run_btn:
    if not selected_job:
        st.error("Please select or create a job description first.")
        st.stop()

    with st.spinner("Processing resumes..."):
        if "Upload" in source and uploaded_files:
            results = process_resumes(uploaded_files, selected_job)
        else:
            results = process_sample_resumes(selected_job)

    if not results:
        st.warning("No resumes found. Add .txt/.pdf/.docx files to resumes/ folder or upload them.")
        st.stop()

    # Apply threshold override
    for r in results:
        if r["final_score"] >= 75:
            r["decision"] = "Strongly Shortlisted"
        elif r["final_score"] >= threshold:
            r["decision"] = "Shortlisted"
        elif r["final_score"] >= threshold * 0.65:
            r["decision"] = "Maybe (Review Manually)"
        else:
            r["decision"] = "Rejected"

    # Sort by score
    results_sorted = sorted(results, key=lambda x: x["final_score"], reverse=True)
    st.session_state["results"] = results_sorted
    st.session_state["job"]     = selected_job

# ─────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ─────────────────────────────────────────────────────────────────────────────
if "results" in st.session_state:
    results_sorted = st.session_state["results"]
    job            = st.session_state["job"]
    stats          = generate_summary_stats(results_sorted)

    # ── Metric Row ────────────────────────────────────────────────────────────
    st.markdown("---")
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (stats["total"],        "#e2e8f0", "Total Resumes"),
        (stats["shortlisted"],  "#4ade80", "Shortlisted"),
        (stats["maybe"],        "#fbbf24", "Manual Review"),
        (stats["rejected"],     "#f87171", "Rejected"),
        (f"{stats['avg_score']:.1f}", "#60a5fa", "Avg Score"),
    ]
    for col, (val, color, label) in zip([c1, c2, c3, c4, c5], metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color};">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Rankings", "📊 Charts", "🔍 Candidate Detail", "📥 Export"])

    # ─── TAB 1: Rankings ────────────────────────────────────────────────────
    with tab1:
        st.markdown('<div class="section-title">Ranked Candidates</div>', unsafe_allow_html=True)

        for i, r in enumerate(results_sorted, start=1):
            name   = r.get("candidate_name", r["filename"])
            score  = r["final_score"]
            skill  = r["skill_match_pct"]
            tfidf  = r["tfidf_score"]
            dec    = r["decision"]
            email  = r.get("email", "N/A")
            matched = r.get("matched_skills", [])
            missing = r.get("missing_skills", [])

            st.markdown(f"""
            <div class="candidate-card">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                    <div>
                        <span style="color:#94a3b8; font-size:0.85rem; font-family:'JetBrains Mono';">#{i}</span>
                        <span style="color:#e2e8f0; font-size:1.1rem; font-weight:600; margin-left:0.75rem;">{name}</span>
                        <span style="color:#4a5568; font-size:0.8rem; margin-left:0.75rem;">{email}</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:1rem;">
                        <div style="text-align:right;">
                            <div style="font-size:1.8rem; font-weight:700; color:{score_color(score)}; font-family:'JetBrains Mono';">{score:.1f}</div>
                            <div style="color:#4a5568; font-size:0.7rem;">SCORE</div>
                        </div>
                        {decision_badge(dec)}
                    </div>
                </div>
                <div style="margin-top:0.75rem; display:flex; gap:2rem; font-size:0.82rem; color:#64748b;">
                    <span>📊 TF-IDF: <b style="color:#94a3b8">{tfidf:.1f}%</b></span>
                    <span>🎯 Skills: <b style="color:#94a3b8">{skill:.1f}%</b> ({r['matched_count']}/{r['total_skills']})</span>
                    <span>💼 Exp: <b style="color:#94a3b8">{r['experience_score']:.0f}pts</b></span>
                </div>
                <div style="margin-top:0.5rem;">
                    {"".join([f'<span class="skill-chip">{s}</span>' for s in matched[:8]])}
                    {"".join([f'<span class="skill-chip skill-chip-missing">{s}</span>' for s in missing[:4]])}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ─── TAB 2: Charts ──────────────────────────────────────────────────────
    with tab2:
        col_a, col_b = st.columns(2)

        # Bar chart — scores
        with col_a:
            df_chart = pd.DataFrame([{
                "Candidate": r.get("candidate_name", r["filename"])[:15],
                "Score": r["final_score"],
                "Decision": r["decision"]
            } for r in results_sorted])

            color_map = {
                "Strongly Shortlisted": "#4ade80",
                "Shortlisted":          "#60a5fa",
                "Maybe (Review Manually)": "#fbbf24",
                "Rejected":             "#f87171"
            }

            fig = px.bar(
                df_chart, x="Candidate", y="Score", color="Decision",
                color_discrete_map=color_map,
                title="Candidate Score Comparison",
                text="Score"
            )
            fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
            fig.update_layout(
                paper_bgcolor="#1a1f35",
                plot_bgcolor="#141929",
                font=dict(color="#94a3b8"),
                title_font=dict(color="#e2e8f0"),
                showlegend=True,
                legend=dict(bgcolor="#1a1f35", bordercolor="#2a3050")
            )
            fig.update_yaxes(range=[0, 105], gridcolor="#1e2740")
            fig.update_xaxes(tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

        # Pie chart — decision breakdown
        with col_b:
            decision_counts = {}
            for r in results_sorted:
                d = r["decision"]
                decision_counts[d] = decision_counts.get(d, 0) + 1

            fig_pie = go.Figure(data=[go.Pie(
                labels=list(decision_counts.keys()),
                values=list(decision_counts.values()),
                hole=0.5,
                marker_colors=[color_map.get(k, "#666") for k in decision_counts.keys()]
            )])
            fig_pie.update_layout(
                title="Decision Distribution",
                paper_bgcolor="#1a1f35",
                font=dict(color="#94a3b8"),
                title_font=dict(color="#e2e8f0"),
                legend=dict(bgcolor="#1a1f35")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Skill match comparison
        df_skills = pd.DataFrame([{
            "Candidate": r.get("candidate_name", r["filename"])[:15],
            "TF-IDF Score": r["tfidf_score"],
            "Skill Match %": r["skill_match_pct"],
            "Experience": r["experience_score"]
        } for r in results_sorted])

        fig_radar = px.bar(
            df_skills.melt(id_vars="Candidate", var_name="Metric", value_name="Score"),
            x="Candidate", y="Score", color="Metric", barmode="group",
            title="Score Component Breakdown",
            color_discrete_sequence=["#4f6ef7", "#7c3aed", "#06b6d4"]
        )
        fig_radar.update_layout(
            paper_bgcolor="#1a1f35", plot_bgcolor="#141929",
            font=dict(color="#94a3b8"), title_font=dict(color="#e2e8f0"),
            legend=dict(bgcolor="#1a1f35")
        )
        fig_radar.update_yaxes(gridcolor="#1e2740")
        st.plotly_chart(fig_radar, use_container_width=True)

    # ─── TAB 3: Candidate Detail ─────────────────────────────────────────────
    with tab3:
        candidates = [r.get("candidate_name", r["filename"]) for r in results_sorted]
        selected_c = st.selectbox("Select Candidate", candidates)
        r = next((x for x in results_sorted if x.get("candidate_name", x["filename"]) == selected_c), None)

        if r:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom:1rem;">
                    <div class="metric-value" style="color:{score_color(r['final_score'])};">{r['final_score']:.1f}</div>
                    <div class="metric-label">Final Score</div>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"**Decision:** {decision_badge(r['decision'])}", unsafe_allow_html=True)
                st.markdown(f"**Email:** {r.get('email', 'N/A')}")
                st.markdown(f"**File:** `{r['filename']}`")

                st.markdown("---")
                st.markdown("**Score Breakdown:**")
                st.metric("TF-IDF Similarity", f"{r['tfidf_score']:.1f}%")
                st.metric("Skill Match", f"{r['skill_match_pct']:.1f}%")
                st.metric("Experience", f"{r['experience_score']:.0f} pts")

            with col2:
                st.markdown(f"**Matched Skills ({r['matched_count']}/{r['total_skills']}):**")
                chips = "".join([f'<span class="skill-chip">{s}</span>' for s in r.get("matched_skills", [])])
                st.markdown(chips or "*None matched*", unsafe_allow_html=True)

                if r.get("missing_skills"):
                    st.markdown("**Missing Skills:**")
                    chips_m = "".join([f'<span class="skill-chip skill-chip-missing">{s}</span>' for s in r["missing_skills"]])
                    st.markdown(chips_m, unsafe_allow_html=True)

                if r.get("raw_text"):
                    with st.expander("Resume Preview"):
                        st.text(r["raw_text"])

    # ─── TAB 4: Export ───────────────────────────────────────────────────────
    with tab4:
        st.markdown("### Export Results")

        # Prepare DataFrame
        df_export = pd.DataFrame([{
            "Rank":          i + 1,
            "Candidate":     r.get("candidate_name", r["filename"]),
            "Email":         r.get("email", "N/A"),
            "Final Score":   r["final_score"],
            "TF-IDF %":      r["tfidf_score"],
            "Skill Match %": r["skill_match_pct"],
            "Skills Matched": r["matched_count"],
            "Total Skills":   r["total_skills"],
            "Experience Pts": r["experience_score"],
            "Decision":       r["decision"],
            "Matched Skills": ", ".join(r.get("matched_skills", [])),
            "Missing Skills": ", ".join(r.get("missing_skills", []))
        } for i, r in enumerate(results_sorted)])

        st.dataframe(df_export, use_container_width=True)

        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            csv_data = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download CSV Report",
                data=csv_data,
                file_name=f"screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_dl2:
            json_data = json.dumps({
                "job": job["title"],
                "generated": datetime.now().isoformat(),
                "stats": stats,
                "results": results_sorted
            }, indent=2, default=str).encode("utf-8")
            st.download_button(
                "📥 Download JSON Report",
                data=json_data,
                file_name=f"screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="text-align:center; padding: 4rem 2rem; color:#4a5568;">
        <div style="font-size:4rem;">🎯</div>
        <h3 style="color:#64748b; margin:1rem 0 0.5rem;">Ready to Screen</h3>
        <p>Select a job from the sidebar and click <b>Run Screening</b></p>
        <br>
        <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; margin-top:1rem;">
            <div style="background:#1a1f35; border:1px solid #2a3050; border-radius:12px; padding:1.5rem; max-width:200px;">
                <div style="font-size:2rem;">📄</div>
                <div style="color:#94a3b8; font-weight:600; margin:0.5rem 0 0.25rem;">5 Sample Resumes</div>
                <div style="color:#4a5568; font-size:0.8rem;">Pre-loaded for demo</div>
            </div>
            <div style="background:#1a1f35; border:1px solid #2a3050; border-radius:12px; padding:1.5rem; max-width:200px;">
                <div style="font-size:2rem;">🤖</div>
                <div style="color:#94a3b8; font-weight:600; margin:0.5rem 0 0.25rem;">TF-IDF + Cosine</div>
                <div style="color:#4a5568; font-size:0.8rem;">ML-powered scoring</div>
            </div>
            <div style="background:#1a1f35; border:1px solid #2a3050; border-radius:12px; padding:1.5rem; max-width:200px;">
                <div style="font-size:2rem;">📊</div>
                <div style="color:#94a3b8; font-weight:600; margin:0.5rem 0 0.25rem;">3 Job Profiles</div>
                <div style="color:#4a5568; font-size:0.8rem;">Python Dev · ML Eng · Analyst</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
