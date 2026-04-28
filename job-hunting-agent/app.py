"""
JobTrack Agent — Intelligent Job-Hunting Assistant
===================================================
This file-driven agent scans job descriptions, resumes, and study notes
stored in local directories to produce skill-gap analysis, resume improvement
suggestions, customised interview questions, cover letters, urgency-tagged
reminders, and a structured application tracker.

Author : Qasim Zubair  |  Roll: 22F-3100
Contact: qasimzubair166@gmail.com
Design : GAME Framework (Goal · Actions · Memory · Environment)
"""

import os
import csv
import json
from datetime import datetime, date

# ──────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────

JOB_DIR      = "input_jobs"
RESUME_DIR   = "input_resumes"
KB_DIR       = "input_kb"
OUTPUT_DIR   = "outputs"
TRACKER_DIR  = "tracker"

MEMORY_FILE  = os.path.join(TRACKER_DIR, "memory.json")
TRACKER_FILE = os.path.join(TRACKER_DIR, "applications.csv")

TODAY = date.today()

# Comprehensive skill/keyword dictionary
SKILL_KEYWORDS = [
    # Programming & Core
    "python", "c++", "javascript", "java", "typescript",
    "oop", "object-oriented", "design patterns", "data structures", "algorithms",
    # ML / DL
    "machine learning", "deep learning", "scikit-learn", "tensorflow", "pytorch",
    "neural network", "computer vision", "nlp", "natural language processing",
    "data preprocessing", "feature engineering", "model evaluation",
    "pandas", "numpy", "matplotlib", "seaborn",
    # AI / LLM
    "prompt engineering", "llm", "openai", "api", "agentic ai", "langchain",
    # Web & Backend
    "flask", "fastapi", "django", "html", "css", "rest api", "streamlit",
    # Databases
    "sql", "postgresql", "mongodb", "sqlite", "database",
    # DevOps / Tools
    "git", "github", "docker", "jupyter", "vs code", "linux",
    # Soft Skills
    "communication", "problem solving", "teamwork", "leadership",
    "time management", "analytical thinking", "documentation",
]


# ──────────────────────────────────────────────
# ENVIRONMENT HELPERS
# ──────────────────────────────────────────────

def ensure_folders():
    """Create all required project folders if they don't exist."""
    for folder in [JOB_DIR, RESUME_DIR, KB_DIR, OUTPUT_DIR, TRACKER_DIR]:
        os.makedirs(folder, exist_ok=True)


