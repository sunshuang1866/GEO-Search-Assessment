---
name: scoring-engine
description: Evaluates AI platform responses using a multi-layer model (content completeness + citation accuracy + optional fact coverage). Reads responses.json and content-labels.json, classifies each question-platform pair into phenomena (A-E), calculates official source citation ratios, identifies content issues, matches optimization suggestions from a 72-item catalog, and performs cross-platform pattern analysis. Optionally accepts standard-answers.json for deeper fact-level diagnosis. Assigns severity (P0-P2) and outputs scoring-results.json with suggestions.md. Supports human spot-check calibration via scoring-calibration.md feedback loop. Use after platform-sampler completes sampling. Do not use for question generation, platform sampling, or issue creation.
---

# Scoring Engine

Evaluate AI platform responses against official content availability. Multi-layer assessment: content completeness (human-labeled), citation accuracy (LLM-judged), and optional fact coverage analysis (when standard answers are available). Includes cross-platform pattern analysis and catalog-based suggestion matching.

## Prerequisites

- `responses.json` in the project root (output from platform-sampler skill)
- `content-labels.json` in the project root (human pre-labeled: `content_exists`, `official_urls`, `content_coverage` per question)
- Optional: `standard-answers.json` (official standard answers — enables Layer 2+ fact coverage analysis)
  - Alternative sources: `INPUT.md` or answer files in `Answers/` directory (Markdown format)
- Optional: `scoring-calibration.md` (feedback from prior human spot-checks, incorporated as prompt context)

## Procedures

**Step 1: Load and Validate Inputs**

1. Read `responses.json` from the project root.
2. Run `python3 scripts/validate-inputs.py responses.json content-labels.json` to verify both files exist and are structurally valid.
3. The script checks:
   - `responses.json` contains a `responses` array with `question_id`, `platform`, `response_text` fields.
   - `content-labels.json` contains a `labels` array with `question_id`, `content_exists` fields.
   - Every `question_id` in responses has a matching label entry.
4. If validation fails, abort with the specific error from stderr.
5. If `scoring-calibration.md` exists, read it. This contains human corrections from prior rounds — use as additional prompt context in Step 3.
6. Check for optional standard answers:
   - If `standard-answers.json` exists, read it directly. Set `has_standard_answers = true`.
   - Otherwise, scan `INPUT.md` and `Answers/*.md` for question-answer pairs. If found, extract the official answer text and source URLs for each question. Set `has_standard_answers = true`.
   - If neither exists, set `has_standard_answers = false`. Log: `"No standard answers found. Skipping Layer 2+ fact coverage analysis."`
7. Load recognized citation sources from `.env` field `OFFICIAL_DOMAINS` (comma-separated). Default: `mindspore.cn,gitcode.com/mindspore,github.com/mindspore-ai,gitee.com/mindspore`.
8. Print input summary to stdout.

**Step 2: Layer 1 — Content Completeness**

1. Read `content-labels.json` and extract each question's `content_exists` value.
2. For each question where `content_exists` is `false` or `"none"`:
   - Classify as **Phenomenon A** (官网无内容).
   - Assign severity **P0**.
   - Do NOT proceed to Layer 2 for this question — there is no baseline to evaluate against.
   - Generate suggestion: "补充官方内容覆盖此问题".
3. For each question where `content_exists` is `true`:
   - Mark as eligible for Layer 2 evaluation.
   - Record the `official_urls` and `content_coverage` for use in Layer 2 prompts.
4. For each question where `content_exists` is `null` (unlabeled):
   - Log a warning: `"question {question_id} has no content_exists label, skipping"`.
   - Exclude from scoring.
5. Output a Layer 1 summary to stdout:
   ```
   Layer 1 — Content Completeness:
     Total questions: {n}
     Labeled: {labeled}
     Unlabeled (skipped): {unlabeled}
     Phenomenon A (no content): {a_count} → P0
     Eligible for Layer 2: {eligible}
   ```

