# Reflection — JobTrack Agent: Intelligent Job-Hunting Assistant

## Student Submission Form

| Field | Value |
|---|---|
| **Student Name** | Qasim Zubair |
| **Roll Number** | 22F-3100 |
| **Section** | AI-8B |
| **University** | FAST University |
| **Email** | qasimzubair166@gmail.com |
| **Job posters in input_jobs/** | 2 |
| **Resume files in input_resumes/** | 1 |
| **KB files in input_kb/** | 2 |

### Agent Features Implemented
- Folder-based file reading: **Yes** (TXT + PDF via pypdf)
- Job description analysis: **Yes**
- Resume keyword analysis: **Yes**
- Skill-gap report: **Yes** (with match percentage)
- Resume tailoring suggestions: **Yes** (with quality scoring)
- Interview question generation from KB: **Yes**
- Application tracker: **Yes** (CSV with 10 columns)
- Reminders: **Yes** (urgency labels: Overdue / Today / Tomorrow / This Week / Upcoming)

### Unique Features Added
- Automated cover letter generation (personalised per job)
- LinkedIn recruiter outreach message drafter
- Seven-criteria resume quality scorer (0–100 scale)
- Graceful PDF text extraction using pypdf
- JSON-based memory persistence for session continuity
- Streamlit dashboard with 7 interactive tabs, charts, and file downloads
- Colour-coded urgency reminder cards (🔴🟠🟡🔵🟢)

### AI Tool Usage
Antigravity AI was consulted for code structure and refactoring suggestions. All logic, testing, and design decisions were carried out and verified independently.

### Testing Evidence
- `python app.py` executed without errors, producing correct skill and match outputs
- All 10 output files confirmed present in `outputs/` and `tracker/`
- Streamlit dashboard verified across all 7 tabs; charts displayed correctly
- Boundary cases verified: empty-folder warning, auto-creation of missing directories

### Declaration
I confirm that I independently built, tested, and understand every part of the submitted code.

**Signature:** Qasim Zubair | **Date:** 2026-04-28

---


## What Was Built

The **JobTrack Agent** is a fully file-driven agentic system structured around the **GAME framework**:

| GAME Component | How It Is Realised |
|---|---|
| **Goal** | Streamline every stage of a student's job-application process |
| **Actions** | Reading input files, extracting keywords, producing reports, updating the tracker, scheduling reminders |
| **Memory** | `tracker/memory.json` (run-to-run persistence), `tracker/applications.csv` (structured history) |
| **Environment** | Local directory tree, Python standard library, plus lightweight optional packages |

---

## Core Features Implemented

### 1. Multi-Format File Ingestion (TXT + PDF)
The agent iterates all `.txt` and `.pdf` files inside each designated input directory. Plain-text files are opened with the built-in `open()` function; PDFs are parsed via `pypdf` with a graceful fallback message when the library is absent.

### 2. Keyword-Based Skill Extraction
Over 50 industry-relevant skill tokens are checked against each document using case-insensitive search. This lightweight approach removes the need for heavyweight NLP models while still producing actionable results.

### 3. Skill Gap Computation
Skills detected in the job description are set-compared with those found in the resume. The output includes a matched list, a missing list, and a numeric match percentage that quantifies the candidate's readiness.

### 4. Resume Tailoring and Quality Scoring
Per-skill improvement suggestions are produced from the JD keywords. A seven-dimension quality scorer (skills breadth, GitHub presence, projects, education, certifications, word count, contact info) returns a total out of 100.

### 5. Interview Question Generator
For every detected job skill a targeted technical question is produced. A fixed set of universal behavioural questions is appended, and knowledge-base sentences are recast as practice prompts, turning study notes into interview preparation material.

### 6. Cover Letter and LinkedIn Draft
Both outputs are scaffolded using fields extracted directly from the job poster (company name, role title). Users receive a reminder to personalise the templates before submission.

### 7. Structured Application Tracker
A ten-column CSV (`tracker/applications.csv`) records company, role, source, status, key dates, and next actions. Five representative sample rows spanning all status values are seeded on first run.

### 8. Urgency-Tagged Reminders
The reminder engine reads the tracker CSV, computes the gap between each deadline and `date.today()`, and attaches one of five urgency labels: 🔴 Overdue / 🟠 Today / 🟡 Tomorrow / 🔵 This Week / 🟢 Upcoming.

### 9. Streamlit Dashboard (7 Tabs)
A polished web interface exposes:
- Summary metrics and a status distribution chart
- Skill gap visualised with progress bars and tag chips
- Resume quality gauge alongside actionable suggestions
- Filterable interview question list
- Editable tracker table with status tallies
- Colour-coded reminder cards grouped by urgency level

### 10. Persistent JSON Memory
Key agent state — most recent run timestamp, extracted skill lists, match score, resume quality score — is written to `tracker/memory.json` so subsequent runs can reference the previous session.

---

## Design Decisions

- **Zero API-key dependency** — Every feature operates on deterministic rule-based logic, ensuring the agent is immediately runnable by any student without a paid account.
- **Optional-dependency design** — `pypdf`, `pandas`, and `matplotlib` are loaded conditionally; the core CLI pipeline remains fully usable if they are absent.
- **Ready-to-run sample data** — Pre-filled input files allow the agent to produce meaningful output the moment it is cloned, lowering the barrier to demonstration.
- **Dashboard as the primary interface** — The Streamlit UI was treated as a first-class deliverable rather than an afterthought, with visual hierarchy and interactivity given equal weight to the underlying logic.

---

## Testing

### CLI Test
```bash
python app.py
```
**Result:** All 9 steps completed. 7 output files created in `outputs/`, 3 files in `tracker/`.

### File Count Verification
```
outputs/job_analysis_report.txt        ✓
outputs/skill_gap_report.txt           ✓
outputs/tailored_resume_suggestions.txt ✓
outputs/interview_questions.txt         ✓
outputs/cover_letter.txt               ✓
outputs/linkedin_message.txt           ✓
outputs/final_agent_report.txt         ✓
tracker/applications.csv               ✓
tracker/reminders.txt                  ✓
tracker/memory.json                    ✓
```

### Dashboard Test
```bash
streamlit run dashboard.py
```
All 7 tabs loaded, charts rendered, download buttons functional, reminders color-coded.

---

## What Could Be Improved

1. **LLM Integration** — Plugging in a generative model (e.g., Gemini or GPT) would replace template outputs with context-sensitive, nuanced suggestions.
2. **Embedding-based skill matching** — Replacing substring search with vector similarity would handle synonyms and abbreviations (e.g., "ML" ↔ "machine learning") automatically.
3. **Automated JD ingestion** — Scraping job listings directly from job boards would eliminate the manual copy-paste step.
4. **Push notifications** — Routing reminders through email or a messaging API would make the urgency system genuinely actionable beyond a local text file.
5. **Per-job resume targeting** — Supporting multiple resume variants and letting the user choose which to compare against each posting.
6. **Role-based access** — Enabling multi-user deployment of the Streamlit dashboard with individual data isolation.
