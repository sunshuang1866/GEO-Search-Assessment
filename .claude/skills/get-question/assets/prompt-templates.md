# Prompt Templates

## REWRITE_TO_QUESTIONS

Shared template for Step 3 (forum) and Step 4 (issue). Replace `{source_type}`, `{source_desc}`, `{categories}`, `{data_json}`, `{output_extra_fields}`.

```
Rewrite these {community} {source_desc} into natural-language questions a user might ask an AI.
Rules:
- At least one question per item. Preserve specificity, do not over-generalize.
- Skip pure bug reports with only stack traces (no general learning value).
- Classify category: {categories}

{data_json}

Output JSON array: [{question, category, lang{output_extra_fields}}]
```

### Forum variant (Step 3)

- `{source_desc}`: `forum post titles, sorted by views (most viewed first)`
- `{categories}`: `installation|configuration|training|deployment|migration|troubleshooting|feature|performance|event|tutorial|other`
- `{output_extra_fields}`: `, source_title, source_views`

### Issue variant (Step 4)

- `{source_desc}`: `GitCode issue titles, sorted by engagement (comments)`
- `{categories}`: `installation|configuration|training|deployment|migration|troubleshooting|feature|performance|compatibility`
- `{output_extra_fields}`: `, source_title, source_comments`

---

## FORUM_FALLBACK

Used when `fetch-forum-posts.py` fails (Step 3 fallback).

```
Generate 10-15 typical usage questions for {community} ({seed_keywords}) that developers post on forums.
Cover: installation, configuration, training, deployment, migration, troubleshooting. Both zh and en.
Output JSON array: [{question, category, lang}]
```

---

## INDUSTRY_DISCOVERY

Used in Step 5 (single LLM call).

```
For open-source project "{community}" (keywords: {seed_keywords}):

1. Identify: industry, sub-domain, positioning, competitors (3-5 names).
2. Generate 10-15 questions a user might ask an AI about this domain — including questions where they don't yet know {community} exists. Cover:
   - "What are mainstream X?"
   - "Which X should I choose?"
   - "What are trends in X?"
   - "What X fits Y scenario?"
   - "Alternatives to {competitor}?"
   Both zh and en.

Output JSON: {
  "domain": {industry, sub_domain, positioning, competitors},
  "questions": [{question, intent, lang}]
}
```

---

## MERGE_DEDUP

Used in Step 6.

```
Merge and deduplicate this {community} question set.
Rules:
- Remove semantic duplicates (similarity > 0.85); keep better-phrased version.
- Priority order: manual > forum / issue > industry.
- Keep all manual questions unchanged.
- Target 30-40 total. If over 40, drop lowest-priority duplicates.
- Assign each question: intent (认知|选型|趋势|场景|教程|故障|特性|迁移), lang (zh|en).

{all_questions_json}

Output JSON array: [{id:"q_001"..., question, intent, lang, source, priority}]
```