def save_text(path: str, content: str):
    """Write text content to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [SAVED] {path}")


# ──────────────────────────────────────────────
# FILE READERS (TXT + PDF)
# ──────────────────────────────────────────────

def _read_pdf(path: str) -> str:
    """Attempt to extract text from a PDF file."""
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except ImportError:
        return "[PDF reading skipped — install pypdf: pip install pypdf]\n"
    except Exception as e:
        return f"[PDF read error: {e}]\n"


def read_files_from_folder(folder: str) -> tuple[str, int, list[str]]:
    """
    Read all .txt and .pdf files from a folder.
    Returns (combined_text, file_count, filenames).
    """
    combined = ""
    count = 0
    names = []

    if not os.path.isdir(folder):
        return combined, count, names

    for filename in sorted(os.listdir(folder)):
        path = os.path.join(folder, filename)
        fname_lower = filename.lower()

        if fname_lower.endswith(".txt"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                combined += f"\n\n{'='*60}\n FILE: {filename}\n{'='*60}\n{content}"
                count += 1
                names.append(filename)
            except Exception as e:
                combined += f"\n[Error reading {filename}: {e}]\n"

        elif fname_lower.endswith(".pdf"):
            content = _read_pdf(path)
            combined += f"\n\n{'='*60}\n FILE: {filename} (PDF)\n{'='*60}\n{content}"
            count += 1
            names.append(filename)

    return combined, count, names


# ──────────────────────────────────────────────
# SKILL EXTRACTION & MATCHING
# ──────────────────────────────────────────────

def extract_keywords(text: str) -> list[str]:
    """Extract known skill keywords from text (case-insensitive)."""
    text_lower = text.lower()
    found = []
    for kw in SKILL_KEYWORDS:
        if kw in text_lower and kw not in found:
            found.append(kw)
    return found


def compare_skills(job_skills: list[str], resume_skills: list[str]) -> tuple[list, list, float]:
    """Return matched skills, missing skills, and match percentage."""
    matched = [s for s in job_skills if s in resume_skills]
    missing = [s for s in job_skills if s not in resume_skills]
    score = round((len(matched) / len(job_skills)) * 100, 1) if job_skills else 0.0
    return matched, missing, score


def resume_quality_score(resume_text: str, resume_skills: list[str]) -> tuple[int, str]:
    """
    Score the resume out of 100 based on multiple criteria.
    Returns (score, breakdown_text).
    """
    score = 0
    breakdown = []

    # Skills breadth (30 pts)
    skill_pts = min(len(resume_skills) * 2, 30)
    score += skill_pts
    breakdown.append(f"Skills breadth     : {skill_pts}/30 ({len(resume_skills)} skills detected)")

    # Has GitHub mention (10 pts)
    if "github" in resume_text.lower():
        score += 10
        breakdown.append("GitHub presence    : 10/10 ✓")
    else:
        breakdown.append("GitHub presence    :  0/10 — add GitHub link")

    # Has projects section (20 pts)
    if "project" in resume_text.lower():
        score += 20
        breakdown.append("Projects section   : 20/20 ✓")
    else:
        breakdown.append("Projects section   :  0/20 — add project experience")

    # Has education (10 pts)
    if any(w in resume_text.lower() for w in ["university", "degree", "bachelor", "cgpa", "gpa"]):
        score += 10
        breakdown.append("Education section  : 10/10 ✓")
    else:
        breakdown.append("Education section  :  0/10 — add education details")

    # Has certifications (10 pts)
    if any(w in resume_text.lower() for w in ["certificate", "certification", "course", "coursera", "udemy"]):
        score += 10
        breakdown.append("Certifications     : 10/10 ✓")
    else:
        breakdown.append("Certifications     :  0/10 — add certifications")

    # Length (resume should be substantial)
    word_count = len(resume_text.split())
    length_pts = min(int(word_count / 50), 10)  # 10 pts max
    score += length_pts
    breakdown.append(f"Resume length      : {length_pts}/10 ({word_count} words)")

    # Has contact info (10 pts)
    if any(w in resume_text.lower() for w in ["email", "linkedin", "phone", "@"]):
        score += 10
        breakdown.append("Contact info       : 10/10 ✓")
    else:
        breakdown.append("Contact info       :  0/10 — add contact information")

    return score, "\n".join(breakdown)


# ──────────────────────────────────────────────
# REPORT GENERATORS
# ──────────────────────────────────────────────

def generate_job_analysis(job_text: str, job_skills: list[str]) -> str:
    lines = [
        "=" * 60,
        "JOB ANALYSIS REPORT",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "SKILLS & KEYWORDS FOUND IN JOB POSTERS:",
        "-" * 40,
    ]
    for s in job_skills:
        lines.append(f"  ✓  {s}")

    lines += [
        "",
        f"TOTAL SKILLS EXTRACTED: {len(job_skills)}",
        "",
        "SAMPLE JD CONTENT (first 800 chars):",
        "-" * 40,
        job_text[:800].strip(),
        "...",
    ]
    return "\n".join(lines)


def generate_skill_gap_report(
    job_skills: list[str],
    resume_skills: list[str],
    matched: list[str],
    missing: list[str],
    score: float,
) -> str:
    lines = [
        "=" * 60,
        "SKILL GAP REPORT",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"MATCH SCORE: {score}%",
        f"  Job skills required : {len(job_skills)}",
        f"  Skills matched      : {len(matched)}",
        f"  Skills missing      : {len(missing)}",
        "",
        "MATCHED SKILLS:",
        "-" * 40,
    ]
    for s in matched:
        lines.append(f"  ✓  {s}")

    lines += ["", "MISSING SKILLS (gaps to close):", "-" * 40]
    for s in missing:
        lines.append(f"  ✗  {s}")

    lines += [
        "",
        "IMPROVEMENT PRIORITY:",
        "-" * 40,
        "  Focus on the missing skills listed above.",
        "  Build small projects or take short courses to demonstrate them.",
        "  Add them to your resume once you can give evidence of usage.",
    ]
    return "\n".join(lines)


def generate_resume_suggestions(
    job_skills: list[str],
    missing: list[str],
    quality_score: int,
    quality_breakdown: str,
) -> str:
    lines = [
        "=" * 60,
        "TAILORED RESUME SUGGESTIONS",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"RESUME QUALITY SCORE: {quality_score}/100",
        "-" * 40,
        quality_breakdown,
        "",
        "SUGGESTED IMPROVEMENTS (aligned with job requirements):",
        "-" * 40,
    ]
    for skill in job_skills:
        lines.append(f"  • Demonstrate '{skill}' with a concrete project or experience.")

    lines += [
        "",
        "SUGGESTED RESUME BULLET POINTS:",
        "-" * 40,
        "  • Built a file-driven AI agent using the GAME framework in Python with full documentation.",
        "  • Trained ML models achieving 87%+ accuracy, evaluated using precision, recall, and F1-score.",
        "  • Developed REST APIs using Flask, integrated SQL databases, and deployed with GitHub CI.",
        "  • Used pandas and numpy for end-to-end data preprocessing and feature engineering pipelines.",
        "  • Applied prompt engineering techniques to interact with LLM APIs for task automation.",
        "  • Maintained all projects on GitHub with README files and version-controlled commits.",
        "  • Collaborated in team environments using Git branching, pull requests, and code reviews.",
    ]

    if missing:
        lines += [
            "",
            "PRIORITY SKILLS TO ADD/IMPROVE BEFORE APPLYING:",
            "-" * 40,
        ]
        for skill in missing:
            lines.append(f"  ⚠  {skill} — build a mini project or add a certification")

    lines += [
        "",
        "GENERAL TIPS:",
        "-" * 40,
        "  • Keep your resume to 1 page if under 2 years of experience.",
        "  • Quantify every achievement (%, numbers, time saved).",
        "  • Tailor your resume for each job — use keywords from the JD.",
        "  • Put the most recent and relevant experience at the top.",
        "  • Proofread carefully — typos are automatic rejection signals.",
    ]
    return "\n".join(lines)


def generate_interview_questions(job_skills: list[str], kb_text: str) -> str:
    lines = [
        "=" * 60,
        "INTERVIEW QUESTIONS (from JD + KB)",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "TECHNICAL QUESTIONS (based on job skills):",
        "-" * 40,
    ]
    for skill in job_skills:
        lines.append(f"  Q: Explain your understanding of {skill}.")
        lines.append(f"  Q: How have you used {skill} in a real project or academic task?")
        lines.append("")

    lines += [
        "HR / BEHAVIORAL QUESTIONS:",
        "-" * 40,
        "  Q: Tell me about yourself.",
        "  Q: Why are you interested in this role and this company?",
        "  Q: Describe your best academic or personal project.",
        "  Q: What is your greatest technical strength?",
        "  Q: What is something you are still working to improve?",
        "  Q: How do you handle tight deadlines or unexpected problems?",
        "  Q: Describe a time you worked in a team — what was your role?",
        "  Q: Why should we select you over other candidates?",
        "",
        "QUESTIONS FROM KNOWLEDGE BASE (top concepts):",
        "-" * 40,
    ]

    kb_lines = [line.strip().lstrip("- •") for line in kb_text.splitlines() if len(line.strip()) > 30]
    for kb_line in kb_lines[:20]:
        lines.append(f"  Q: How would you explain this in an interview: \"{kb_line.strip()[:100]}\"?")

    lines += [
        "",
        "PREPARATION TIPS:",
        "-" * 40,
        "  • Use the STAR format for behavioral answers (Situation, Task, Action, Result).",
        "  • Prepare 2-3 strong project stories under 2 minutes each.",
        "  • Research the company before the interview.",
        "  • Prepare 2 thoughtful questions to ask the interviewer.",
        "  • Practice speaking aloud — clarity and confidence matter.",
    ]
    return "\n".join(lines)


def generate_cover_letter(
    job_text: str,
    resume_text: str,
    matched: list[str],
    company_name: str = "the company",
    role_name: str = "this position",
) -> str:
    # Extract company and role from job text if possible
    for line in job_text.splitlines():
        if "company:" in line.lower():
            company_name = line.split(":", 1)[-1].strip()
        if "position:" in line.lower() or "role:" in line.lower():
            role_name = line.split(":", 1)[-1].strip()

    skills_str = ", ".join(matched[:5]) if matched else "Python, machine learning, and problem solving"

    letter = f"""{'='*60}
