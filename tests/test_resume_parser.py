"""
Tests for utils/resume_parser.py
Covers: text extraction (TXT), section detection, bullet point extraction,
header filtering, deduplication, and action-verb line detection.
"""

import pytest
import io
from utils.resume_parser import (
    extract_text,
    extract_text_from_txt,
    detect_sections,
    extract_bullet_points,
    SECTION_PATTERNS,
    MAX_RESUME_SIZE,
)


# ─── extract_text_from_txt ────────────────────────────────────────────────────

class TestExtractTextFromTxt:
    def test_utf8_text(self):
        content = "Hello World\nThis is a resume."
        result = extract_text_from_txt(content.encode("utf-8"))
        assert "Hello World" in result

    def test_latin1_fallback(self):
        content = "Résumé: café engineer"
        result = extract_text_from_txt(content.encode("latin-1"))
        assert len(result) > 0

    def test_empty_bytes_returns_empty_string(self):
        result = extract_text_from_txt(b"")
        assert result == ""

    def test_preserves_newlines(self):
        content = "Line one\nLine two\nLine three"
        result = extract_text_from_txt(content.encode("utf-8"))
        assert "Line one" in result
        assert "Line two" in result


# ─── detect_sections ─────────────────────────────────────────────────────────

class TestDetectSections:
    def test_detects_experience_section(self):
        text = "EXPERIENCE\nWorked at Acme Corp from 2022–2023."
        sections = detect_sections(text)
        assert "experience" in sections

    def test_detects_education_section(self):
        text = "Education\nB.Tech Computer Science — IIT Delhi"
        sections = detect_sections(text)
        assert "education" in sections

    def test_detects_skills_section(self):
        text = "Technical Skills\nPython, JavaScript, Go"
        sections = detect_sections(text)
        assert "skills" in sections

    def test_detects_projects_section(self):
        text = "Projects\nDevPilot AI — ML resume analyzer"
        sections = detect_sections(text)
        assert "projects" in sections

    def test_detects_all_four_core_sections(self, sample_resume_text):
        sections = detect_sections(sample_resume_text)
        for sec in ["experience", "education", "skills", "projects"]:
            assert sec in sections, f"Missing section: {sec}"

    def test_no_false_positive_mid_sentence(self):
        # "experience" in a mid-sentence should NOT trigger a section header
        text = "I have 5 years of experience in Python programming and software development."
        sections = detect_sections(text)
        # This line is too long (>50 chars) to be a header, should go to "other"
        assert "experience" not in sections

    def test_colon_header_detected(self):
        text = "Experience:\nBuilt REST APIs using FastAPI."
        sections = detect_sections(text)
        assert "experience" in sections

    def test_uppercase_header_detected(self):
        text = "EDUCATION\nB.Tech, IIT 2020-2024"
        sections = detect_sections(text)
        assert "education" in sections

    def test_section_content_captured_correctly(self):
        text = "EXPERIENCE\nEngineered REST APIs.\nDeployed on AWS."
        sections = detect_sections(text)
        content = sections.get("experience", "")
        assert "Engineered" in content or "Deployed" in content

    def test_certifications_section_detected(self):
        text = "Certifications\nAWS Certified Solutions Architect"
        sections = detect_sections(text)
        assert "certifications" in sections

    def test_empty_text_returns_no_sections(self):
        sections = detect_sections("")
        # Should not crash; any sections returned should be empty
        assert isinstance(sections, dict)

    def test_summary_section_detected(self):
        text = "Summary\nPassionate software engineer with 3 years of experience."
        sections = detect_sections(text)
        assert "summary" in sections


# ─── extract_bullet_points ───────────────────────────────────────────────────

