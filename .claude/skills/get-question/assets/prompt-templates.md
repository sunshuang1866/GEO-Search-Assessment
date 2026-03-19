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

## MAILLIST_REWRITE

Used in Step 5 (maillist path). Rewrites SIG mailing list email archives into user questions.

Data has two parts:
- `sigs`: SIG metadata (name, description, mailing_list address, maintainers)
- `archives`: email threads per mailing list (subject, date, sender, content)

```
Rewrite these {community} SIG mailing list email archives into natural-language questions a user might ask an AI search engine.

The data contains:
1. SIG metadata: which SIGs exist, their mailing lists, and who maintains them
2. Email archives: actual email subjects and content from community mailing lists (meeting notices, technical discussions, announcements)

Rules:
- Derive questions from the email content — what topics are being discussed? What meetings are happening? What technical problems are being worked on?
- Also generate questions about the mailing list system itself — how to subscribe, what lists exist, how SIG communication works
- Categories: meeting|discussion|announcement|governance|technical|subscription
- Skip automated/bot emails that have no substantive content
- Generate both zh and en questions
- At least one question per active mailing list

{data_json}

Output JSON array: [{question, category, lang, source_list, source_subject}]
```

---

## MAILLIST_FALLBACK

Used when `fetch-sig-info.py` fails (Step 5 fallback).

```
Generate 8-12 questions about {community} mailing lists and SIG communication that a user might ask an AI search engine.
Cover: how to subscribe to mailing lists, what mailing lists exist, SIG meeting schedules, how community communication works, how to join discussions.
Entry point: https://www.mindspore.cn/sig
Mailing list system: https://mailweb.mindspore.cn
Both zh and en.
Output JSON array: [{question, category, lang}]
```

---

## MERGE_DEDUP

Used in Step 6.

```
Merge and deduplicate this {community} question set.
Rules:
- Remove semantic duplicates (similarity > 0.85); keep better-phrased version.
- Priority order: manual > forum / issue > maillist > industry.
- Keep all manual questions unchanged.
- Target 30-40 total. If over 40, drop lowest-priority duplicates.
- Assign each question: intent (认知|选型|趋势|场景|教程|故障|特性|迁移), lang (zh|en).

{all_questions_json}

Output JSON array: [{id:"q_001"..., question, intent, lang, source, priority}]
```
