#!/usr/bin/env python3
"""Fetch top forum posts from MindSpore Discourse forum.

Usage:
    python3 fetch-forum-posts.py --community <name> --limit <N> [--api-url <url>]
    python3 fetch-forum-posts.py --community MindSpore --limit 50
    python3 fetch-forum-posts.py --community MindSpore --limit 50 --category help

Output: JSON array of posts to stdout, errors to stderr.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import urllib.parse

DEFAULT_API_URL = "https://discuss.mindspore.cn"

# Category slug → id mapping for MindSpore Discourse forum
CATEGORY_MAP = {
    "help": 4,           # 问题求助 (103 topics)
    "feedback": 2,       # 建议与反馈
    "tech": 15,          # 经验分享
    "activities": 14,    # 活动公告
    "mindspore-lite": 38,  # MindSpore Lite推理部署 (43 topics)
    "mindspore-transformers": 39,  # 大模型套件
    "mindspore-llm-inference-serving": 36,  # 大模型推理部署
}

# Categories to fetch by default (highest question density)
DEFAULT_CATEGORIES = ["help", "mindspore-lite"]


def fetch_json(url: str) -> dict:
    """Fetch JSON from a URL with error handling."""
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} fetching {url}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e.reason}", file=sys.stderr)
        raise


# Category IDs that contain real questions/issues (not blogs or announcements)
QUESTION_CATEGORY_IDS = {4, 38, 19, 20, 23}


def fetch_top_topics(base_url: str, limit: int) -> list[dict]:
    """Fetch top topics from /top.json, filtered to question-oriented categories."""
    topics = []
    page = 0
    while len(topics) < limit * 3:  # fetch extra to allow for filtering
        url = f"{base_url}/top.json?period=all&page={page}"
        data = fetch_json(url)
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            break
        # Filter to question-oriented categories only
        filtered = [t for t in topic_list if t.get("category_id") in QUESTION_CATEGORY_IDS]
        topics.extend(filtered)
        page += 1
        if page > 3:  # cap at 3 pages to avoid rate limits
            break
    return topics[:limit]


def fetch_category_topics(base_url: str, slug: str, category_id: int, limit: int) -> list[dict]:
    """Fetch top topics (sorted by views) from a specific category using /l/top endpoint."""
    topics = []
    page = 0
    while len(topics) < limit:
        url = f"{base_url}/c/{slug}/{category_id}/l/top.json?period=all&page={page}"
        data = fetch_json(url)
        topic_list = data.get("topic_list", {}).get("topics", [])
        if not topic_list:
            break
        topics.extend(topic_list)
        page += 1
        if page > 3:
            break
    return topics[:limit]


def normalize_topic(topic: dict) -> dict:
    """Extract relevant fields from a Discourse topic object."""
    return {
        "id": topic.get("id"),
        "title": topic.get("title", ""),
        "views": topic.get("views", 0),
        "reply_count": topic.get("reply_count", 0),
        "like_count": topic.get("like_count", 0),
        "posts_count": topic.get("posts_count", 0),
        "category_id": topic.get("category_id"),
        "tags": topic.get("tags", []),
        "has_accepted_answer": topic.get("has_accepted_answer", False),
        "pinned": topic.get("pinned", False),
        "closed": topic.get("closed", False),
        "created_at": topic.get("created_at", ""),
        "last_posted_at": topic.get("last_posted_at", ""),
    }


def fetch_posts(community: str, limit: int, api_url: str | None = None,
                category: str | None = None) -> list[dict]:
    """Fetch forum topics, deduplicate, sort by views, return top N."""
    base_url = (api_url or DEFAULT_API_URL).rstrip("/")

    all_topics = {}  # id → topic, for dedup

    if category:
        # Fetch from a specific category
        categories = [category]
    else:
        # Fetch from default high-value categories + global top
        categories = DEFAULT_CATEGORIES

    # Fetch from specified categories
    for slug in categories:
        cat_id = CATEGORY_MAP.get(slug)
        if cat_id is None:
            print(f"WARNING: Unknown category '{slug}', skipping.", file=sys.stderr)
            continue
        try:
            topics = fetch_category_topics(base_url, slug, cat_id, limit)
            for t in topics:
                all_topics[t["id"]] = t
            print(f"Fetched {len(topics)} topics from category '{slug}'", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Failed to fetch category '{slug}': {e}", file=sys.stderr)

    # Also fetch global top topics
    if not category:
        try:
            top_topics = fetch_top_topics(base_url, limit)
            for t in top_topics:
                all_topics[t["id"]] = t
            print(f"Fetched {len(top_topics)} global top topics", file=sys.stderr)
        except Exception as e:
            print(f"WARNING: Failed to fetch global top topics: {e}", file=sys.stderr)

    if not all_topics:
        print("ERROR: No topics fetched from any source.", file=sys.stderr)
        sys.exit(1)

    # Normalize, filter pinned/closed, sort by views
    results = []
    for topic in all_topics.values():
        normalized = normalize_topic(topic)
        if normalized["pinned"] or normalized["closed"]:
            continue
        results.append(normalized)

    results.sort(key=lambda t: t["views"], reverse=True)
    return results[:limit]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch forum posts from Discourse")
    parser.add_argument("--community", required=True, help="Community name")
    parser.add_argument("--limit", type=int, default=50, help="Max topics to return")
    parser.add_argument("--api-url", default=None, help="Forum base URL (default: discuss.mindspore.cn)")
    parser.add_argument("--category", default=None,
                        choices=list(CATEGORY_MAP.keys()),
                        help="Fetch from a specific category only")
    args = parser.parse_args()

    posts = fetch_posts(args.community, args.limit, args.api_url, args.category)
    print(json.dumps(posts, ensure_ascii=False, indent=2))
