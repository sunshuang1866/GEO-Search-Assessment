#!/usr/bin/env python3
"""Fetch MindSpore SIG mailing list email archives for question generation.

Two-step flow:
  1. Fetch SIG list from MagicAPI → extract mailing_list addresses per SIG
  2. Fetch email archives from HyperKitty API → thread subjects + email content

Data sources:
  - SIG list:    https://www.mindspore.cn/api-magicapi/sig/all/mindspore
  - Mail archive: https://mailweb.mindspore.cn/hyperkitty/api/list/{addr}/threads/
  - Email content: https://mailweb.mindspore.cn/archives/api/list/{addr}/email/{id}/

Usage:
    python3 fetch-sig-info.py --community MindSpore --limit 50
    python3 fetch-sig-info.py --community MindSpore --limit 20 --lists "dev@mindspore.cn,mindspore-tsc@mindspore.cn"

Output: JSON object with SIG metadata + email threads to stdout, errors to stderr.
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
import urllib.parse

SITE_BASE = "https://www.mindspore.cn"
MAIL_BASE = "https://mailweb.mindspore.cn"


def fetch_json(url: str) -> dict | list:
    """Fetch and parse JSON from a URL."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "GEO-Search-Assessment/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} fetching {url}", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"Network error fetching {url}: {e.reason}", file=sys.stderr)
        raise


# ── Step 1: SIG list → mailing list addresses ──────────────────────────────

def fetch_sig_mailing_lists(community: str) -> dict:
    """Fetch SIG list and extract unique mailing_list addresses.

    Returns dict: {
        "sigs": [{"name", "description", "mailing_list", "maintainers"}],
        "mailing_lists": ["dev@mindspore.cn", ...]
    }
    """
    url = f"{SITE_BASE}/api-magicapi/sig/all/{community.lower()}"
    data = fetch_json(url)
    sig_list = data.get("data", {}).get("sigList", [])

    sigs = []
    ml_set = set()
    for sig in sig_list:
        ml = sig.get("mailing_list", "")
        maintainers = []
        for m in sig.get("maintainers", []):
            maintainers.append({
                "name": m.get("name", ""),
                "organization": m.get("organization", ""),
            })
        sigs.append({
            "name": sig.get("name", ""),
            "description": (sig.get("description", "") or "")[:300],
            "mailing_list": ml,
            "maintainers": maintainers,
        })
        if ml:
            ml_set.add(ml)

    return {"sigs": sigs, "mailing_lists": sorted(ml_set)}


# ── Step 2: HyperKitty API → email archives ────────────────────────────────

def fetch_all_mailing_lists() -> list[dict]:
    """Fetch all available mailing lists from HyperKitty API."""
    url = f"{MAIL_BASE}/hyperkitty/api/lists/"
    data = fetch_json(url)
    return data.get("results", [])


def fetch_threads(list_addr: str, limit: int = 50) -> list[dict]:
    """Fetch recent threads from a mailing list.

    HyperKitty paginates at 10 per page. Fetches multiple pages up to limit.
    """
    threads = []
    offset = 0
    page_size = 10

    while len(threads) < limit:
        url = (
            f"{MAIL_BASE}/hyperkitty/api/list/{list_addr}/threads/"
            f"?limit={page_size}&offset={offset}"
        )
        try:
            data = fetch_json(url)
        except Exception as e:
            print(f"  WARNING: Failed to fetch threads at offset {offset}: {e}", file=sys.stderr)
            break

        results = data.get("results", [])
        if not results:
            break

        threads.extend(results)
        offset += page_size

        if not data.get("next"):
            break

    return threads[:limit]


def fetch_email_content(list_addr: str, message_id_hash: str) -> dict | None:
    """Fetch a single email's content from HyperKitty API."""
    url = f"{MAIL_BASE}/archives/api/list/{list_addr}/email/{message_id_hash}/"
    try:
        return fetch_json(url)
    except Exception as e:
        print(f"  WARNING: Failed to fetch email {message_id_hash}: {e}", file=sys.stderr)
        return None


def normalize_thread(thread: dict, email: dict | None) -> dict:
    """Normalize a thread + email into a clean structure."""
    result = {
        "subject": thread.get("subject", ""),
        "date": thread.get("date_active", ""),
        "replies": thread.get("replies_count", 0),
    }

    if email:
        result["sender_name"] = email.get("sender_name", "")
        content = email.get("content", "")
        # Truncate long emails but keep enough for question generation
        result["content"] = content[:1000] if content else ""

    return result


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Fetch SIG mailing list email archives from HyperKitty"
    )
    parser.add_argument("--community", required=True, help="Community name (e.g., MindSpore)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max email threads to fetch per mailing list")
    parser.add_argument("--lists", default=None,
                        help="Comma-separated mailing list addresses to fetch "
                             "(default: auto-discover from SIG API)")
    parser.add_argument("--fetch-content", action="store_true",
                        help="Also fetch full email body for each thread (slower, more API calls)")
    args = parser.parse_args()

    # ── Step 1: Get SIG → mailing list mapping ──
    print(f"Step 1: Fetching SIG mailing lists for {args.community}...", file=sys.stderr)
    try:
        sig_data = fetch_sig_mailing_lists(args.community)
    except Exception as e:
        print(f"ERROR: Failed to fetch SIG list: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Found {len(sig_data['sigs'])} SIGs, "
          f"{len(sig_data['mailing_lists'])} unique mailing lists", file=sys.stderr)

    # Determine which lists to fetch
    if args.lists:
        target_lists = [addr.strip() for addr in args.lists.split(",")]
    else:
        # Auto: use SIG-associated lists + discover all available lists
        all_lists = fetch_all_mailing_lists()
        available_addrs = {ml.get("name", "") for ml in all_lists}
        # Merge SIG lists + all available lists (some lists aren't SIG-specific)
        target_lists = sorted(
            sig_data["mailing_lists"] | available_addrs - {""}
        )

    print(f"  Target lists: {target_lists}", file=sys.stderr)

    # ── Step 2: Fetch email archives ──
    print("Step 2: Fetching email archives...", file=sys.stderr)
    archives = {}

    for addr in target_lists:
        print(f"  Fetching {addr}...", file=sys.stderr)
        threads = fetch_threads(addr, limit=args.limit)

        if not threads:
            print(f"    {addr}: 0 threads (empty)", file=sys.stderr)
            continue

        normalized = []
        for thread in threads:
            email = None
            if args.fetch_content:
                # Extract message_id_hash from the starting_email URL
                starting_url = thread.get("starting_email", "")
                if starting_url:
                    msg_hash = starting_url.rstrip("/").split("/")[-1]
                    email = fetch_email_content(addr, msg_hash)

            normalized.append(normalize_thread(thread, email))

        archives[addr] = normalized
        print(f"    {addr}: {len(normalized)} threads", file=sys.stderr)

    # ── Output ──
    total_threads = sum(len(v) for v in archives.values())
    print(f"Total: {total_threads} threads from {len(archives)} lists", file=sys.stderr)

    output = {
        "_meta": {
            "source": f"{SITE_BASE}/sig",
            "api_sig_list": f"{SITE_BASE}/api-magicapi/sig/all/{args.community.lower()}",
            "api_mail_archive": f"{MAIL_BASE}/hyperkitty/api/",
            "mailman_web": f"{MAIL_BASE}/postorius/lists/",
        },
        "sigs": sig_data["sigs"],
        "archives": archives,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
