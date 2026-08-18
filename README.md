# 🚀 DevPilot AI

**Your Personal Software Engineer Dashboard**

DevPilot AI is an all-in-one AI-powered platform designed to help software engineering students prepare for internships and placements. Instead of relying on multiple fragmented tools, DevPilot AI combines powerful analyzers, mock interviews, and learning roadmaps into a single polished SaaS-style application.

## ✨ Core Modules
- 📄 **Resume Analyzer**: ATS score analysis, keyword optimization, and action-oriented bullet point enhancement.
- 🐙 **GitHub Profile Analyzer**: Repository quality assessment, commit consistency analysis, language statistics, and project quality scoring.
- 🧠 **LeetCode Coach**: Track coding progress, identify weak topics, generate personalized practice plans, and predict interview readiness.
- 🎤 **AI Mock Interview**: Resume-based technical and behavioral interview practice with AI-generated feedback and communication analysis.
- 💻 **AI Code Reviewer**: Detect bugs and code smells, time/space complexity analysis, security recommendations, and refactoring suggestions.
- 📊 **Dashboards & Roadmaps**: Coding progress tracking, placement readiness scoring, and personalized weekly milestones.

## 🛠️ Tech Stack
- **Frontend / Deployment**: Streamlit & Streamlit Community Cloud
- **Backend**: Python
- **AI Models**: Google Gemini (or OpenAI GPT)
- **Database**: SQLite
- **Visualization**: Plotly
- **Speech Integration**: Whisper (Speech-to-Text), ElevenLabs (Text-to-Speech)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- An API Key for Google Gemini (or OpenAI)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/UdeepChowdary/DevPilot_AI.git
   cd DevPilot_AI
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   Create a `.env` file in the root directory and add your API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

## 🗺️ Roadmap
- **v1.0** – Resume Analyzer + GitHub Analyzer *(Current Focus)*
- **v1.5** – AI Code Reviewer
- **v2.0** – AI Mock Interview
- **v2.5** – LeetCode Coach
- **v3.0+** – System Design Mentor, Recruiter Dashboard, Team Collaboration & Leaderboards
