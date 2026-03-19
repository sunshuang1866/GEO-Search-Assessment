#!/usr/bin/env python3
"""Parse and validate LLM scoring output for a single (question, platform) pair.

Usage:
    python3 parse-llm-score.py '<json_string>'

Validates the structured scoring fields and outputs cleaned JSON to stdout.
Errors go to stderr with non-zero exit code.
"""

import json
import sys


VALID_CITATION_TYPES = {"B", "C", "D", "E"}
REQUIRED_FIELDS = ["citation_type", "official_source_ratio", "accuracy_score", "details"]
VALID_ISSUE_TAGS = {
    "no_direct_answer", "buried_answer", "missing_faq", "ambiguous_terminology",
    "missing_disambiguation", "negation_missed", "negation_reversed", "outdated_info",
    "version_confusion", "fabricated_claims", "vague_numbers", "no_schema_markup",
    "poor_structure", "no_tables", "missing_summary", "no_query_variants",
    "missing_scope", "entity_confusion", "shallow_content", "no_evidence",
    "no_alternatives", "missing_use_cases", "no_process_doc", "inconsistent_data",
    "missing_edge_cases", "no_reasoning",
}


def parse_and_validate(raw_json):
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: Cannot parse LLM output as JSON: {e}", file=sys.stderr)
        sys.exit(1)

    errors = []

    # Check required fields
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        errors.append(f"Missing required fields: {missing}")

    # Validate citation_type
    ct = data.get("citation_type", "")
    if ct not in VALID_CITATION_TYPES:
        errors.append(f"Invalid citation_type '{ct}'. Must be one of {VALID_CITATION_TYPES}")

    # Validate official_source_ratio
    ratio = data.get("official_source_ratio")
    if ratio is not None:
        try:
            ratio = float(ratio)
            if not (0.0 <= ratio <= 1.0):
                errors.append(f"official_source_ratio {ratio} out of range [0.0, 1.0]")
            else:
                data["official_source_ratio"] = ratio
        except (TypeError, ValueError):
            errors.append(f"official_source_ratio '{ratio}' is not a valid number")

    # Validate accuracy_score
    score = data.get("accuracy_score")
    if score is not None:
        try:
            score = int(score)
            if not (1 <= score <= 10):
                errors.append(f"accuracy_score {score} out of range [1, 10]")
            else:
                data["accuracy_score"] = score
        except (TypeError, ValueError):
            errors.append(f"accuracy_score '{score}' is not a valid integer")

    if errors:
        print("VALIDATION ERRORS:\n" + "\n".join(f"  - {e}" for e in errors), file=sys.stderr)
        sys.exit(1)

    # Validate issues_found
    issues = data.get("issues_found", [])
    if not isinstance(issues, list):
        errors.append(f"issues_found must be an array, got {type(issues).__name__}")
        issues = []
    else:
        invalid_tags = [t for t in issues if t not in VALID_ISSUE_TAGS]
        if invalid_tags:
            print(f"WARNING: Unknown issue tags (ignored): {invalid_tags}", file=sys.stderr)
        issues = [t for t in issues if t in VALID_ISSUE_TAGS]

    # Output cleaned data
    output = {
        "citation_type": data["citation_type"],
        "official_source_ratio": data["official_source_ratio"],
        "accuracy_score": data["accuracy_score"],
        "details": data.get("details", ""),
        "issues_found": issues,
        "sources_identified": data.get("sources_identified", []),
    }
    json.dump(output, sys.stdout, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 parse-llm-score.py '<json_string>'", file=sys.stderr)
        sys.exit(1)
    parse_and_validate(sys.argv[1])