COVER LETTER (Auto-Generated — Personalise Before Sending)
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Date: {TODAY.strftime('%B %d, %Y')}

Hiring Manager
{company_name}

Dear Hiring Manager,

I am writing to express my strong interest in the {role_name} position at
{company_name}. As a Computer Science undergraduate with practical exposure
to {skills_str}, I believe I can deliver value to your team from the outset.

Over the course of my studies I have completed projects spanning machine
learning model development, RESTful API construction with Flask, relational
database management, and version-controlled collaboration on GitHub. I have
additionally explored LLM APIs and applied prompt-engineering strategies to
automate knowledge-intensive workflows.

I am particularly drawn to {company_name} because of the opportunity to work
on real-world problems in a professional setting. I adapt quickly to new
technologies, communicate clearly within teams, and take pride in producing
readable, well-documented code.

My resume is attached for your reference. I would greatly appreciate the
chance to discuss how my skills align with this role at your convenience.

Thank you for considering my application.

Yours sincerely,

Qasim Zubair
qasimzubair166@gmail.com
"""
    return letter


def generate_linkedin_message(
    job_text: str,
    company_name: str = "your company",
    role_name: str = "the position",
) -> str:
    for line in job_text.splitlines():
        if "company:" in line.lower():
            company_name = line.split(":", 1)[-1].strip()
        if "position:" in line.lower() or "role:" in line.lower():
            role_name = line.split(":", 1)[-1].strip()

    message = f"""{'='*60}