**Step 3: Layer 2 — Citation Accuracy (LLM Evaluation)**

1. For each question eligible for Layer 2, iterate over all platform responses.
2. For each (question, platform) pair, construct an LLM evaluation prompt.
3. Read `references/scoring-prompt-template.md` for the full prompt template.
4. The prompt instructs the LLM to:
   - Identify all sources cited or referenced in the AI response (explicit URLs, named sources, implied references).
   - Classify each source as "official" (matching `official_urls` domains or known official channels) or "third-party".
   - Calculate `official_source_ratio` = official source count / total source count.
   - Determine which phenomenon (B/C/D/E) applies based on the classification rules in the prompt.
   - Assign an `accuracy_score` (1-10 scale).
   - Identify content issues as `issues_found` tags (26 standardized tags for matching catalog suggestions).
   - Provide a brief `details` explanation.
5. Parse the LLM response. Run `python3 scripts/parse-llm-score.py '{llm_response_json}'` to extract and validate the structured scoring fields.
6. The script validates:
   - `citation_type` is one of B, C, D, E.
   - `official_source_ratio` is a float between 0.0 and 1.0.
   - `accuracy_score` is an integer 1-10.
   - `issues_found` is an array of valid issue tags.
   - All required fields are present.
7. If parsing fails, retry the LLM call once with a stricter format instruction. If it fails again, log the error and mark the pair as `"scoring_failed"`.

**Step 4: Layer 2+ — Fact Coverage Analysis (Optional)**

> This step only runs when `has_standard_answers = true`. If no standard answers are available, skip to Step 5.

For each question that has both platform responses and a standard answer:

1. Extract the standard answer's key facts as a checklist. Prompt the LLM:
   ```
   Given the following official standard answer:

   {standard_answer}

   Extract a list of key facts (atomic claims) that a correct response MUST convey.
   Mark each fact as either:
   - POSITIVE (something that IS true, e.g., "supports Ascend/GPU/CPU")
   - NEGATIVE (something that is NOT true / a limitation, e.g., "cannot directly read PyTorch models")

   Output as JSON array: [{"fact": "...", "polarity": "POSITIVE|NEGATIVE"}]
   ```

2. For each platform response, run the fact coverage check prompt:
   ```
   You are a GEO fact coverage checker. Compare this AI platform response against the official key facts.

   Question: {question}
   Platform: {platform_name}
   Platform Response: {response_text}
   Official Key Facts: {key_facts_json}

   Evaluate and output JSON:
   {
     "fact_coverage": {
       "covered_facts": ["..."],
       "missed_facts": ["..."],
       "contradicted_facts": ["..."],
       "fabricated_claims": ["..."]
     },
     "negation_handling": "correct|missed|reversed",
     "fact_coverage_ratio": 0.0-1.0
   }
   ```

3. Merge fact coverage results into the Layer 2 scoring results for the same (question, platform) pair:
   - If `contradicted_facts` is non-empty, override `citation_type` to **C** and severity to **P0**.
   - If `fabricated_claims` is non-empty, add `fabricated_claims` to `issues_found`.
   - If `negation_handling` is "missed", add `negation_missed` to `issues_found`.
   - If `negation_handling` is "reversed", add `negation_reversed` to `issues_found`.
   - Append `fact_coverage` data to the result object.

4. Output a Layer 2+ summary to stdout:
   ```
   Layer 2+ — Fact Coverage:
     Questions with standard answers: {n}
     Avg fact coverage ratio: {ratio:.1%}
     Contradicted facts found: {contradicted_count}
     Fabricated claims found: {fabricated_count}
     Negation failures: {negation_count}
   ```

**Step 5: Cross-Platform Pattern Analysis**

1. Group all scored results by question. For each question, identify:
   - Which platforms scored well vs poorly
   - Common `issues_found` tags across platforms
   - Whether an issue is **content-origin** (appears on ≥3 platforms, meaning the official content needs fixing) or **platform-specific** (only 1 platform, likely a platform-side issue)

