<div align="center">

```
      ██████╗ ███████╗██╗   ██╗██████╗ ██╗██╗      ██████╗ ████████╗     █████╗ ██╗
      ██╔══██╗██╔════╝██║   ██║██╔══██╗██║██║     ██╔═══██╗╚══██╔══╝    ██╔══██╗██║
      ██║  ██║█████╗  ██║   ██║██████╔╝██║██║     ██║   ██║   ██║       ███████║██║
      ██║  ██║██╔══╝  ╚██╗ ██╔╝██╔═══╝ ██║██║     ██║   ██║   ██║       ██╔══██║██║
      ██████╔╝███████╗ ╚████╔╝ ██║     ██║███████╗╚██████╔╝   ██║       ██║  ██║██║
      ╚═════╝ ╚══════╝  ╚═══╝  ╚═╝     ╚═╝╚══════╝ ╚═════╝    ╚═╝       ╚═╝  ╚═╝╚═╝
```

# 🚀 𝓓𝓮𝓿𝓟𝓲𝓵𝓸𝓽 • 𝓐𝓘
### *The Next-Gen Engineering Placement & Career Acceleration Dashboard*

<p align="center">
  <b>Empowering Software Engineers with ML-Powered ATS Optimization, Deep Career Analytics & AI Intelligence</b>
