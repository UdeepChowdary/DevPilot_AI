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
[![Version](https://img.shields.io/badge/Version-3.0.1-6366F1?style=for-the-badge)](README.md)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-2.0%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)

<p align="center">
  <a href="#resume-analyzer"><b>Resume Analyzer</b></a> •
  <a href="#github-profile-analyzer"><b>GitHub Profile Analyzer</b></a> •
  <a href="#ai-mock-interview"><b>AI Mock Interview</b></a> •
  <a href="#leetcode-coach"><b>LeetCode Coach</b></a> •
  <a href="#placement-readiness-dashboard"><b>Placement Dashboard</b></a> •
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
| **AI Mock Interview** | Live | Resume-tailored behavioral & technical interview simulation, speech pacing analysis, 4-dimension scoring rubric, and exportable PDF audit. |
| **LeetCode Coach** | Live | Algorithmic topic radar across 8 core pillars, weak-pattern diagnostic, curated company roadmaps, AI complexity optimizer, and PDF export. |
| **Placement Dashboard** | Live | Unified Engineering Readiness Score (0–100), 4-pillar benchmark radar, milestone sprint planner, application Kanban pipeline, and PDF dossier export. |

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

## AI Mock Interview

The **AI Mock Interview** simulator replicates real-world technical and behavioral interview loops calibrated against top tech company screening bars:

### 1. Resume-Tailored Question Generation
- Auto-extracts technologies, frameworks, and project bullets from your active parsed resume to generate hyper-tailored questions.
- Customizable interview styles: **FAANG / Tier-1 Big Tech**, **High-Growth Tech Unicorn**, **FinTech / Low-Latency**, and **Early-Stage Startup**.
- Question focus modes: *Mixed Technical & Behavioral*, *Deep System Architecture*, and *Behavioral STAR Leadership*.

### 2. Multi-Modal Audio & Written Delivery
- Native microphone recording support using Streamlit audio input.
- Real-time audio transcription powered by Google Gemini multimodal understanding.
- Rich text answer editor allowing candidates to speak, type, or refine responses.

### 3. Recruiter Scoring Rubric (0–100)
Evaluates candidate answers across **4 core dimensions** (25 pts each):
- **Technical Correctness & Depth (25 pts)**: Architecture choices, data structures, concurrency, and API contracts.
- **Structure & Organization (25 pts)**: Logical sequencing using the **STAR Method** (*Situation, Task, Action, Result*).
- **Communication & Delivery (25 pts)**: Clarity, brevity, and automatic verbal filler detection (`um`, `uh`, `basically`, `like`).
- **Engineering Tradeoffs & Metrics (25 pts)**: P99 latency impact, memory/CPU tradeoffs, scale, failure modes, and testability.

### 4. Exemplary Senior Engineer Model Answers
- Compares your response against a recruiter-approved Staff Engineer model answer for every question.
- Delivers granular "What went well" feedback and actionable missing points.

### 5. Exportable Interview Performance Audit
- 1-click download of a complete, professionally formatted PDF audit report summarizing overall scores, competency breakdowns, and question-by-question critiques.

---

## LeetCode Coach & Algorithmic Diagnostic

The **LeetCode Coach** delivers deep algorithmic skill diagnostics, blind-spot detection, curated company roadmaps, and code complexity audits to help candidates ace technical coding rounds:

### 1. Multi-Mode Ingestion & Public GraphQL Ingestion
- **Live LeetCode Sync**: Ingests real-time problem-solving statistics, difficulty distributions, and topic submissions via the public LeetCode GraphQL API.
- **Offline / Manual Fallback**: Allows candidates to manually configure solve counts or test sample profiles (e.g. *FAANG Ready (520+)*, *Mid-Level (220+)*, *Beginner (45+)*) without internet access.

### 2. Algorithmic Readiness Score (0–100)
Evaluates candidate problem-solving breadth and depth across **5 weighted dimensions**:
- **Volume & Breadth (30 pts)**: Total solved count, difficulty weighting (Easy=1x, Medium=2.5x, Hard=5x).
- **8-Pillar Algorithmic Balance (25 pts)**: Distribution across core DSA categories to prevent over-indexing on simple arrays.
- **Advanced Data Structures (20 pts)**: Mastery of Graph Theory, Dynamic Programming, Trees, and Tries.
- **Difficulty Ratio (15 pts)**: Ratio of Medium and Hard problems vs. total solved (target: $\ge 60\%$).
- **Contest & Global Standing (10 pts)**: Global ranking percentile and contest performance.

### 3. 8-Pillar Topic Radar & Blind-Spot Detection
- Visualizes mastery across the **8 fundamental interview pillars**:
  - *Arrays & Hashing*
  - *Two Pointers & Sliding Window*
  - *Linked Lists, Stacks & Queues*
  - *Binary Search & Divide/Conquer*
  - *Trees & Binary Search Trees*
  - *Graphs, BFS & DFS*
  - *Dynamic Programming & Greedy*
  - *Backtracking, Bit Manipulation & Math*
- Identifies **Strongest Foundations** and pinpoints **Vulnerable Blind Spots** with actionable advice.

### 4. Curated Company Placement Roadmaps
- **FAANG 75**: High-frequency, high-yield patterns covering the core 75 questions asked at Meta, Google, Amazon, and Apple.
- **FinTech & Low-Latency Systems**: Priority focus on binary trees, graph algorithms, bit manipulation, and optimal cache-friendly data structures.
- **Placement Sprint (Last 30 Days)**: High-yield medium problems to rapidly eliminate candidate blind spots before interview season.
- Automatically prioritizes questions targeting the candidate's diagnosed weakest pillars.

### 5. AI Code Complexity & Pattern Optimizer
- Evaluates submitted code snippets for **Time & Space Complexity** ($O(N)$, $O(N \log N)$, $O(N^2)$, etc.).
- Offline heuristic AST & pattern analyzer detects nested loops, recursion depth, auxiliary memory allocations, and sorting calls.
- Google Gemini AI mode provides clean asymptotic derivation, code review notes, and optimal implementations.

### 6. Exportable Algorithmic Audit Report (PDF)
- 1-click download of a publication-grade PDF report generated via `fpdf2`, featuring overall score badge, 8-pillar mastery bars, key blind spots, and personalized roadmap problems.

---

## Placement Readiness Dashboard

The **Placement Readiness Dashboard** serves as the central command center for software engineering candidates, synthesizing all career dimensions into a unified readiness index, milestone sprint planner, and job application pipeline:

### 1. Unified Engineering Readiness Score (ERS: 0–100)
Synthesizes candidate performance across **4 core pillars** (weighted 25% each by default or customizable):
- **Resume ATS & Keyword Alignment (25%)**: Evaluates keyword match, quantified bullet strength, and layout structure.
- **GitHub Portfolio Hygiene & Depth (25%)**: Evaluates open-source documentation, deployed demos, license badges, and language depth.
- **Mock Interview Delivery & STAR Structure (25%)**: Technical depth, architectural tradeoffs, speech pacing, and verbal filler density.
- **LeetCode Algorithmic Problem Solving (25%)**: 8-pillar DSA coverage, medium/hard problem volume, and asymptotic complexity intuition.
- Automatically handles partial sessions with neutral 50pt baselines while nudging candidates to run live diagnostics.

### 2. Company Tier Benchmarking & 4-Axis Polar Radar
- Compares candidate readiness against real hiring bars across 3 company tiers:
  - **Tier-1**: FAANG, Quant Trading, HFT, and Elite Tech Unicorns (min. ERS 82+).
  - **Tier-2**: High-Growth Product Unicorns and Mid-Tech Scaleups (min. ERS 70+).
  - **Tier-3**: Tech Services, Enterprise IT, and Growth Startups (min. ERS 52+).
- Visualizes candidate strengths vs. target tier standards on an interactive Plotly polar radar chart.

### 3. Placement Sprint Milestone Planner
- Live countdown timer to target campus or off-campus placement season.
- Trackable milestone checklists across 5 core categories:
  - *Resume & Branding* (ATS $\ge$ 80, Google XYZ bullets for top projects).
  - *GitHub & Portfolio* (3+ repos with live deployment URLs, OSI licenses, clean architecture docs).
  - *DSA & LeetCode* (150+ problems, Blind 75 / FAANG 75 core patterns, Graph & DP coverage).
  - *Mock Interviews* (3+ simulations with score $\ge$ 75, STAR format mastery, zero filler words).
  - *Applications & Referrals* (30 company tier list, 15+ alumni referral outreach, 25+ applications submitted).
- Dynamic progress bar, custom milestone creator, and persistent session state.

### 4. Application & Interview Pipeline Manager
- Full funnel tracking across 7 distinct hiring stages:
  - `Wishlist` $\rightarrow$ `Applied` $\rightarrow$ `OA / Screen` $\rightarrow$ `Technical Round` $\rightarrow$ `Final Round` $\rightarrow$ `Offer Received` $\rightarrow$ `Archived / Rejected`
- Funnel metrics calculating **Total Applications**, **Active Pipeline**, **Interview Callback Rate (%)**, and **Offer Conversion Rate (%)**.
- Pre-populated realistic sample pipeline (Google, Stripe, Datadog, Uber, Atlassian).
- 1-click stage updates, custom application creator, and CSV/JSON export & import.

### 5. Executive Placement Dossier (PDF Export)
- Publication-grade multi-page PDF generated via `fpdf2`.
- Includes overall ERS score badge, tier verdict, 4-pillar progress bars, strengths & bottleneck gap analysis, milestone sprint summary, and active job application table.

---

## Project Structure

```bash
DevPilot_AI/
├── app.py                      # Main landing page & module dashboard
├── requirements.txt            # Python dependencies
├── .env.example                # Example environment configuration
├── pages/
│   ├── 1_Resume_Analyzer.py    # Resume Analyzer UI & interactive workflows
│   ├── 2_GitHub_Analyzer.py    # GitHub Profile Analyzer & Recruiter Auditor
│   ├── 3_Mock_Interview.py     # AI Mock Interview simulator & audio coach
│   ├── 4_LeetCode_Coach.py     # LeetCode Coach & Algorithmic Diagnostic UI
│   └── 5_Placement_Dashboard.py# Placement Readiness Dashboard & Pipeline Manager
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py        # PDF, DOCX, TXT extraction & section detection
│   ├── ats_scorer.py           # ATS scoring algorithm (TF-IDF & heuristics)
│   ├── keyword_extractor.py    # RAKE, spaCy & 200+ Tech skills taxonomy
│   ├── bullet_enhancer.py      # Rule-based, Gemini XYZ, and T5 enhancers
│   ├── github_fetcher.py       # GitHub REST API v3 data ingestion & statistics
│   ├── github_scorer.py        # 0–100 Portfolio readiness scoring & diagnostics
│   ├── github_ai_reviewer.py   # Gemini AI portfolio coach & resume bullet generator
│   ├── interview_coach.py      # Question generator, speech analyzer & answer rubric
│   ├── leetcode_coach.py       # LeetCode GraphQL fetcher, 8-pillar auditor & complexity engine
│   ├── placement_tracker.py    # Unified ERS score, milestone planner & pipeline analytics
│   ├── pdf_generator.py        # Professional PDF report exporter (fpdf2)
│   ├── sidebar.py              # Shared sidebar navigation & session scorecards
│   └── gemini_client.py        # Google Gemini API connector
├── tests/
│   ├── test_ats_scorer.py      # ATS scoring unit & integration tests
│   ├── test_github_scorer.py   # GitHub audit & portfolio scoring tests
│   ├── test_interview_coach.py # Mock interview question & rubric evaluation tests
│   ├── test_leetcode_coach.py  # LeetCode auditor, radar, roadmap & complexity tests
│   ├── test_placement_tracker.py # Placement readiness, milestone & pipeline tests
│   └── test_resume_parser.py   # Text extraction & section parsing tests
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
Copy `.env.example` to `.env` or create a `.env` file in the root directory:
```bash
# Windows PowerShell:
Copy-Item .env.example .env

# macOS / Linux:
cp .env.example .env
```
Configure your keys inside `.env`:
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
- [x] **v2.0**: AI Mock Interview (Resume-tailored questions, audio recording & transcription, 4-dimension scoring, pacing analysis, PDF export)
- [x] **v2.5**: LeetCode Algorithmic Coach & Placement Readiness Tracker
- [x] **v3.0**: Placement Readiness Dashboard & Application Pipeline Manager
- [x] **v3.0.1**: Patch Release — UI bug fixes in GitHub health audit & placement pipeline rendering, HTML sanitization, and configuration documentation

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

