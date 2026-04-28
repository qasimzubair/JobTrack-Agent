# JobTrack Agent — Intelligent Job-Hunting Assistant

> **Author:** Qasim Zubair | Roll No: 22F-3100 | Section: AI-8B | FAST University
> **Email:** qasimzubair166@gmail.com

A **file-driven AI agent** implementing the GAME framework (Goal, Actions, Memory, Environment) that ingests job descriptions, resumes, and knowledge-base notes from designated local folders to automate and organise the entire job-application workflow.

---

## Features

| Feature | Description |
|---|---|
| File Reading | Reads `.txt` and `.pdf` files from `input_jobs/`, `input_resumes/`, `input_kb/` |
| Job Analysis | Extracts skills and keywords from job posters |
| Skill Gap Report | Compares job requirements with your resume, shows match % |
| Resume Tailoring | Personalized bullet points and improvement suggestions |
| Resume Quality Score | Scores your resume out of 100 across 7 criteria |
| Interview Questions | Generates technical, HR, and KB-inspired questions |
| Cover Letter | Auto-generates a customizable cover letter |
| LinkedIn Message | Drafts a recruiter outreach message |
| Application Tracker | CSV tracker with status, interview dates, follow-ups |
| Smart Reminders | Date-aware urgency labels: Overdue / Today / Tomorrow / This Week |
| JSON Memory | Persists agent context between runs |
| Streamlit Dashboard | Visual 7-tab web UI with charts and download buttons |

---

## Folder Structure

```
job-hunting-agent/
├── app.py               # Main CLI agent
├── dashboard.py         # Streamlit web dashboard
├── requirements.txt
├── .gitignore
├── README.md
├── reflection.md
│
├── input_jobs/          # Paste job posters here (.txt or .pdf)
├── input_resumes/       # Paste your resume here (.txt or .pdf)
├── input_kb/            # Paste course notes / prep material here (.txt or .pdf)
│
├── outputs/             # Generated reports (auto-created on run)
├── tracker/             # CSV tracker + reminders (auto-created on run)
└── samples/             # Pre-filled example files
```

---

## Setup and Installation

### 1. Clone the repository
```bash
git clone https://github.com/qasimzubair/job-hunting-agent.git
cd job-hunting-agent
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run

### Option A — CLI Agent (generates all reports)
```bash
python app.py
```

### Option B — Streamlit Dashboard (visual UI)
```bash
streamlit run dashboard.py
```
Then open **http://localhost:8501** in your browser.

---

## Input Guide

| Folder | What to Add |
|---|---|
| `input_jobs/` | Copy job postings from LinkedIn / Rozee / WhatsApp as `.txt` files |
| `input_resumes/` | Paste your resume as `my_resume.txt` |
| `input_kb/` | Copy course slides, prep notes as `.txt` files |

> **Tip:** PDF files are also supported — the agent auto-extracts text from them.

---

## Output Files

| File | Description |
|---|---|
| `outputs/job_analysis_report.txt` | Extracted skills from job posters |
| `outputs/skill_gap_report.txt` | Match score + gaps |
| `outputs/tailored_resume_suggestions.txt` | Resume quality + improvement tips |
| `outputs/interview_questions.txt` | Technical + HR questions |
| `outputs/cover_letter.txt` | Auto-generated cover letter |
| `outputs/linkedin_message.txt` | Recruiter outreach message |
| `outputs/final_agent_report.txt` | Complete combined report |
| `tracker/applications.csv` | Application status tracker |
| `tracker/reminders.txt` | Urgency-aware reminders |
| `tracker/memory.json` | Agent memory (persistent context) |

---

## Tech Stack

- **Language:** Python 3.10+
- **Libraries:** `streamlit`, `matplotlib`, `pandas`, `pypdf`, `csv`, `json`, `os`, `datetime`
- **Framework:** GAME (Goal, Actions, Memory, Environment)
- **Version Control:** Git + GitHub
