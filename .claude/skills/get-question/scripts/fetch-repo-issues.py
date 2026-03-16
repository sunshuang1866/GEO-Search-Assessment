#!/usr/bin/env python3
"""Fetch top issues from a GitCode repository.

Usage:
    python3 fetch-repo-issues.py --owner <org> --repo <name> --limit 50
    python3 fetch-repo-issues.py --owner <org> --repo <name> --limit 50 --state all

Requires GITCODE_TOKEN environment variable or --token flag.
Output: JSON array of issues to stdout, errors to stderr.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.gitcode.com/api/v5"


def fetch_json(url: str, token: str) -> dict | list:
    """Fetch JSON from GitCode API with token auth."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "private-token": token,
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        if e.code == 404 and "token not found" in body.lower():
            print(
                f"HTTP 404: GitCode token is invalid or not found. "
                f"Please regenerate GITCODE_TOKEN at gitcode.com/profile/personal_access_tokens",
                file=sys.stderr,
            )
        elif e.code == 403:
            print(
                f"HTTP 403: GitCode token lacks required permissions (needs 'read_repository' scope). "
                f"Please check token scopes at gitcode.com/profile/personal_access_tokens",
                file=sys.stderr,
            )
        else:
            print(f"HTTP {e.code} fetching {url}: {body}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e.reason}", file=sys.stderr)
        raise


def fetch_issues(owner: str, repo: str, token: str, limit: int,
                 state: str = "all", sort: str = "created",
                 direction: str = "desc") -> list[dict]:
    """Fetch issues from GitCode API with pagination."""
    issues = []
    page = 1
    per_page = min(limit, 100)

    while len(issues) < limit:
        url = (
            f"{API_BASE}/repos/{owner}/{repo}/issues"
            f"?state={state}&sort={sort}&direction={direction}"
            f"&page={page}&per_page={per_page}"
        )
        data = fetch_json(url, token)
        if not data:
            break
        issues.extend(data)
        if len(data) < per_page:
            break
        page += 1

    return issues[:limit]


def normalize_issue(issue: dict) -> dict:
    """Extract relevant fields from a GitCode issue object."""
    labels = issue.get("labels", [])
    label_names = []
    if isinstance(labels, list):
        for label in labels:
            if isinstance(label, dict):
                label_names.append(label.get("name", ""))
            elif isinstance(label, str):
                label_names.append(label)

    return {
        "id": issue.get("id") or issue.get("number"),
        "number": issue.get("number"),
        "title": issue.get("title", ""),
        "state": issue.get("state", ""),
        "labels": label_names,
        "comments": issue.get("comments", 0),
        "created_at": issue.get("created_at", ""),
        "updated_at": issue.get("updated_at", ""),
        "html_url": issue.get("html_url", ""),
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch issues from GitCode")
    parser.add_argument("--owner", required=True, help="Repo owner/org")
    parser.add_argument("--repo", required=True, help="Repo name")
    parser.add_argument("--limit", type=int, default=50, help="Max issues to return")
    parser.add_argument("--state", default="all", choices=["open", "closed", "all"],
                        help="Issue state filter")
    parser.add_argument("--sort", default="created", choices=["created", "updated"],
                        help="Sort field")
    parser.add_argument("--token", default=None, help="GitCode API token (or set GITCODE_TOKEN env)")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITCODE_TOKEN", "")
    if not token:
        print(
            "ERROR: GitCode API requires authentication. "
            "Set GITCODE_TOKEN in .env or pass --token.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Fetching issues from {args.owner}/{args.repo} (state={args.state}, limit={args.limit})...",
          file=sys.stderr)

    issues = fetch_issues(args.owner, args.repo, token, args.limit, args.state, args.sort)

    # Normalize and sort by comments (engagement)
    results = [normalize_issue(i) for i in issues]
    results.sort(key=lambda i: i["comments"], reverse=True)

    print(f"Fetched {len(results)} issues", file=sys.stderr)
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