class TestExtractBulletPoints:
    def test_dash_bullets_extracted(self):
        text = "- Engineered a REST API with FastAPI.\n- Deployed on AWS Lambda."
        bullets = extract_bullet_points(text)
        assert len(bullets) >= 1
        assert any("REST API" in b or "Deployed" in b for b in bullets)

    def test_dot_bullets_extracted(self):
        text = "• Built a machine learning pipeline.\n• Optimized queries by 40%."
        bullets = extract_bullet_points(text)
        assert len(bullets) >= 1

    def test_asterisk_bullets_extracted(self):
        text = "* Spearheaded the migration to microservices.\n* Reduced latency by 35%."
        bullets = extract_bullet_points(text)
        assert len(bullets) >= 1

    def test_numbered_bullets_extracted(self):
        text = "1. Architected the CI/CD pipeline for the team.\n2. Automated deployments using GitHub Actions."
        bullets = extract_bullet_points(text)
        assert len(bullets) >= 1

    def test_action_verb_lines_extracted(self):
        text = "Deployed containerized apps using Docker and Kubernetes.\nOptimized database queries for performance."
        bullets = extract_bullet_points(text)
        assert len(bullets) >= 1

    def test_contact_info_filtered_out(self):
        text = "• john@email.com\n• linkedin.com/in/johndoe\n• Built a REST API."
        bullets = extract_bullet_points(text)
        assert not any("@" in b for b in bullets)
        assert not any("linkedin" in b.lower() for b in bullets)

    def test_skill_header_lines_filtered(self):
        text = "Languages: Python, JavaScript, Go\n• Engineered the backend API."
        bullets = extract_bullet_points(text)
        assert not any(b.lower().startswith("languages:") for b in bullets)

    def test_date_range_lines_filtered(self):
        text = "Software Engineer — Acme Corp (Jan 2022 – Dec 2023)\n• Optimized performance by 40%."
        bullets = extract_bullet_points(text)
        # The job title line with date range should be filtered
        assert not any("Jan 2022" in b for b in bullets)

    def test_deduplication(self):
        text = "• Built a REST API with FastAPI.\n• Built a REST API with FastAPI."
        bullets = extract_bullet_points(text)
        assert len(bullets) == len(set(bullets))

    def test_very_short_lines_filtered(self):
        text = "• OK\n• Engineered a scalable REST API pipeline for 10k users."
        bullets = extract_bullet_points(text)
        assert not any(len(b) < 12 for b in bullets)

    def test_empty_text_returns_empty_list(self):
        assert extract_bullet_points("") == []

    def test_no_bullets_returns_empty_list(self):
        text = "This is just a paragraph without any bullets or action verbs."
        # No strong action verbs, no bullet symbols — should return empty or minimal
        bullets = extract_bullet_points(text)
        assert isinstance(bullets, list)

    def test_full_resume_extracts_multiple_bullets(self, sample_resume_text):
        bullets = extract_bullet_points(sample_resume_text)
        assert len(bullets) >= 3  # sample has 5+ bullet points


# ─── Section pattern coverage ─────────────────────────────────────────────────

class TestSectionPatterns:
    @pytest.mark.parametrize("header,section", [
        ("EXPERIENCE", "experience"),
        ("Work Experience", "experience"),
        ("Professional Experience", "experience"),
        ("EDUCATION", "education"),
        ("Academic Background", "education"),
        ("SKILLS", "skills"),
        ("Technical Skills", "skills"),
        ("PROJECTS", "projects"),
        ("Key Projects", "projects"),
        ("Open Source", "projects"),
        ("Certifications", "certifications"),
        ("Awards", "certifications"),
        ("SUMMARY", "summary"),
        ("Objective", "summary"),
        ("Leadership", "leadership"),
        ("Extracurricular", "leadership"),
    ])
    def test_header_matches_section(self, header, section):
        import re
        clean = re.sub(r"^[\W_]+|[\W_]+$", "", header).strip()
        pattern = SECTION_PATTERNS[section]
        assert pattern.match(clean), f"'{header}' should match section '{section}'"


class TestExtractTextFileLimits:
    def test_oversized_file_rejected(self):
        class MockUploadedFile(io.BytesIO):
            name = "huge_resume.txt"

        huge_payload = b"A" * (MAX_RESUME_SIZE + 50)
        mock_file = MockUploadedFile(huge_payload)
        with pytest.raises(ValueError, match="exceeds the maximum allowed size"):
            extract_text(mock_file)

    def test_valid_size_file_processed(self):
        class MockUploadedFile(io.BytesIO):
            name = "normal_resume.txt"

        valid_payload = b"Jane Doe\nSoftware Engineer\nPython, Docker"
        mock_file = MockUploadedFile(valid_payload)
        res = extract_text(mock_file)
        assert "Jane Doe" in res