2. Group results by `issues_found` tags. Prompt the LLM:
   ```
   Given the following scoring results across all questions and platforms:

   {results_json}

   Identify recurring patterns:
   1. HALLUCINATION patterns: Which topics/terms trigger fabricated claims? On which platforms?
   2. DISAMBIGUATION patterns: Which terms are ambiguous? What are they confused with?
   3. NEGATION failures: Which negative facts are consistently missed or reversed?
   4. CITATION gaps: Which pages/topics have zero official citations across all platforms?
   5. CONTENT-ORIGIN issues: Which problems appear on ≥3 platforms (indicating the official content needs improvement)?

   Output as JSON:
   {
     "hallucination_patterns": [{"trigger": "...", "platforms": [...], "example": "..."}],
     "disambiguation_patterns": [{"term": "...", "confused_with": "...", "platforms": [...]}],
     "negation_failures": [{"fact": "...", "platforms_missed": [...]}],
     "citation_gaps": [{"topic": "...", "suggested_page": "..."}],
     "content_origin_issues": [{"issue": "...", "affected_platforms": [...], "question_ids": [...]}]
   }
   ```

3. Store the pattern analysis result. This feeds into Step 6 for suggestion prioritization and into Step 7 for the report.

**Step 6: Assign Severity and Match Suggestions from Catalog**

1. For each scored (question, platform) pair, assign severity based on these rules:
   - **P0**: Phenomenon A (content gap) or C (wrong/hallucinated citation)
   - **P1**: Phenomenon B (has content, not cited) or E (low citation ratio, `official_source_ratio` < 0.3)
   - **P2**: Phenomenon D with minor issues (ratio > 0.7 but some inaccuracies noted)
   - **No action**: Phenomenon D, ratio > 0.7, no issues
2. Read `references/geo-suggestions-catalog.md` — the complete GEO optimization suggestion catalog (72 items).
3. Read `references/suggestion-rules.md` for the matching workflow:
   a. Use the phenomenon type to look up candidate suggestion IDs from the catalog's mapping table.
   b. Use the `issues_found` tags from the scoring output to narrow down the most relevant suggestions via the issue→suggestion mapping table.
   c. Select the top 5 most relevant suggestions per (question, platform) pair.
   d. For suggestions that appear across multiple platforms for the same question, merge into one suggestion listing all affected platforms.
   e. For **content-origin issues** from Step 5 (≥3 platforms), elevate the merged suggestion's priority by one level (P2→P1 or P1→P0).
4. For each matched suggestion, generate a suggestion object:
   ```json
   {
     "suggestion_id": "s_001",
     "question_id": "q_001",
     "question": "...",
     "platform": "ChatGPT",
     "citation_type": "B",
     "official_source_ratio": 0.2,
     "accuracy_score": 4,
     "severity": "P1",
     "category": "seo",
     "catalog_refs": ["CTX-02", "ORG-05", "DIS-01"],
     "suggestion_text": "针对该问题和官方页面的实际情况，将 catalog 中的通用指南转化为具体可执行的改进措施",
     "details": "...",
     "affected_platforms": ["ChatGPT", "DeepSeek"],
     "is_content_origin": true
   }
   ```
5. Categories: `content` (A — missing content), `seo` (B — discoverability), `correction` (C — wrong info), `optimization` (E — low ratio).

**Step 7: Compile Output**

1. Run `python3 scripts/compile-report.py` with scoring results piped as JSON to stdin:
   ```json
   {
     "results": [...],
     "patterns": {...},
     "suggestions": [...],
     "metadata": {
       "scored_at": "...",
       "total_questions": N,
       "total_platforms": N,
       "platforms": [...],
       "has_standard_answers": true,
       "official_domains": [...]
     }
   }
   ```
   The script:
   - Deduplicates suggestions with >80% text similarity
   - Sorts by priority (P0 → P1 → P2), then by impact breadth
   - Assigns unique IDs to each suggestion
   - Outputs compiled JSON to stdout