LINKEDIN RECRUITER OUTREACH MESSAGE
{'='*60}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
(Aim for under 300 characters in InMail — personalise before sending)

─── BRIEF VERSION ────────────────────────────────────────
Hi [Recruiter Name], I am a CS student with a focus on AI/ML and
came across the {role_name} opening at {company_name}. I would love
to connect and hear more about the role. Email: qasimzubair166@gmail.com

─── FULL VERSION (Connection Request Note) ───────────────
Hi [Name], I am an undergraduate CS student with hands-on experience
in Python, machine learning, and building intelligent agents. I came
across the {role_name} vacancy at {company_name} and feel my project
portfolio maps closely to the requirements. Any guidance or a quick
chat about the opportunity would be greatly appreciated.
Email: qasimzubair166@gmail.com
"""
    return message


# ──────────────────────────────────────────────
# APPLICATION TRACKER
# ──────────────────────────────────────────────

TRACKER_HEADERS = [
    "application_id", "company", "role", "source", "status",
    "applied_date", "interview_date", "follow_up_date", "next_action", "notes"
]


def create_or_update_tracker() -> str:
    """Create tracker CSV with sample rows if it doesn't exist. Return path."""
    if os.path.exists(TRACKER_FILE):
        return TRACKER_FILE  # Don't overwrite existing data

    today_str = TODAY.strftime("%Y-%m-%d")
    tomorrow_str = date(TODAY.year, TODAY.month, min(TODAY.day + 1, 28)).strftime("%Y-%m-%d")
    interview_date = date(TODAY.year, TODAY.month, min(TODAY.day + 5, 28)).strftime("%Y-%m-%d")
    followup_date  = date(TODAY.year, TODAY.month, min(TODAY.day + 8, 28)).strftime("%Y-%m-%d")

    rows = [
        {
            "application_id": "APP-001",
            "company": "TechVision AI",
            "role": "Junior AI Engineer Intern",
            "source": "LinkedIn",
            "status": "Interview Scheduled",
            "applied_date": today_str,
            "interview_date": interview_date,
            "follow_up_date": followup_date,
            "next_action": "Revise Python, ML basics, and prepare project explanation notes",
            "notes": "Resume tailored for Python and ML role",
        },
        {
            "application_id": "APP-002",
            "company": "DataFlow Systems",
            "role": "Python Backend Developer (Junior)",
            "source": "Rozee.pk",
            "status": "Applied",
            "applied_date": today_str,
            "interview_date": "",
            "follow_up_date": followup_date,
            "next_action": "Follow up if no response received",
            "notes": "Emphasized Flask and SQL experience in resume",
        },
        {
            "application_id": "APP-003",
            "company": "StartupX",
            "role": "ML Trainee",
            "source": "WhatsApp Poster",
            "status": "Not Applied",
            "applied_date": "",
            "interview_date": "",
            "follow_up_date": tomorrow_str,
            "next_action": "Tailor resume for ML role and apply before deadline",
            "notes": "Deadline is soon — prioritize this",
        },
        {
            "application_id": "APP-004",
            "company": "DigitalNest",
            "role": "Junior Software Engineer",
            "source": "LinkedIn",
            "status": "Shortlisted",
            "applied_date": today_str,
            "interview_date": "",
            "follow_up_date": followup_date,
            "next_action": "Prepare for technical assessment",
            "notes": "Strong DSA and Flask experience highlighted",
        },
        {
            "application_id": "APP-005",
            "company": "CodeHouse",
            "role": "AI Intern",
            "source": "Company Website",
            "status": "Rejected",
            "applied_date": today_str,
            "interview_date": "",
            "follow_up_date": "",
            "next_action": "Request feedback and improve weak areas",
            "notes": "Lacked Docker experience — consider learning it",
        },
    ]

    with open(TRACKER_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=TRACKER_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    return TRACKER_FILE


def _parse_date(date_str: str):
    """Safely parse a date string to a date object."""
    if not date_str or date_str.strip() == "":
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def _urgency_label(target_date) -> str:
    """Return urgency label based on how far the date is from today."""
    if target_date is None:
        return ""
    delta = (target_date - TODAY).days
    if delta < 0:
        return "🔴 OVERDUE"
    elif delta == 0:
        return "🟠 TODAY"
    elif delta == 1:
        return "🟡 TOMORROW"
    elif delta <= 7:
        return "🔵 THIS WEEK"
    else:
        return "🟢 UPCOMING"


def generate_reminders() -> str:
    lines = [
        "=" * 60,
        "APPLICATION REMINDERS (Urgency-Aware)",
        "=" * 60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Today's Date: {TODAY.strftime('%Y-%m-%d')}",
        "",
    ]

    if not os.path.exists(TRACKER_FILE):
        lines.append("No tracker file found. Run the agent first to create it.")
        return "\n".join(lines)

    reminders_by_urgency = {"🔴 OVERDUE": [], "🟠 TODAY": [], "🟡 TOMORROW": [], "🔵 THIS WEEK": [], "🟢 UPCOMING": [], "INFO": []}

    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            app_id       = row.get("application_id", "")
            company      = row.get("company", "")
            role         = row.get("role", "")
            status       = row.get("status", "").strip()
            interview_dt = _parse_date(row.get("interview_date", ""))
            followup_dt  = _parse_date(row.get("follow_up_date", ""))
            next_action  = row.get("next_action", "")

            if status.lower() == "interview scheduled" and interview_dt:
                urg = _urgency_label(interview_dt)
                msg = (f"[{app_id}] {urg} — Interview with {company} for '{role}' "
                       f"on {interview_dt}.\n    Action: {next_action}")
                reminders_by_urgency.get(urg, reminders_by_urgency["INFO"]).append(msg)

            elif status.lower() == "not applied":
                urg = _urgency_label(followup_dt) if followup_dt else "INFO"
                msg = (f"[{app_id}] {urg} — NOT APPLIED yet to {company} for '{role}'. "
                       f"\n    Action: Tailor resume and apply ASAP.")
                reminders_by_urgency.get(urg, reminders_by_urgency["INFO"]).append(msg)

            elif status.lower() == "applied":
                urg = _urgency_label(followup_dt) if followup_dt else "🟢 UPCOMING"
                msg = (f"[{app_id}] {urg} — Application sent to {company}. "
                       f"Follow up on {followup_dt or 'N/A'} if no response.\n    Action: {next_action}")
                reminders_by_urgency.get(urg, reminders_by_urgency["INFO"]).append(msg)

            elif status.lower() == "shortlisted":
                msg = (f"[{app_id}] 🟡 SHORTLISTED — {company} for '{role}'. "
                       f"\n    Action: Prepare for technical test or next round. {next_action}")
                reminders_by_urgency["🟡 TOMORROW"].append(msg)

            elif status.lower() == "offered":
                msg = (f"[{app_id}] 🎉 OFFER RECEIVED — {company} for '{role}'. "
                       f"\n    Action: Review offer terms and respond within deadline.")
                reminders_by_urgency["INFO"].append(msg)

    for urgency in ["🔴 OVERDUE", "🟠 TODAY", "🟡 TOMORROW", "🔵 THIS WEEK", "🟢 UPCOMING", "INFO"]:
        items = reminders_by_urgency[urgency]
        if items:
            lines.append(f"\n{'─'*40}")
            lines.append(f"  {urgency}")
            lines.append(f"{'─'*40}")
            for item in items:
                lines.append(f"\n  {item}")

    return "\n".join(lines)


def generate_tracker_summary() -> str:
    """Return a text dashboard of application status counts."""
    if not os.path.exists(TRACKER_FILE):
        return "No tracker file found.\n"

    counts = {}
    total  = 0

    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row.get("status", "Unknown").strip()
            counts[status] = counts.get(status, 0) + 1
            total += 1

    lines = [
        "=" * 60,
        "APPLICATION STATUS DASHBOARD",
        "=" * 60,
        f"Total Applications: {total}",
        "",
    ]
    bar_width = 30
    for status, cnt in sorted(counts.items()):
        pct  = cnt / total if total else 0
        bar  = "█" * int(pct * bar_width)
        lines.append(f"  {status:<22} {bar:<30} {cnt} ({pct*100:.0f}%)")

    return "\n".join(lines)


# ──────────────────────────────────────────────
# MEMORY (JSON)
# ──────────────────────────────────────────────

def save_memory(data: dict):
    """Persist agent memory as JSON."""
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  [MEMORY] Saved to {MEMORY_FILE}")


# ──────────────────────────────────────────────
# MAIN AGENT ORCHESTRATOR
# ──────────────────────────────────────────────

def run_agent():
    print("\n" + "=" * 60)
    print("  CareerPrep Job-Hunting Agent — Starting...")
    print("=" * 60)

    # Step 0: Ensure folders exist
    ensure_folders()
    print("\n[STEP 1/9] Reading input files...")

    # Step 1: Read all files
    job_text,    job_count,    job_files    = read_files_from_folder(JOB_DIR)
    resume_text, resume_count, resume_files = read_files_from_folder(RESUME_DIR)
    kb_text,     kb_count,     kb_files     = read_files_from_folder(KB_DIR)

    print(f"  Job files    : {job_count} ({', '.join(job_files) or 'none'})")
    print(f"  Resume files : {resume_count} ({', '.join(resume_files) or 'none'})")
    print(f"  KB files     : {kb_count} ({', '.join(kb_files) or 'none'})")

    if job_count == 0 or resume_count == 0 or kb_count == 0:
        print("\n[ERROR] Please add at least one file to each input folder before running.")
        print("  • input_jobs/   — paste a job poster as .txt")
        print("  • input_resumes/ — paste your resume as .txt")
        print("  • input_kb/     — paste course notes as .txt")
        return

    # Step 2: Extract skills
    print("\n[STEP 2/9] Extracting skills and keywords...")
    job_skills    = extract_keywords(job_text)
    resume_skills = extract_keywords(resume_text)
    matched, missing, score = compare_skills(job_skills, resume_skills)
    print(f"  Job skills   : {len(job_skills)}")
    print(f"  Resume skills: {len(resume_skills)}")
    print(f"  Match score  : {score}%")

    # Step 3: Resume quality score
    print("\n[STEP 3/9] Scoring resume quality...")
    quality_score, quality_breakdown = resume_quality_score(resume_text, resume_skills)
    print(f"  Resume quality score: {quality_score}/100")

    # Step 4: Generate reports
    print("\n[STEP 4/9] Generating analysis reports...")
    job_report         = generate_job_analysis(job_text, job_skills)
    gap_report         = generate_skill_gap_report(job_skills, resume_skills, matched, missing, score)
    resume_suggestions = generate_resume_suggestions(job_skills, missing, quality_score, quality_breakdown)
    interview_qs       = generate_interview_questions(job_skills, kb_text)
    cover_letter       = generate_cover_letter(job_text, resume_text, matched)
    linkedin_msg       = generate_linkedin_message(job_text)

    # Step 5: Tracker
    print("\n[STEP 5/9] Creating / updating application tracker...")
    create_or_update_tracker()
    tracker_summary = generate_tracker_summary()
    print(f"  Tracker file : {TRACKER_FILE}")

    # Step 6: Reminders
    print("\n[STEP 6/9] Generating urgency-aware reminders...")
    reminders = generate_reminders()

    # Step 7: Compile final report
    print("\n[STEP 7/9] Compiling final report...")
    final_report = "\n\n".join([
        f"CareerPrep Job-Hunting Agent — Final Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{'='*60}",
        tracker_summary,
        job_report,
        gap_report,
        resume_suggestions,
        interview_qs,
        cover_letter,
        linkedin_msg,
        reminders,
    ])

    # Step 8: Save all outputs
    print("\n[STEP 8/9] Saving output files...")
    save_text(os.path.join(OUTPUT_DIR, "job_analysis_report.txt"),       job_report)
    save_text(os.path.join(OUTPUT_DIR, "skill_gap_report.txt"),          gap_report)
    save_text(os.path.join(OUTPUT_DIR, "tailored_resume_suggestions.txt"), resume_suggestions)
    save_text(os.path.join(OUTPUT_DIR, "interview_questions.txt"),        interview_qs)
    save_text(os.path.join(OUTPUT_DIR, "cover_letter.txt"),              cover_letter)
    save_text(os.path.join(OUTPUT_DIR, "linkedin_message.txt"),          linkedin_msg)
    save_text(os.path.join(OUTPUT_DIR, "final_agent_report.txt"),        final_report)
    save_text(os.path.join(TRACKER_DIR, "reminders.txt"),               reminders)

    # Step 9: Save memory
    print("\n[STEP 9/9] Saving agent memory...")
    save_memory({
        "last_run": datetime.now().isoformat(),
        "job_files": job_files,
        "resume_files": resume_files,
        "kb_files": kb_files,
        "job_skills": job_skills,
        "resume_skills": resume_skills,
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": score,
        "resume_quality_score": quality_score,
    })

    # Summary
    print("\n" + "=" * 60)
    print("  ✅  Agent completed successfully!")
    print("=" * 60)
    print(f"  Job files read    : {job_count}")
    print(f"  Resume files read : {resume_count}")
    print(f"  KB files read     : {kb_count}")
    print(f"  Match score       : {score}%")
    print(f"  Resume quality    : {quality_score}/100")
    print(f"  Outputs saved to  : {OUTPUT_DIR}/")
    print(f"  Tracker saved to  : {TRACKER_DIR}/")
    print("")
    print("  Run the Streamlit dashboard for a visual view:")
    print("  👉  streamlit run dashboard.py")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_agent()
