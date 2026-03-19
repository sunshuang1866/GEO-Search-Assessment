#!/usr/bin/env python3
"""Compile scoring report from results, patterns, and suggestions.

Reads JSON from stdin, deduplicates suggestions, sorts by priority, assigns IDs,
and outputs the final compiled JSON to stdout.
"""

import json
import sys
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    """Compute text similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def deduplicate_suggestions(suggestions: list, threshold: float = 0.8) -> list:
    """Remove suggestions with >threshold text similarity."""
    if not suggestions:
        return []

    unique = [suggestions[0]]
    for s in suggestions[1:]:
        s_text = s.get("suggestion_text", "") + " ".join(s.get("catalog_refs", []))
        is_dup = False
        for u in unique:
            u_text = u.get("suggestion_text", "") + " ".join(u.get("catalog_refs", []))
            if similarity(s_text, u_text) > threshold:
                # Keep the higher priority one
                priority_order = {"P0": 0, "P1": 1, "P2": 2}
                s_pri = priority_order.get(s.get("severity", "P2"), 2)
                u_pri = priority_order.get(u.get("severity", "P2"), 2)
                if s_pri < u_pri:
                    unique.remove(u)
                    unique.append(s)
                # Merge affected_platforms
                u_platforms = set(u.get("affected_platforms", [u.get("platform", "")]))
                s_platforms = set(s.get("affected_platforms", [s.get("platform", "")]))
                merged = unique[-1]
                merged["affected_platforms"] = sorted(u_platforms | s_platforms)
                is_dup = True
                break
        if not is_dup:
            unique.append(s)
    return unique


def assign_ids(suggestions: list) -> list:
    """Assign unique IDs to suggestions."""
    for i, s in enumerate(suggestions, 1):
        s["suggestion_id"] = f"s_{i:03d}"
    return suggestions


def sort_by_priority(suggestions: list) -> list:
    """Sort suggestions by priority (P0 first) then by category."""
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    return sorted(suggestions, key=lambda s: (
        priority_order.get(s.get("severity", "P2"), 2),
        s.get("category", "zzz"),
        s.get("question_id", "")
    ))


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    results = data.get("results", [])
    patterns = data.get("patterns", {})
    suggestions = data.get("suggestions", [])
    metadata = data.get("metadata", {})

    # Deduplicate
    suggestions = deduplicate_suggestions(suggestions)

    # Sort
    suggestions = sort_by_priority(suggestions)

    # Assign IDs
    suggestions = assign_ids(suggestions)

    # Compute summary stats
    def count_by_priority(items):
        counts = {"P0": 0, "P1": 0, "P2": 0}
        for item in items:
            p = item.get("severity", "P2")
            counts[p] = counts.get(p, 0) + 1
        return counts

    content_origin_count = sum(
        1 for s in suggestions if s.get("is_content_origin", False)
    )

    report = {
        "metadata": metadata,
        "summary": {
            "total_results": len(results),
            "suggestions_count": len(suggestions),
            "suggestions_by_priority": count_by_priority(suggestions),
            "content_origin_issues": content_origin_count,
        },
        "results": results,
        "patterns": patterns,
        "suggestions": suggestions,
    }

    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    print(f"\nCompiled: {len(suggestions)} suggestions "
          f"({content_origin_count} content-origin)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