2. Write `scoring-results.json` to the project root:
   ```json
   {
     "metadata": {
       "scored_at": "2026-03-12T...",
       "total_questions": 10,
       "total_platforms": 4,
       "total_pairs": 40,
       "scored_pairs": 36,
       "skipped_pairs": 4,
       "has_standard_answers": true
     },
     "results": [
       {
         "question_id": "q_001",
         "platform": "ChatGPT",
         "content_exists": true,
         "citation_type": "B",
         "official_source_ratio": 0.2,
         "accuracy_score": 4,
         "severity": "P1",
         "details": "...",
         "issues_found": ["no_direct_answer", "missing_faq"],
         "sources_identified": [...],
         "fact_coverage": { ... }
       }
     ],
     "patterns": {
       "hallucination_patterns": [...],
       "disambiguation_patterns": [...],
       "negation_failures": [...],
       "citation_gaps": [...],
       "content_origin_issues": [...]
     },
     "summary": {
       "by_phenomenon": {"A": 4, "B": 12, "C": 2, "D": 18, "E": 4},
       "by_severity": {"P0": 6, "P1": 16, "P2": 4, "no_action": 14},
       "by_platform": {
         "ChatGPT": {"avg_score": 6.2, "avg_ratio": 0.45},
         "DeepSeek": {"avg_score": 5.8, "avg_ratio": 0.38}
       }
     },
     "suggestions": [...]
   }
   ```

3. Generate `suggestions.md` using the template in `assets/suggestions-template.md`. Fill in:
   - Executive summary (total scores, breakdown by phenomenon and severity).
   - Key findings (top 3 from pattern analysis).
   - Per-question detail tables (including fact coverage when available).
   - Platform comparison matrix.
   - Cross-platform pattern summary.
   - Prioritized action items grouped by severity (with catalog_refs).
   - Execution roadmap (P0: 1-2 weeks, P1: 2-4 weeks, P2: ongoing).
   - KPI tracking targets.
4. Write `suggestions.md` to the project root.
5. Print a summary to stdout:
   ```
   Scoring complete:
     Pairs scored: {scored}/{total}
     Fact coverage: {yes/no} (standard answers {found/not found})
     P0: {p0} | P1: {p1} | P2: {p2} | OK: {ok}
     Content-origin issues: {n} (appear on ≥3 platforms)
     Avg citation ratio: {avg_ratio:.1%}
     Output: scoring-results.json, suggestions.md
   ```

**Step 8: Human Spot-Check Calibration**

1. PAUSE and inform the operator:
   ```
   Scoring complete. Please review scoring-results.json.
   Recommended: spot-check 20% of results (stratified by severity).
   Record corrections in scoring-calibration.md.
   ```
2. Run `python3 scripts/select-spot-check.py scoring-results.json` to generate a stratified sample for review.
3. The script outputs a Markdown checklist of (question_id, platform) pairs to review, sampling proportionally from each severity level.
4. After human review, any corrections saved to `scoring-calibration.md` will be incorporated as prompt context in the next scoring run (learning loop).

## Error Handling

* If `responses.json` is missing, abort with: `"responses.json not found. Run platform-sampler skill first."`
* If `content-labels.json` is missing, abort with: `"content-labels.json not found. Human labeling required before scoring."`
* If `content-labels.json` has all `content_exists: null`, abort with: `"No questions have been labeled. Complete human labeling first."`
* If `standard-answers.json` is missing and no `Answers/` directory: skip Layer 2+ with a log message (not an error).
* If a question in `responses.json` has no matching standard answer, skip fact coverage for that question with a warning.
* If LLM scoring fails for a (question, platform) pair after retry, log the error and continue. Report failed pairs in the summary.
* If more than 50% of pairs fail scoring, abort with: `"Too many scoring failures ({n}/{total}). Check LLM API availability."`
* If the LLM pattern analysis prompt returns malformed JSON, retry once. If still malformed, log the error and proceed without pattern analysis.
