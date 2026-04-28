"""
CareerPrep Job-Hunting Agent — Streamlit Dashboard
====================================================
A polished 6-tab web dashboard that provides a visual interface to run
the agent and explore all reports with charts and download buttons.
"""

import os
import csv
import json
from datetime import datetime, date

import streamlit as st

# ── Page config ────────────────────────────────────────────────
st.set_page_config(
    page_title="CareerPrep Agent",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main { background: #0d1117; }

.hero-card {
    background: linear-gradient(135deg, #1a1f2e 0%, #0f3460 50%, #16213e 100%);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99, 179, 237, 0.2);
    box-shadow: 0 4px 30px rgba(0,0,0,0.4);
}

.metric-card {
    background: linear-gradient(135deg, #1a1f2e, #0d1117);
    border-radius: 12px;
    padding: 1.2rem;
    border: 1px solid rgba(99,179,237,0.15);
    text-align: center;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-3px); }

.skill-chip-green {
    display: inline-block;
    background: rgba(72,187,120,0.15);
    color: #68D391;
    border: 1px solid rgba(72,187,120,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.82rem;
    font-weight: 500;
}

.skill-chip-red {
    display: inline-block;
    background: rgba(245,101,101,0.15);
    color: #FC8181;
    border: 1px solid rgba(245,101,101,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    margin: 3px;
    font-size: 0.82rem;
    font-weight: 500;
}

.reminder-overdue  { background: rgba(245,101,101,0.1); border-left: 4px solid #FC8181; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin: 6px 0; }
.reminder-today    { background: rgba(237,137,54,0.1);  border-left: 4px solid #ED8936; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin: 6px 0; }
.reminder-tomorrow { background: rgba(236,201,75,0.1);  border-left: 4px solid #ECC94B; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin: 6px 0; }
.reminder-week     { background: rgba(99,179,237,0.1);  border-left: 4px solid #63B3ED; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin: 6px 0; }
.reminder-upcoming { background: rgba(72,187,120,0.1);  border-left: 4px solid #68D391; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin: 6px 0; }

.section-header {
    font-size: 1.1rem; font-weight: 600;
    color: #63B3ED; margin: 1rem 0 0.5rem 0;
    border-bottom: 1px solid rgba(99,179,237,0.2);
    padding-bottom: 4px;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────
JOB_DIR      = "input_jobs"
RESUME_DIR   = "input_resumes"
KB_DIR       = "input_kb"
OUTPUT_DIR   = "outputs"
TRACKER_DIR  = "tracker"
TRACKER_FILE = os.path.join(TRACKER_DIR, "applications.csv")
MEMORY_FILE  = os.path.join(TRACKER_DIR, "memory.json")
TODAY        = date.today()

# ── Helper functions ───────────────────────────────────────────

def read_output(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_tracker():
    rows = []
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(dict(row))
    return rows


def _parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _urgency_label(target_date):
    if target_date is None:
        return "upcoming", "🟢"
    delta = (target_date - TODAY).days
    if delta < 0:    return "overdue",  "🔴"
    elif delta == 0: return "today",    "🟠"
    elif delta == 1: return "tomorrow", "🟡"
    elif delta <= 7: return "week",     "🔵"
    else:            return "upcoming", "🟢"


def agent_ran():
    return os.path.exists(os.path.join(OUTPUT_DIR, "final_agent_report.txt"))


# ── Sidebar ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 CareerPrep Agent")
    st.markdown("---")

    # Run agent button
    if st.button("▶  Run Agent Now", use_container_width=True, type="primary"):
        with st.spinner("Agent running..."):
            try:
                import subprocess, sys
                result = subprocess.run(
                    [sys.executable, "app.py"],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    st.success("✅ Agent completed!")
                    st.code(result.stdout, language="text")
                else:
                    st.error("Agent error:")
                    st.code(result.stderr, language="text")
            except Exception as e:
                st.error(f"Failed to run agent: {e}")

    st.markdown("---")

    mem = load_memory()
    if mem:
        st.markdown("**Last Run**")
        st.caption(mem.get("last_run", "N/A")[:19])
        st.markdown(f"**Match Score:** `{mem.get('match_score', 0)}%`")
        st.markdown(f"**Resume Quality:** `{mem.get('resume_quality_score', 0)}/100`")
        st.markdown("---")

    # Input folder status
    st.markdown("**Input Folders**")
    for label, d in [("Jobs", JOB_DIR), ("Resumes", RESUME_DIR), ("KB", KB_DIR)]:
        if os.path.isdir(d):
            files = [f for f in os.listdir(d) if f.endswith((".txt", ".pdf"))]
            color = "🟢" if files else "🔴"
            st.markdown(f"{color} `{label}` — {len(files)} file(s)")
        else:
            st.markdown(f"🔴 `{label}` — folder missing")

    st.markdown("---")
    st.caption("CareerPrep Job-Hunting Agent\nBuilt with 🐍 Python + Streamlit")


# ── Main header ────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <h1 style="margin:0; font-size:2rem; background: linear-gradient(90deg,#63B3ED,#68D391);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        🎯 CareerPrep Job-Hunting Agent
    </h1>
    <p style="margin:0.5rem 0 0 0; color:#a0aec0; font-size:1rem;">
        Your AI-powered career companion — job analysis, skill gaps, resume tailoring,
        interview prep, application tracking, and smart reminders.
    </p>
</div>
""", unsafe_allow_html=True)

# ── If agent hasn't run yet ────────────────────────────────────
if not agent_ran():
    st.info("👆 Click **▶ Run Agent Now** in the sidebar to generate all reports, then explore the tabs below.")

# ── Tabs ───────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Overview",
    "🔍 Job Analysis",
    "⚡ Skill Gap",
    "📝 Resume",
    "🎤 Interview Prep",
    "📋 Tracker",
    "⏰ Reminders",
])


# ─────────────────────────────────────────────
# TAB 0 — OVERVIEW
# ─────────────────────────────────────────────
with tabs[0]:
    mem = load_memory()
    tracker_rows = load_tracker()

    col1, col2, col3, col4 = st.columns(4)

    match_score    = mem.get("match_score", 0)
    quality_score  = mem.get("resume_quality_score", 0)
    total_apps     = len(tracker_rows)
    interviews_sched = sum(1 for r in tracker_rows if r.get("status", "").lower() == "interview scheduled")

    with col1:
        st.metric("🎯 Match Score",    f"{match_score}%")
    with col2:
        st.metric("📄 Resume Quality", f"{quality_score}/100")
    with col3:
        st.metric("📋 Applications",   total_apps)
    with col4:
        st.metric("🗓 Interviews",      interviews_sched)

    st.divider()

    if mem:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-header">✅ Matched Skills</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="skill-chip-green">{s}</span>' for s in mem.get("matched_skills", []))
            st.markdown(chips or "_Run the agent to see matched skills._", unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-header">❌ Missing Skills</div>', unsafe_allow_html=True)
            chips = "".join(f'<span class="skill-chip-red">{s}</span>' for s in mem.get("missing_skills", []))
            st.markdown(chips or "_Run the agent to see skill gaps._", unsafe_allow_html=True)

    # Status counts chart
    if tracker_rows:
        st.divider()
        st.markdown('<div class="section-header">📊 Application Status Breakdown</div>', unsafe_allow_html=True)
        status_counts = {}
        for row in tracker_rows:
            s = row.get("status", "Unknown")
            status_counts[s] = status_counts.get(s, 0) + 1

        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use("Agg")

            fig, ax = plt.subplots(figsize=(8, 3), facecolor="#0d1117")
            ax.set_facecolor("#1a1f2e")
            labels = list(status_counts.keys())
            values = list(status_counts.values())
            colors = ["#63B3ED", "#68D391", "#ECC94B", "#FC8181", "#9F7AEA", "#ED8936"]
            bars   = ax.barh(labels, values, color=colors[:len(labels)], height=0.5)
            ax.set_xlabel("Count", color="#a0aec0")
            ax.tick_params(colors="#a0aec0")
            for spine in ax.spines.values():
                spine.set_edgecolor("#2d3748")
            ax.bar_label(bars, color="#e2e8f0", padding=4)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        except ImportError:
            for label, count in status_counts.items():
                st.markdown(f"**{label}**: {count}")


# ─────────────────────────────────────────────
# TAB 1 — JOB ANALYSIS
# ─────────────────────────────────────────────
with tabs[1]:
    st.subheader("🔍 Job Analysis Report")
    content = read_output("job_analysis_report.txt")
    if content:
        st.download_button("⬇ Download Report", content, "job_analysis_report.txt", use_container_width=True)
        st.code(content, language="text")
    else:
        st.info("Run the agent to generate this report.")

    # Show raw job files
    with st.expander("📁 Raw Job Poster Files"):
        if os.path.isdir(JOB_DIR):
            for fname in sorted(os.listdir(JOB_DIR)):
                if fname.endswith(".txt"):
                    fpath = os.path.join(JOB_DIR, fname)
                    with open(fpath, "r", encoding="utf-8") as f:
                        st.markdown(f"**{fname}**")
                        st.text(f.read())
                        st.divider()


# ─────────────────────────────────────────────
# TAB 2 — SKILL GAP
# ─────────────────────────────────────────────
with tabs[2]:
    st.subheader("⚡ Skill Gap Analysis")
    mem = load_memory()

    if mem:
        score = mem.get("match_score", 0)
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.markdown("**Overall Match Score**")
            st.progress(score / 100)
            st.markdown(f"### {score}% Match")

        with col_r:
            quality = mem.get("resume_quality_score", 0)
            st.markdown("**Resume Quality**")
            st.progress(quality / 100)
            st.markdown(f"### {quality}/100")

        st.divider()

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ✅ Matched Skills")
            for s in mem.get("matched_skills", []):
                st.markdown(f'<span class="skill-chip-green">{s}</span>', unsafe_allow_html=True)

        with col_b:
            st.markdown("#### ❌ Skills to Acquire")
            for s in mem.get("missing_skills", []):
                st.markdown(f'<span class="skill-chip-red">{s}</span>', unsafe_allow_html=True)

        st.divider()

        # Skill gap bar chart
        try:
            import matplotlib.pyplot as plt, matplotlib
            matplotlib.use("Agg")

            categories = ["Job Skills", "Resume Skills", "Matched", "Missing"]
            values     = [
                len(mem.get("job_skills", [])),
                len(mem.get("resume_skills", [])),
                len(mem.get("matched_skills", [])),
                len(mem.get("missing_skills", [])),
            ]
            palette = ["#63B3ED", "#9F7AEA", "#68D391", "#FC8181"]
            fig, ax = plt.subplots(figsize=(8, 3), facecolor="#0d1117")
            ax.set_facecolor("#1a1f2e")
            bars = ax.bar(categories, values, color=palette)
            ax.tick_params(colors="#a0aec0")
            ax.bar_label(bars, color="#e2e8f0", padding=4)
            for spine in ax.spines.values():
                spine.set_edgecolor("#2d3748")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        except ImportError:
            pass

    content = read_output("skill_gap_report.txt")
    if content:
        st.download_button("⬇ Download Skill Gap Report", content, "skill_gap_report.txt", use_container_width=True)
        with st.expander("📄 Full Report Text"):
            st.code(content, language="text")
    else:
        st.info("Run the agent to generate this report.")


# ─────────────────────────────────────────────
# TAB 3 — RESUME
# ─────────────────────────────────────────────
with tabs[3]:
    st.subheader("📝 Resume Suggestions & Cover Letter")
    tab3a, tab3b, tab3c = st.tabs(["✏ Resume Suggestions", "📨 Cover Letter", "💬 LinkedIn Message"])

    with tab3a:
        content = read_output("tailored_resume_suggestions.txt")
        if content:
            st.download_button("⬇ Download", content, "tailored_resume_suggestions.txt", use_container_width=True)
            st.code(content, language="text")
        else:
            st.info("Run the agent to generate resume suggestions.")

    with tab3b:
        content = read_output("cover_letter.txt")
        if content:
            st.download_button("⬇ Download Cover Letter", content, "cover_letter.txt", use_container_width=True)
            st.code(content, language="text")
        else:
            st.info("Run the agent to generate a cover letter.")

    with tab3c:
        content = read_output("linkedin_message.txt")
        if content:
            st.download_button("⬇ Download LinkedIn Message", content, "linkedin_message.txt", use_container_width=True)
            st.code(content, language="text")
        else:
            st.info("Run the agent to generate a LinkedIn message.")


# ─────────────────────────────────────────────
# TAB 4 — INTERVIEW PREP
# ─────────────────────────────────────────────
with tabs[4]:
    st.subheader("🎤 Interview Preparation Questions")
    content = read_output("interview_questions.txt")
    if content:
        st.download_button("⬇ Download Questions", content, "interview_questions.txt", use_container_width=True)

        # Filter by skill
        mem = load_memory()
        skills = mem.get("job_skills", [])
        if skills:
            selected = st.selectbox("Filter questions by skill:", ["All"] + skills)
            if selected != "All":
                filtered = [
                    line for line in content.splitlines()
                    if selected.lower() in line.lower() or not line.startswith("  Q:")
                ]
                content = "\n".join(filtered)

        st.code(content, language="text")
    else:
        st.info("Run the agent to generate interview questions.")


# ─────────────────────────────────────────────
# TAB 5 — TRACKER
# ─────────────────────────────────────────────
with tabs[5]:
    st.subheader("📋 Application Tracker")
    rows = load_tracker()

    if rows:
        # Status filter
        all_statuses = sorted(set(r.get("status", "") for r in rows))
        filt = st.multiselect("Filter by Status:", all_statuses, default=all_statuses)
        filtered = [r for r in rows if r.get("status", "") in filt]

        # Status badges
        status_emoji = {
            "Not Applied":         "⬜",
            "Applied":             "📤",
            "Shortlisted":         "🔶",
            "Interview Scheduled": "📅",
            "Offered":             "🎉",
            "Rejected":            "❌",
        }

        # Summary counts
        col_counts = st.columns(len(all_statuses))
        for i, stat in enumerate(all_statuses):
            cnt = sum(1 for r in rows if r.get("status") == stat)
            col_counts[i].metric(f"{status_emoji.get(stat, '⚪')} {stat}", cnt)

        st.divider()

        # Table
        try:
            import pandas as pd
            df = pd.DataFrame(filtered)
            df["status"] = df["status"].apply(lambda s: f"{status_emoji.get(s,'⚪')} {s}")
            st.dataframe(df, use_container_width=True, hide_index=True)
        except ImportError:
            for row in filtered:
                st.markdown(
                    f"**{row.get('application_id')}** | "
                    f"{status_emoji.get(row.get('status',''),'')} {row.get('status')} | "
                    f"{row.get('company')} — {row.get('role')}"
                )

        # Download tracker CSV
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            csv_data = f.read()
        st.download_button("⬇ Download applications.csv", csv_data, "applications.csv", "text/csv", use_container_width=True)

    else:
        st.info("Run the agent to populate the application tracker.")


# ─────────────────────────────────────────────
# TAB 6 — REMINDERS
# ─────────────────────────────────────────────
with tabs[6]:
    st.subheader(f"⏰ Smart Reminders — {TODAY.strftime('%B %d, %Y')}")
    rows = load_tracker()

    urgency_css = {
        "overdue":  "reminder-overdue",
        "today":    "reminder-today",
        "tomorrow": "reminder-tomorrow",
        "week":     "reminder-week",
        "upcoming": "reminder-upcoming",
    }
    urgency_label = {
        "overdue":  "🔴 OVERDUE",
        "today":    "🟠 TODAY",
        "tomorrow": "🟡 TOMORROW",
        "week":     "🔵 THIS WEEK",
        "upcoming": "🟢 UPCOMING",
    }

    if rows:
        buckets: dict = {"overdue": [], "today": [], "tomorrow": [], "week": [], "upcoming": []}

        for row in rows:
            app_id      = row.get("application_id", "")
            company     = row.get("company", "")
            role        = row.get("role", "")
            status      = row.get("status", "").strip()
            interview_dt = _parse_date(row.get("interview_date", ""))
            followup_dt  = _parse_date(row.get("follow_up_date", ""))
            next_action  = row.get("next_action", "")

            if status.lower() == "interview scheduled" and interview_dt:
                urg, _ = _urgency_label(interview_dt)
                buckets[urg].append({
                    "title": f"[{app_id}] Interview — {company}",
                    "body":  f"Role: **{role}** | Date: `{interview_dt}` | Action: {next_action}",
                })
            elif status.lower() == "not applied":
                urg, _ = _urgency_label(followup_dt) if followup_dt else ("upcoming", "🟢")
                buckets[urg].append({
                    "title": f"[{app_id}] Not Applied — {company}",
                    "body":  f"Role: **{role}** | Action: Tailor resume and apply ASAP.",
                })
            elif status.lower() == "applied":
                urg, _ = _urgency_label(followup_dt) if followup_dt else ("upcoming", "🟢")
                buckets[urg].append({
                    "title": f"[{app_id}] Follow Up — {company}",
                    "body":  f"Role: **{role}** | Follow up by: `{followup_dt or 'N/A'}` | {next_action}",
                })
            elif status.lower() == "shortlisted":
                buckets["week"].append({
                    "title": f"[{app_id}] Shortlisted — {company}",
                    "body":  f"Role: **{role}** | Prepare for technical test. {next_action}",
                })

        for urg_key in ["overdue", "today", "tomorrow", "week", "upcoming"]:
            items = buckets[urg_key]
            if items:
                st.markdown(f"#### {urgency_label[urg_key]}")
                for item in items:
                    css = urgency_css[urg_key]
                    st.markdown(
                        f'<div class="{css}"><strong>{item["title"]}</strong><br>{item["body"]}</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown("")

        # Download reminders
        reminder_content = read_output("../tracker/reminders.txt") or ""
        reminder_path = os.path.join(TRACKER_DIR, "reminders.txt")
        if os.path.exists(reminder_path):
            with open(reminder_path, "r", encoding="utf-8") as f:
                reminder_content = f.read()
            st.download_button("⬇ Download reminders.txt", reminder_content, "reminders.txt", use_container_width=True)

    else:
        st.info("Run the agent to generate reminders.")
