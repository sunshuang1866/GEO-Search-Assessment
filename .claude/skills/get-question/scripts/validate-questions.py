#!/usr/bin/env python3
"""Validate questions JSON from stdin.

Usage: cat questions.json | python3 validate-questions.py

Validates:
- JSON structure is a valid array
- Each item has required fields: id, question, intent, lang, source
- intent is one of: 认知, 选型, 趋势, 场景, 教程, 故障, 特性, 迁移
- lang is one of: zh, en
- id follows pattern q_NNN
- No duplicate ids
- Total count is within 30-40 range (warning if outside)

Output: "VALID" to stdout on success, errors to stderr on failure.
"""

import json
import re
import sys

REQUIRED_FIELDS = {"id", "question", "intent", "lang", "source"}
VALID_LANGS = {"zh", "en"}
VALID_INTENTS = {"认知", "选型", "趋势", "场景", "教程", "故障", "特性", "迁移"}


def validate(data: list) -> list[str]:
    errors = []

    if not isinstance(data, list):
        return ["ERROR: Root element must be a JSON array."]

    seen_ids = set()
    for i, item in enumerate(data):
        prefix = f"Item [{i}]"

        if not isinstance(item, dict):
            errors.append(f"{prefix}: Must be a JSON object.")
            continue

        # Check required fields
        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            errors.append(f"{prefix}: Missing fields: {missing}")
            continue

        # Validate id
        qid = item["id"]
        if not re.match(r"^q_\d{3}$", qid):
            errors.append(f"{prefix}: id '{qid}' must match pattern q_NNN (e.g., q_001).")
        if qid in seen_ids:
            errors.append(f"{prefix}: Duplicate id '{qid}'.")
        seen_ids.add(qid)

        # Validate lang
        if item["lang"] not in VALID_LANGS:
            errors.append(f"{prefix}: Invalid lang '{item['lang']}'. Must be one of {VALID_LANGS}.")

        # Validate intent
        if item["intent"] not in VALID_INTENTS:
            errors.append(f"{prefix}: Invalid intent '{item['intent']}'. Must be one of {VALID_INTENTS}.")

        # Validate question is non-empty
        if not item["question"] or len(item["question"].strip()) < 3:
            errors.append(f"{prefix}: Question is empty or too short.")

    # Count warnings
    total = len(data)
    if total < 30:
        errors.append(f"WARNING: Only {total} questions. Target is 30-40.")
    elif total > 40:
        errors.append(f"WARNING: {total} questions exceeds target of 30-40.")

    return errors


if __name__ == "__main__":
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate(data)
    if errors:
        # Separate actual errors from warnings
        real_errors = [e for e in errors if not e.startswith("WARNING")]
        warnings = [e for e in errors if e.startswith("WARNING")]

        for w in warnings:
            print(w, file=sys.stderr)

        if real_errors:
            for e in real_errors:
                print(e, file=sys.stderr)
            sys.exit(1)

    print(f"VALID: {len(data)} questions passed validation.")
