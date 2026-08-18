import streamlit as st

st.set_page_config(
    page_title="DevPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 DevPilot AI")
st.subheader("Your Personal Software Engineer Dashboard")

st.markdown("""
Welcome to **DevPilot AI**, your all-in-one AI-powered platform designed to help you prepare for software engineering placements and internships!

### 🌟 Core Modules Coming Soon:
- 📄 **Resume Analyzer**: Get ATS scoring, keyword optimization, and actionable feedback.
- 🐙 **GitHub Profile Analyzer**: Analyze your repository quality and commit consistency.
- 🧠 **LeetCode Coach**: Track your coding progress and identify weak topics.
- 🎤 **AI Mock Interview**: Practice technical and behavioral interviews based on your resume.
- 💻 **AI Code Reviewer**: Get automated bug detection and refactoring suggestions.
""")

st.info("👈 Modules will appear in the sidebar as they are built.")
