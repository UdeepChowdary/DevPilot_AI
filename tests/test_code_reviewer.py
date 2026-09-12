"""
Tests for utils/code_reviewer.py
Covers: language detection, bug pattern matching, code smell detection,
complexity estimation, heuristic analysis, and the review_code() entry point.
"""

import pytest
from utils.code_reviewer import (
    detect_language_from_filename,
    analyze_code_heuristic,
    estimate_complexity,
    review_code,
    SUPPORTED_LANGUAGES,
)


# ─── detect_language_from_filename ───────────────────────────────────────────

class TestDetectLanguageFromFilename:
    @pytest.mark.parametrize("filename,expected", [
        ("app.py",    "python"),
        ("index.js",  "javascript"),
        ("main.ts",   "typescript"),
        ("Main.java", "java"),
        ("server.go", "go"),
        ("main.cpp",  "cpp"),
        ("main.cc",   "cpp"),
        ("main.cxx",  "cpp"),
        ("lib.rs",    "rust"),
    ])
    def test_known_extensions(self, filename, expected):
        assert detect_language_from_filename(filename) == expected

    def test_unknown_extension_returns_none(self):
        assert detect_language_from_filename("Makefile") is None

    def test_no_extension_returns_none(self):
        assert detect_language_from_filename("README") is None

    def test_case_insensitive_extension(self):
        assert detect_language_from_filename("App.PY") == "python"


# ─── estimate_complexity ──────────────────────────────────────────────────────

class TestEstimateComplexity:
    def test_no_loops_constant_or_log(self):
        result = estimate_complexity("x = 1\ny = 2", "python")
        assert result["max_loop_nesting"] == 0
        tc = result["time_complexity"]
        assert "O(1)" in tc or "O(log" in tc

    def test_single_loop_linear(self):
        result = estimate_complexity("for i in range(n):\n    print(i)", "python")
        assert result["max_loop_nesting"] >= 1
        assert "O(n)" in result["time_complexity"]

    def test_double_loop_quadratic(self):
        code = "for i in range(n):\n    for j in range(n):\n        pass"
        result = estimate_complexity(code, "python")
        assert result["max_loop_nesting"] >= 2
        assert "O(n\u00b2)" in result["time_complexity"]

    def test_triple_loop_cubic(self):
        code = ("for i in range(n):\n"
                "    for j in range(n):\n"
                "        for k in range(n):\n"
                "            pass")
        result = estimate_complexity(code, "python")
        assert result["max_loop_nesting"] >= 3
        assert "O(n\u00b3)" in result["time_complexity"]

    def test_cyclomatic_grows_with_branches(self):
        s = estimate_complexity("x = 1", "python")["cyclomatic_complexity"]
        b = estimate_complexity(
            "if a:\n    pass\nelif b:\n    pass\nfor x in y:\n    pass",
            "python"
        )["cyclomatic_complexity"]
        assert b > s

    def test_has_required_keys(self):
        result = estimate_complexity("x = 1", "python")
        for key in ["cyclomatic_complexity", "max_loop_nesting", "time_complexity",
                    "space_complexity", "complexity_rating", "complexity_note",
                    "line_count", "branch_points"]:
            assert key in result

    def test_line_count_skips_blanks(self):
        assert estimate_complexity("x = 1\n\ny = 2\n\nz = 3", "python")["line_count"] == 3


# ─── Python bug detection ─────────────────────────────────────────────────────

class TestHeuristicPythonBugs:
    def _ids(self, code):
        return [b["id"] for b in analyze_code_heuristic(code, "python")["bugs"]]

    def test_hardcoded_secret(self):
        assert "hardcoded_secret" in self._ids('api_key = "sk-abc123def456"')

    def test_bare_except(self):
        assert "bare_except" in self._ids("try:\n    pass\nexcept:\n    pass")

    def test_mutable_default_arg(self):
        assert "mutable_default_arg" in self._ids("def foo(items=[]):\n    return items")

    def test_print_in_prod(self):
        assert "print_in_prod" in self._ids("def f():\n    print('x')\n    return 1")

    def test_eval_exec(self):
        assert "eval_exec" in self._ids("result = eval(user_input)")

    def test_todo_fixme(self):
        assert "todo_fixme" in self._ids("# TODO: fix this\nx = 1")

    def test_clean_code_no_bugs(self):
        code = "import os\n\ndef key():\n    return os.environ['KEY']\n"
        assert analyze_code_heuristic(code, "python")["bugs"] == []

    def test_bugs_deduplicated(self):
        code = 'password = "abc123xyz"\npassword = "abc123xyz"'
        result = analyze_code_heuristic(code, "python")
        pairs = [(b["id"], b["line"]) for b in result["bugs"]]
        assert len(pairs) == len(set(pairs))

    def test_bug_required_fields(self):
        result = analyze_code_heuristic('api_key = "supersecret123"', "python")
        for bug in result["bugs"]:
            for field in ["id", "severity", "category", "message", "line"]:
                assert field in bug


# ─── JS / TS bugs ─────────────────────────────────────────────────────────────

