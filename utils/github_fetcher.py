"""
🐙 GitHub Fetcher Utility — DevPilot AI
Fetches GitHub user profiles, repositories, language statistics, and repo health metrics
using GitHub REST API v3 with optional Personal Access Token (PAT) support.
"""

from typing import Dict, List, Any, Optional
import requests
import base64
import os
from datetime import datetime

GITHUB_API_BASE = "https://api.github.com"


def _get_headers(token: Optional[str] = None) -> Dict[str, str]:
    """Build request headers with optional authentication."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "DevPilot-AI-Dashboard",
    }
    # Priority: explicitly passed token -> environment variable
    auth_token = token or os.getenv("GITHUB_TOKEN")
    if auth_token and auth_token.strip():
        headers["Authorization"] = f"token {auth_token.strip()}"
    return headers


def get_user_profile(username: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch public profile metadata for a given GitHub username.
    Returns profile dict or raises an exception with a user-friendly message.
    """
    clean_username = username.strip()
    if not clean_username:
        raise ValueError("GitHub username cannot be empty.")

    url = f"{GITHUB_API_BASE}/users/{clean_username}"
    response = requests.get(url, headers=_get_headers(token), timeout=12)

    # Check rate limit info
    rate_limit_remaining = response.headers.get("X-RateLimit-Remaining")
    
    if response.status_code == 200:
        data = response.json()
        data["_rate_limit_remaining"] = rate_limit_remaining
        return data
    elif response.status_code == 404:
        raise ValueError(f"GitHub user '{clean_username}' was not found. Please check the username spelling.")
    elif response.status_code == 403:
        raise PermissionError(
            "GitHub API rate limit exceeded. Please provide a GitHub Personal Access Token (PAT) "
            "in the sidebar to unlock 5,000 requests/hour."
        )
    else:
        raise RuntimeError(f"GitHub API returned error ({response.status_code}): {response.text}")


def get_user_repos(
    username: str,
    token: Optional[str] = None,
    max_repos: int = 100,
) -> List[Dict[str, Any]]:
    """
    Fetch public repositories for a given GitHub user (sorted by most recently updated).
    """
    clean_username = username.strip()
    url = f"{GITHUB_API_BASE}/users/{clean_username}/repos"
    params = {
        "per_page": min(max_repos, 100),
        "sort": "updated",
        "direction": "desc",
        "type": "all",
    }
    
    response = requests.get(url, headers=_get_headers(token), params=params, timeout=15)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return []
    elif response.status_code == 403:
        raise PermissionError("GitHub API rate limit exceeded while fetching repositories.")
    else:
        raise RuntimeError(f"Failed to fetch repositories ({response.status_code}).")


def get_repo_languages(
    owner: str,
    repo_name: str,
    token: Optional[str] = None,
) -> Dict[str, int]:
    """
    Fetch byte breakdown of programming languages for a specific repository.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/languages"
    try:
        response = requests.get(url, headers=_get_headers(token), timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {}


def get_repo_readme_preview(
    owner: str,
    repo_name: str,
    token: Optional[str] = None,
    max_length: int = 1500,
) -> Optional[str]:
    """
    Fetch and decode the raw README content of a repository if present.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo_name}/readme"
    headers = _get_headers(token)
    headers["Accept"] = "application/vnd.github.v3.raw"
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            content = response.text
            return content[:max_length] if len(content) > max_length else content
    except Exception:
        pass
    return None


def fetch_complete_github_data(
    username: str,
    token: Optional[str] = None,
    fetch_top_repo_languages: bool = True,
) -> Dict[str, Any]:
    """
    Convenience orchestrator: Fetches profile, repos, aggregated language breakdown,
    and detailed metrics for analysis.
    """
    profile = get_user_profile(username, token=token)
    repos = get_user_repos(username, token=token)

    # Separate original vs forked repos
    original_repos = [r for r in repos if not r.get("fork", False)]
    forked_repos = [r for r in repos if r.get("fork", False)]

    # Calculate overall language statistics
    language_bytes_agg: Dict[str, int] = {}
    language_repo_counts: Dict[str, int] = {}

    # Gather languages from top repos (up to 15 original repos to respect rate limits)
    repos_to_inspect = original_repos[:15] if fetch_top_repo_languages else []
    for r in repos_to_inspect:
        repo_name = r.get("name", "")
        langs = get_repo_languages(username, repo_name, token=token)
        for lang, byte_count in langs.items():
            language_bytes_agg[lang] = language_bytes_agg.get(lang, 0) + byte_count

    # Fallback to repo primary language if byte-level API is sparse
    if not language_bytes_agg:
        for r in original_repos:
            prim_lang = r.get("language")
            if prim_lang:
                language_bytes_agg[prim_lang] = language_bytes_agg.get(prim_lang, 0) + (r.get("size", 10) * 1024)

    for r in original_repos:
        prim_lang = r.get("language")
        if prim_lang:
            language_repo_counts[prim_lang] = language_repo_counts.get(prim_lang, 0) + 1

    # Aggregate key stats
    total_stars = sum(r.get("stargazers_count", 0) for r in original_repos)
    total_forks = sum(r.get("forks_count", 0) for r in original_repos)
    total_open_issues = sum(r.get("open_issues_count", 0) for r in original_repos)
    repos_with_desc = sum(1 for r in original_repos if r.get("description") and len(r["description"].strip()) > 8)
    repos_with_license = sum(1 for r in original_repos if r.get("license"))
    repos_with_homepage = sum(1 for r in original_repos if r.get("homepage") and r["homepage"].strip().startswith("http"))
    repos_with_topics = sum(1 for r in original_repos if r.get("topics") and len(r["topics"]) > 0)

    # Sort top original repos by stars, then updated_at
    top_repos = sorted(
        original_repos,
        key=lambda x: (x.get("stargazers_count", 0), x.get("updated_at", "")),
        reverse=True,
    )

    return {
        "profile": profile,
        "all_repos": repos,
        "original_repos": original_repos,
        "forked_repos": forked_repos,
        "top_repos": top_repos,
        "language_bytes": language_bytes_agg,
        "language_repo_counts": language_repo_counts,
        "stats": {
            "total_public_repos": len(repos),
            "original_repo_count": len(original_repos),
            "forked_repo_count": len(forked_repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_open_issues": total_open_issues,
            "repos_with_description": repos_with_desc,
            "repos_with_license": repos_with_license,
            "repos_with_homepage": repos_with_homepage,
            "repos_with_topics": repos_with_topics,
        },
    }
