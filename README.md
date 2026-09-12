<div align="center">

```
           ██████╗ ███████╗██╗   ██╗██████╗ ██╗██╗      ██████╗ ████████╗     █████╗ ██╗
           ██╔══██╗██╔════╝██║   ██║██╔══██╗██║██║     ██╔═══██╗╚══██╔══╝    ██╔══██╗██║
           ██║  ██║█████╗  ██║   ██║██████╔╝██║██║     ██║   ██║   ██║       ███████║██║
           ██║  ██║██╔══╝  ╚██╗ ██╔╝██╔═══╝ ██║██║     ██║   ██║   ██║       ██╔══██║██║
           ██████╔╝███████╗ ╚████╔╝ ██║     ██║███████╗╚██████╔╝   ██║       ██║  ██║██║
           ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝     ╚═╝╚══════╝ ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝
```

# DevPilot AI
### The Engineering Placement & Career Acceleration Dashboard

<p align="center">
  <b>Empowering Software Engineers with ML-Powered ATS Optimization, Deep Career Analytics & AI Intelligence</b>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-10B981?style=for-the-badge)](https://github.com/UdeepChowdary/DevPilot_AI/pulls)

<p align="center">
  <a href="#resume-analyzer"><b>Resume Analyzer</b></a> •
  <a href="#github-profile-analyzer"><b>GitHub Profile Analyzer</b></a> •
  <a href="#modules-overview"><b>Modules Overview</b></a> •
  <a href="#getting-started"><b>Quick Start</b></a> •
  <a href="#project-structure"><b>Architecture</b></a> •
  <a href="#product-roadmap"><b>Roadmap</b></a>
</p>

---

</div>

## About DevPilot AI

**DevPilot AI** is an all-in-one NLP and AI-powered suite built for software engineering students and job candidates preparing for technical internships and placement seasons. DevPilot AI combines **100% offline heuristic ML engines** with optional **Google Gemini AI intelligence** to deliver actionable, transparent, and accurate career tools.

---

## Modules Overview

| Module | Status | Core Technologies & Capabilities |
| :--- | :---: | :--- |
| **Resume Analyzer** | Live | ATS scoring (0–100), layout-aware PDF/DOCX parsing, TF-IDF keyword match, 200+ skill taxonomy, Google XYZ bullet rewriter. |
| **GitHub Profile Analyzer** | Live | Portfolio readiness score (0–100), repo documentation & license audit, language byte breakdown, and AI resume bullets. |
| **AI Code Reviewer** | **Live ✅** | Static analysis for Python, JS, TS, Java, Go, C++, Rust; AST/regex security checks; cyclomatic & Big-O complexity estimation; side-by-side refactoring diff generator. |
| **AI Mock Interview** | Planned | Resume-tailored behavioral & technical interview simulation with speech transcription and pacing critique. |
| **LeetCode Coach** | Planned | Algorithmic topic radar, weak-pattern diagnostic, and automated weekly practice roadmaps. |
| **Placement Dashboard** | Planned | Consolidated readiness scorecard, milestone tracker, and application pipeline manager. |

---

## Resume Analyzer

The **Resume Analyzer** combines machine learning text analytics, NLP parsing, and generative AI to deliver comprehensive resume critiques:

### 1. Multi-Format & Layout-Aware Parsing
- Supports **PDF**, Microsoft Word (**`.docx`**), and plain text (**`.txt`**).
- Implements topologically sorted block extraction via **PyMuPDF** to prevent text corruption on modern 2-column resume designs.
- Accurately detects and maps core resume sections (*Summary, Experience, Education, Skills, Projects, Certifications, Leadership*).

### 2. Normalized ATS Scoring Engine (0–100)
- **Keyword Alignment**: TF-IDF cosine similarity against target Job Descriptions (or vocabulary richness if no JD is provided).
- **Impact & Action Verbs**: Evaluates the density of high-impact engineering action verbs across both past and active tenses (*Spearheaded, Architected, Engineered, Optimized*).
- **Smart Metric Detection**: Identifies true quantified outcomes (%, $, latency in ms, scale in users/events) while filtering out false positives like graduation years and phone numbers.
- **Section & Format Completeness**: Evaluates structural integrity, word count conciseness (350–850 words), and contact information presence.

### 3. Comprehensive 200+ Tech Skills Taxonomy
- Pre-built taxonomy covering languages, frontend, backend, databases, cloud, DevOps, AI/ML, and system design.
- Whitelists critical 1-2 letter skills (`Go`, `C`, `R`, `AI`, `ML`, `CI`, `CD`, `UI`, `UX`) to ensure short acronyms are never missed.
- Generates interactive **Matched vs. Missing Skills** chip visualizations and requirement coverage charts.

### 4. Multi-Engine Bullet Point Enhancer
- **Fast Rule-Based Mode**: Instant offline verb replacement and grammar cleanup (e.g. *"Helped to build"* $\rightarrow$ *"Constructed"* / *"Engineered"*).
- **Gemini AI Mode**: Leverages Google's **XYZ Formula** (*"Accomplished [X] as measured by [Y], by doing [Z]"*) to generate recruiter-ready bullet rewrites.
- **Local T5 Mode**: Offline neural summarization and refinement via Hugging Face Transformers.
- **1-Click Copy Snippets**: Copy any enhanced bullet directly into your clipboard with a single click.

### 5. Exportable ATS Audit Report
- Generate and download a complete Markdown audit report summarizing overall scores, component breakdowns, strengths, areas for improvement, keyword gaps, and bullet rewrites.

---

## GitHub Profile Analyzer

The **GitHub Profile Analyzer** delivers a recruiter-grade audit of an engineer's public GitHub portfolio, evaluating code hygiene, project depth, stack specialization, and translating repositories into resume-ready achievements:

### 1. Developer Portfolio Readiness Score (0–100)
Evaluates public profiles across **5 core dimensions** calibrated against tech recruiter screening standards:

| Dimension | Weight | What It Measures |
| :--- | :---: | :--- |
| **Profile Completeness** | 15 pts | Avatar, clear bio, full name, company/school, location, and linked portfolio/blog URL. |
| **Repo Quality & Hygiene** | 35 pts | Original project ratio, descriptions, README presence, OSI-approved licenses, topic tags, and live deployment demo URLs. |
| **Activity & Consistency** | 25 pts | Push recency, active quarterly maintenance, and sustained multi-project cadence. |
| **Language & Stack Depth** | 15 pts | Byte-level codebase volume, primary stack specialization, and polyglot versatility. |
| **Community & Impact** | 10 pts | Star counts, community forks, and follower peer validation. |

**Grading Scale**:
- `A+` (90–100): *Elite Showcase* — High-conviction portfolio ready for Tier-1 tech screening.
- `A` (80–89): *Strong Candidate* — Solid open-source presence with clean documentation.
- `B` (65–79): *Competent Developer* — Good foundations; needs license badges, topic tags, or live demos.
- `C` (50–64): *Developing Portfolio* — Missing repo descriptions, outdated code, or unbalanced fork ratios.
- `D/F` (<50): *Needs Attention* — Incomplete profile or blank placeholder repositories.

---

### 2. Portfolio Diagnostics & Prioritized Action Plan (Tab 1)
- **Recruiter Verdict**: Instant synthesized hiring-manager summary highlighting candidate caliber and standout traits.
- **Green Flags & Red Flags**: Identifies competitive strengths (e.g. *Production-ready live deployments, MIT licenses*) and warning signs (e.g. *Missing repository descriptions*).
- **Interactive 5-Axis Radar Chart**: Visualizes balance across all 5 evaluation dimensions in real time.
- **Prioritized Action Plan**: Ranked task checklist sorted by **Impact** (High / Medium) and **Estimated Effort** (5–30 mins) to immediately boost score.

---

### 3. Repository-by-Repository Health Audit (Tab 2)
- **Individual Repo Hygiene Badges**: Pass/Fail indicators for:
  - `Description` (verifies presence and length)
  - `Live Demo` (detects Vercel, Netlify, Render, GitHub Pages, etc.)
  - `License` (verifies MIT, Apache, GPL, BSD)
  - `Topics` (verifies discoverability tags)
- **Repo Health Scores (0–100)**: Individual repository ratings based on complete metadata and community stars.
- **Interactive Search & Sorting**: Filter repositories by name, language, health score, stars, or recent commit updates.
- **Targeted Fix Recommendations**: Expandable per-repository tips on how to improve presentation for recruiters.

---

### 4. Tech Stack & Language Composition (Tab 3)
- **Byte-Accurate Donut Chart**: Visualizes actual lines and bytes of code written across all public repositories.
- **Stack Specialization Progress Bars**: Displays percentages and byte volume for top programming languages.
- **Repository Language Counts**: Tracks how many distinct projects utilize each technology.

---

### 5. AI Recruiter Coach & XYZ Resume Bullets (Tab 4)
- **30-Second Interview Elevator Pitch**: A verbal script tailored to the candidate's exact top repositories for the classic *"Walk me through your background and projects"* interview question.
- **Google XYZ Resume Bullets**: Automatically extracts technical context from top repositories and formats them into quantified bullets (*"Engineered [X] as measured by [Y], by doing [Z]"*).
- **Recruiter Interview Tips**: Specific talking points highlighting architecture decisions, scaling challenges, and trade-offs.
- **Strategic Capstone Recommender**: Diagnoses portfolio gaps and recommends high-leverage project ideas to build next.
- **Likely Technical Interview Questions**: Anticipates questions hiring managers will ask based on repository implementations.

---

### 6. Exportable Portfolio Audit Report (Tab 5)
- **1-Click Markdown Download**: Generates a portable, cleanly formatted `.md` audit report containing the full portfolio scorecard, repository table, action checklist, and AI critiques.

---

## Project Structure

```bash
DevPilot_AI/
├── app.py                      # Main landing page & module dashboard
├── requirements.txt            # Python dependencies
├── pages/
│   ├── 1_📄_Resume_Analyzer.py # Resume Analyzer UI & interactive workflows
│   └── 2_🐙_GitHub_Analyzer.py # GitHub Profile Analyzer & Recruiter Auditor
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py        # PDF, DOCX, TXT extraction & section detection
│   ├── ats_scorer.py           # ATS scoring algorithm (TF-IDF & heuristics)
│   ├── keyword_extractor.py    # RAKE, spaCy & 200+ Tech skills taxonomy
│   ├── bullet_enhancer.py      # Rule-based, Gemini XYZ, and T5 enhancers
│   ├── github_fetcher.py       # GitHub REST API v3 data ingestion & statistics
│   ├── github_scorer.py        # 0–100 Portfolio readiness scoring & diagnostics
│   ├── github_ai_reviewer.py   # Gemini AI portfolio coach & resume bullet generator
│   └── gemini_client.py        # Google Gemini API connector
└── LICENSE                     # MIT License
```

---

## Getting Started

### Prerequisites
- Python **3.10+**
- (Optional) A [Google Gemini API Key](https://aistudio.google.com/) for smart AI rewrites.
- (Optional) A [GitHub Personal Access Token](https://github.com/settings/tokens) for 5,000 requests/hr rate limits.

### 1. Clone the Repository
```bash
git clone https://github.com/UdeepChowdary/DevPilot_AI.git
cd DevPilot_AI
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv

# Windows:
.\venv\Scripts\activate

# macOS / Linux:
source venv/activate

pip install -r requirements.txt
```

### 3. (Optional) Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GITHUB_TOKEN=your_optional_github_token_here
```
*(Note: DevPilot AI can run 100% offline without an API key using built-in rule-based and local NLP heuristics.)*

### 4. Launch the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## Product Roadmap

- [x] **v1.0**: Resume Analyzer (ATS Scoring, Keyword Matching, Multi-engine Bullets, PDF/DOCX Support, Report Exporter)
- [x] **v1.1**: GitHub Profile Analyzer (Portfolio scoring, repo health audit, tech stack breakdown, AI resume bullets)
- [x] **v1.5**: AI Code Reviewer (Static analysis for 7 languages, cyclomatic/Big-O complexity, security checks, refactoring suggestions)
- [ ] **v2.0**: AI Mock Interview (Resume-tailored questions, audio transcription, feedback)
- [ ] **v2.5**: LeetCode Algorithmic Coach & Placement Readiness Tracker

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