</p>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-1.5%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-10B981?style=for-the-badge)](https://github.com/UdeepChowdary/DevPilot_AI/pulls)

<p align="center">
  <a href="#-feature-spotlight-resume-analyzer"><b>📄 Resume Analyzer</b></a> •
  <a href="#-getting-started"><b>🚀 Quick Start</b></a> •
  <a href="#-modules-overview"><b>🌟 Modules</b></a> •
  <a href="#-project-structure"><b>🛠️ Architecture</b></a> •
  <a href="#-product-roadmap"><b>🗺️ Roadmap</b></a>
</p>

---

</div>

## 💡 About DevPilot AI

**DevPilot AI** is an all-in-one AI & NLP-powered suite built specifically for software engineering students and candidates preparing for top-tier tech internships and placement seasons. Instead of juggling disconnected tools or paying for subscription-gated resume checkers, DevPilot AI combines **100% offline heuristic ML engines** with optional **Google Gemini AI intelligence** to deliver actionable, transparent, and accurate career tools.

---

## 🌟 Modules Overview

| Module | Status | Core Technologies & Capabilities |
| :--- | :---: | :--- |
| 📄 **Resume Analyzer** | **✅ Live** | ATS scoring (0–100), layout-aware PDF/DOCX parsing, TF-IDF keyword match, 200+ skill taxonomy, Google XYZ bullet rewriter. |
| 🐙 **GitHub Profile Analyzer** | **✅ Live** | Portfolio readiness score (0–100), repo documentation & license audit, language byte breakdown, and AI resume bullets. |
| 💻 **AI Code Reviewer** | 🔜 Coming Soon | Automated bug detection, asymptotic time/space complexity analysis ($O(N)$), and architectural refactoring suggestions. |
| 🎤 **AI Mock Interview** | 🔜 Coming Soon | Resume-tailored behavioral & technical interview simulation with speech transcription and pacing critique. |
| 🧠 **LeetCode Coach** | 🔜 Coming Soon | Algorithmic topic radar, weak-pattern diagnostic, and automated weekly practice roadmaps. |
| 📊 **Placement Dashboard** | 🔜 Coming Soon | Consolidated readiness scorecard, milestone tracker, and application pipeline manager. |

---

## 📄 Feature Spotlight: Resume Analyzer

The **Resume Analyzer** combines machine learning text analytics, NLP parsing, and generative AI to deliver comprehensive resume critiques:

### 1. 📑 Multi-Format & Layout-Aware Parsing
- Supports **PDF**, Microsoft Word (**`.docx`**), and plain text (**`.txt`**).
- Implements topologically sorted block extraction via **PyMuPDF** to prevent text corruption on modern 2-column resume designs.
- Accurately detects and maps core resume sections (*Summary, Experience, Education, Skills, Projects, Certifications, Leadership*).

### 2. 📊 Normalized ATS Scoring Engine (0–100)
- **Keyword Alignment**: TF-IDF cosine similarity against target Job Descriptions (or vocabulary richness if no JD is provided).
- **Impact & Action Verbs**: Evaluates the density of high-impact engineering action verbs across both past and active tenses (*Spearheaded, Architected, Engineered, Optimized*).
- **Smart Metric Detection**: Identifies true quantified outcomes (%, $, latency in ms, scale in users/events) while filtering out false positives like graduation years and phone numbers.
- **Section & Format Completeness**: Evaluates structural integrity, word count conciseness (350–850 words), and contact information presence.

### 3. 🔑 Comprehensive 200+ Tech Skills Taxonomy
- Pre-built taxonomy covering languages, frontend, backend, databases, cloud, DevOps, AI/ML, and system design.
- Whitelists critical 1-2 letter skills (`Go`, `C`, `R`, `AI`, `ML`, `CI`, `CD`, `UI`, `UX`) to ensure short acronyms are never missed.
- Generates interactive **Matched vs. Missing Skills** chip visualizations and requirement coverage charts.

### 4. ✨ Multi-Engine Bullet Point Enhancer
- **⚡ Fast Rule-Based Mode**: Instant offline verb replacement and grammar cleanup (e.g. *"Helped to build"* $\rightarrow$ *"Constructed"* / *"Engineered"*).
- **🧠 Gemini AI Mode**: Leverages Google's **XYZ Formula** (*"Accomplished [X] as measured by [Y], by doing [Z]"*) to generate top-tier Silicon Valley recruiter-ready bullet rewrites.
- **🤖 Local T5 Mode**: Offline neural summarization and refinement via Hugging Face Transformers.
- **1-Click Copy Snippets**: Copy any enhanced bullet directly into your clipboard with a single click.

### 5. 📥 Exportable ATS Audit Report
- Generate and download a complete Markdown audit report summarizing overall scores, component breakdowns, strengths, areas for improvement, keyword gaps, and bullet rewrites.

---

## 🐙 Feature Spotlight: GitHub Profile Analyzer

The **GitHub Profile Analyzer** provides an in-depth, recruiter-grade audit of your open-source presence and repositories:

### 1. 📊 Normalized Developer Readiness Score (0–100)
- **Profile Completeness (15 pts)**: Bio, full name, organization, avatar, location, and linked external portfolio.
- **Repo Quality & Hygiene (35 pts)**: Original vs. forked project balance, description coverage, open-source licenses, topic tags, and live deployment URLs.
- **Activity & Consistency (25 pts)**: Push recency, active quarter maintenance, and multi-repo development cadence.
- **Tech Stack & Language Depth (15 pts)**: Core stack specialization vs. full-stack polyglot versatility.
- **Community Impact (10 pts)**: Star validation, forks, and developer following.

### 2. 🛠️ Repository-by-Repository Health Audit
- Automated hygiene check for individual projects with pass/fail badges for **READMEs**, **Descriptions**, **Open Source Licenses**, **Topic Tags**, and **Live Deployed Previews**.
- Actionable, custom recommendations for each repository to boost recruiter appeal.

### 3. 🧠 AI Recruiter Coach & Resume Bullets
- **30-Second Interview Elevator Pitch**: A polished verbal introduction script tailored to your GitHub projects.
- **Google XYZ Resume Bullets**: Automatically extracts technical context from your top repos and generates quantified resume bullets.
- **Strategic Capstone Recommender**: Diagnoses portfolio gaps (e.g. missing backend API or cloud deployment) and suggests high-impact next projects.

---

## 🛠️ Project Structure

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

## 🚀 Getting Started

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
*(Note: DevPilot AI can run 100% offline without an API key using built-in rule-based and local NLP heuristics!)*

### 4. Launch the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🗺️ Product Roadmap

- [x] **v1.0**: Resume Analyzer (ATS Scoring, Keyword Matching, Multi-engine Bullets, PDF/DOCX Support, Report Exporter)
- [x] **v1.1**: GitHub Profile Analyzer (Portfolio scoring, repo health audit, tech stack breakdown, AI resume bullets)
- [ ] **v1.5**: AI Code Reviewer (Static analysis, complexity calculation, refactoring tips)
- [ ] **v2.0**: AI Mock Interview (Resume-tailored questions, audio transcription, feedback)
- [ ] **v2.5**: LeetCode Algorithmic Coach & Placement Readiness Tracker

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