class TestHeuristicJavaScriptBugs:
    def test_console_log(self):
        r = analyze_code_heuristic("function f() { console.log('x'); }", "javascript")
        assert "console_log" in [b["id"] for b in r["bugs"]]

    def test_eval_js(self):
        r = analyze_code_heuristic("const r = eval(input);", "javascript")
        assert "eval_usage" in [b["id"] for b in r["bugs"]]

    def test_typescript_inherits_js(self):
        # TS inherits JS patterns; use keyword=value assignment that the regex matches
        r = analyze_code_heuristic('const token = "sk-abc123secret456abc"', "typescript")
        assert "hardcoded_secret" in [b["id"] for b in r["bugs"]]


# ─── Java bugs ────────────────────────────────────────────────────────────────

class TestHeuristicJavaBugs:
    def test_empty_catch(self):
        r = analyze_code_heuristic("try { risky(); } catch (Exception e) { }", "java")
        assert "empty_catch" in [b["id"] for b in r["bugs"]]

    def test_system_exit(self):
        r = analyze_code_heuristic("public void stop() { System.exit(0); }", "java")
        assert "system_exit" in [b["id"] for b in r["bugs"]]


# ─── Rust bugs ────────────────────────────────────────────────────────────────

class TestHeuristicRustBugs:
    def test_unwrap(self):
        r = analyze_code_heuristic("let x = some_result.unwrap();", "rust")
        assert "unwrap_overuse" in [b["id"] for b in r["bugs"]]

    def test_todo_macro(self):
        r = analyze_code_heuristic("fn process() -> i32 { todo!() }", "rust")
        assert "todo_panic" in [b["id"] for b in r["bugs"]]


# ─── C++ bugs ─────────────────────────────────────────────────────────────────

class TestHeuristicCppBugs:
    def test_raw_new(self):
        r = analyze_code_heuristic("int* ptr = new int(42);", "cpp")
        assert "raw_pointer" in [b["id"] for b in r["bugs"]]

    def test_gets(self):
        r = analyze_code_heuristic("gets(buffer);", "cpp")
        assert "scanf_gets" in [b["id"] for b in r["bugs"]]


# ─── Code Smells ──────────────────────────────────────────────────────────────

class TestCodeSmells:
    def test_deep_nesting(self):
        code = ("def f():\n"
                "    if True:\n"
                "        if True:\n"
                "            if True:\n"
                "                if True:\n"
                "                    if True:\n"
                "                        x = 1")
        result = analyze_code_heuristic(code, "python")
        assert "Deep Nesting" in [s["type"] for s in result["smells"]]

    def test_duplicate_lines(self):
        code = "x = some_long_expression()\n" * 3
        result = analyze_code_heuristic(code, "python")
        assert "Duplicate Code" in [s["type"] for s in result["smells"]]

    def test_clean_no_smells(self):
        result = analyze_code_heuristic("def add(a, b):\n    return a + b\n", "python")
        assert len(result["smells"]) == 0


# ─── Summary & Suggestions ────────────────────────────────────────────────────

class TestSummaryAndSuggestions:
    def test_critical_red_summary(self):
        result = analyze_code_heuristic('password = "supersecretpassword123"', "python")
        assert "\U0001f534" in result["summary"] or "critical" in result["summary"].lower()

    def test_clean_green_summary(self):
        result = analyze_code_heuristic(
            "def add(a: int, b: int) -> int:\n    return a + b\n", "python"
        )
        assert "\u2705" in result["summary"] or "clean" in result["summary"].lower()

    def test_suggestions_always_present(self):
        result = analyze_code_heuristic("x = 1", "python")
        assert len(result["suggestions"]) >= 1

    def test_secret_suggestion_env_hint(self):
        result = analyze_code_heuristic('api_key = "sk-abc123def456secret"', "python")
        txt = " ".join(result["suggestions"]).lower()
        assert "environment" in txt or "dotenv" in txt or "secret" in txt


# ─── review_code entry point ──────────────────────────────────────────────────

class TestReviewCode:
    def test_empty_code_early_return(self):
        result = review_code("", "python")
        assert result["bugs"] == []
        assert result["language"] == "python"

    def test_whitespace_only_early_return(self):
        result = review_code("   \n   ", "python")
        assert result["bugs"] == []

    def test_no_api_key_heuristic(self):
        assert review_code("x = 1", "python")["is_ai_generated"] is False

    def test_blank_api_key_heuristic(self):
        assert review_code("x = 1", "python", api_key="  ")["is_ai_generated"] is False

    def test_result_has_required_keys(self):
        result = review_code("def f(): pass", "python")
        for key in ["bugs", "smells", "complexity", "suggestions", "summary", "language"]:
            assert key in result

    def test_javascript_review(self):
        result = review_code("function f() { console.log('hi'); }", "javascript")
        assert result["language"] == "javascript"
        assert "console_log" in [b["id"] for b in result["bugs"]]

    def test_severity_values_valid(self):
        code = 'password = "abc123"\ntry:\n    pass\nexcept:\n    pass'
        for bug in review_code(code, "python")["bugs"]:
            assert bug["severity"] in {"critical", "warning", "info"}

    @pytest.mark.parametrize("lang", list(SUPPORTED_LANGUAGES.keys()))
    def test_all_supported_languages(self, lang):
        assert review_code("x = 1", lang)["language"] == lang
