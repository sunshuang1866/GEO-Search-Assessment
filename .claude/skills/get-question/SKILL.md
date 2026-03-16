---
name: get-question
description: Generates a structured question set for GEO search assessment. Supports 3 question source paths (forum, issue, industry) — select individually or all. Reads manual questions from Markdown, auto-generates questions via selected paths, merges, deduplicates semantically, classifies by scenario and intent, then outputs questions.json and questions.md. Forum and issue are the primary sources. Use when starting a new GEO assessment or refreshing the question set for a community. Do not use for platform sampling, scoring, or improvement suggestion generation.
---

# Get Question

Generate a comprehensive question set covering two scenarios (了解阶段 + 使用阶段) for GEO search assessment.

## Prerequisites

- `.env` file with API tokens (copy from `.env.example` if missing)
- Community name provided as input

## Procedures

**Step 1: Load Configuration**

1. Set `SKILL_DIR=.claude/skills/get-question`. All script invocations in subsequent steps use this prefix (e.g., `python3 $SKILL_DIR/scripts/fetch-forum-posts.py`).
2. Read `.env` from the project root to load API tokens.
3. Accept required and optional inputs from the caller:
   - `community` (required): Community name (e.g., "MindSpore")
   - `seed_keywords` (optional): Comma-separated seed keywords (e.g., "深度学习框架,AI计算,端侧推理"). If not provided, derive automatically using the LLM: `"List 3-5 comma-separated technical keywords that best describe the open-source project '{community}'. Output only the keywords, no explanation."`
   - `paths` (optional): Comma-separated list of paths to run. Options: `forum`, `issue`, `industry`, `all`. Default: `all`.
     - `forum` → Path 1: Forum Usage Question Extraction (primary source)
     - `issue` → Path 2: Repo Issue Question Extraction (primary source)
     - `industry` → Path 3: Industry Question Discovery
     - `all` → Run all three paths
   - `forum_url` (optional): Override the forum base URL (e.g., `https://discuss.mindspore.cn`). If not explicitly provided but the caller passes a URL-shaped string, treat it as `forum_url`.
   - `limit` (optional): Max topics/issues to fetch per source. Default: `50`. Parse Chinese format if given (e.g., "前10" or "前10的热门问题" → `10`).
4. Check if `feedback-rules.md` exists in the project root. If present, read it and incorporate the rules as additional prompt context for all LLM calls in subsequent steps.
5. Log resolved configuration: `"Community: {community} | Keywords: {seed_keywords} | Paths: {paths} | Limit: {limit}"`

**Step 2: Parse Manual Questions**

1. Check if `manual-questions.md` exists in the project root.
2. If present, run `python3 $SKILL_DIR/scripts/parse-manual-questions.py manual-questions.md` to extract questions.
3. The script outputs JSON to stdout. Capture the output as the manual question list.
4. If the file does not exist, skip this step with an empty manual question list.

**Step 3: Path 1 — Forum Usage Question Extraction (使用阶段) [PRIMARY]**

> This is the primary question source. Forum and issue data reflect real developer pain points.
> Only runs if `paths` includes `forum` or `all`.

1. Build the command: `python3 $SKILL_DIR/scripts/fetch-forum-posts.py --community "{community}" --limit {limit}`. If `forum_url` was provided, append `--api-url "{forum_url}"`.
2. Run the command. The script fetches from `问题求助 Help` (id:4) and `MindSpore Lite` (id:38) categories, sorted by views, pinned/closed topics excluded. See `$SKILL_DIR/references/forum-api-spec.md` for full API details.
3. If the script succeeds, prompt the LLM to rewrite forum topics into search questions:
   ```
   The following are real forum post titles from the {community} community, sorted by views (most viewed first).
   For each post, think about what questions a user might type into an AI assistant about this topic.
   The scope is broad: technical problems, feature explanations, community events, blog topics, announcements — anything a user might be curious about and ask an AI.

   Rules:
   - For every post, generate at least one natural language question that reflects what someone might ask an AI about this topic.
   - A post about "结营公示" might yield questions like "MindSpore 学习营获奖名单是什么？" or "怎么参加 MindSpore 学习营？"
   - A technical blog like "扩散模型系列——DDPM" might yield "DDPM 扩散模型的原理是什么？" or "MindSpore 怎么实现 DDPM？"
   - Preserve the specificity of the original post — do not over-generalize.
   - For each question, classify the category: installation, configuration, training, deployment, migration, troubleshooting, feature, performance, event, tutorial, other.

   {forum_posts_json}

   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang, source_title, source_views.
   ```
4. If the script fails (network error, API unavailable, exit code ≠ 0), fall back to LLM-generated usage questions:
   ```
   For the open-source community "{community}" with keywords "{seed_keywords}",
   generate typical usage questions that users would post on community forums.
   Cover: installation, configuration, training, deployment, migration, troubleshooting.
   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang.
   Generate 10-15 questions. Both zh and en.
   ```
5. Collect the output as the Path 1 question list.

**Step 4: Path 2 — Repo Issue Question Extraction (使用阶段) [PRIMARY]**

> This is a primary question source alongside forum. Repo issues reflect real developer problems.
> Only runs if `paths` includes `issue` or `all`.
> Requires `GITCODE_TOKEN` in `.env`.

1. Pre-validate the GitCode token before running the full fetch. Run:
   ```
   curl -s -o /dev/null -w "%{http_code}" \
     -H "private-token: {GITCODE_TOKEN}" \
     "https://api.gitcode.com/api/v5/user"
   ```
   If the HTTP status is not `200`, log `WARNING: GITCODE_TOKEN is invalid or expired (HTTP {status}). Skipping Path 2.` and skip to Step 5.
2. Run `GITCODE_TOKEN={GITCODE_TOKEN} python3 $SKILL_DIR/scripts/fetch-repo-issues.py --owner mindspore --repo mindspore --limit {limit}` to fetch issues.
   - The script calls GitCode API v5 (`api.gitcode.com`) with token auth.
   - Issues are sorted by comment count (engagement proxy).
   - See `$SKILL_DIR/references/gitcode-api-spec.md` for full API details.
3. If the script succeeds, prompt the LLM to rewrite issue titles into search questions:
   ```
   The following are real issue titles from the {community} repository on GitCode, sorted by engagement (comments).
   Rewrite them into natural language search questions that a developer might type into an AI assistant.

   Rules:
   - Filter out pure bug reports with only error stack traces and no general learning value.
   - Keep issues that represent common usage problems, feature requests, compatibility questions, and how-to questions.
   - Preserve the original intent — do not generalize too much.
   - For each question, classify the category: installation, configuration, training, deployment, migration, troubleshooting, feature, performance, compatibility.

   {issues_json}

   Output as JSON array with fields: question, category, scenario ("使用阶段"), lang, source_title, source_comments.
   ```
4. If the script fails (network error, API error), log warning and skip this path. Do NOT fall back to LLM generation — issue data should come from real sources.
5. Collect the output as the Path 2 question list.

**Step 5: Path 3 — Industry Question Discovery (了解阶段)**

> Only runs if `paths` includes `industry` or `all`.

1. Determine the community's domain hierarchy by prompting the LLM:
   ```
   Given the open-source community "{community}" with keywords "{seed_keywords}",
   determine:
   - Industry (行业)
   - Sub-domain (细分领域)
   - Positioning (定位)
   - Competitors (竞品, list 3-5)
   Output as JSON.
   ```
2. Using the domain hierarchy, generate questions across four user intents by prompting the LLM:
   ```
   Based on the following domain hierarchy:
   {domain_hierarchy_json}

   Generate search questions a user might ask when they do NOT know about {community}.
   Cover four intent categories:
   - 认知 (awareness): "What are the mainstream X?" type questions
   - 选型 (selection): "Which X should I choose?" type questions
   - 趋势 (trends): "What are the trends in X?" type questions
   - 场景 (scenarios): "What X works best for Y scenario?" type questions

   Also generate reverse-expansion questions using competitors:
   - "What alternatives to {competitor} exist?" type questions

   Output as JSON array with fields: question, intent, scenario ("了解阶段"), lang.
   Generate 10-15 questions total. Both zh and en.
   ```
3. Collect the output as the Path 3 question list.

**Step 6: Merge and Deduplicate**

1. Combine all question lists: manual + Path 1 + Path 2 + Path 3.
2. Prompt the LLM to perform semantic deduplication and classification:
   ```
   Merge the following question lists into a unified question set.
   Rules:
   - Remove semantically duplicate questions (similarity > 0.85). Keep the better-phrased version.
   - Manual questions have highest priority (keep all, mark source as "manual").
   - Forum-sourced questions (Path 1) and issue-sourced questions (Path 2) have second-highest priority.
   - Classify each question:
     - scenario: "了解阶段" or "使用阶段"
     - intent: "认知" / "选型" / "趋势" / "场景" / "教程" / "故障" / "特性" / "迁移"
     - lang: "zh" or "en"
   - Target: 30-40 questions total.
   - If total exceeds 40, prioritize by: manual > forum (path1) / issue (path2) > industry (path3).

   {all_questions_json}

   Output as JSON array with fields: id (q_001...), question, scenario, intent, lang, source, priority.
   ```
3. Validate the output with `python3 $SKILL_DIR/scripts/validate-questions.py` (reads from stdin).

**Step 7: Generate Output Files**

1. Write the validated JSON to `questions.json` in the project root.
2. Generate `questions.md` from the JSON using the template in `$SKILL_DIR/assets/questions-template.md`:
   - Group questions by scenario, then by intent.
   - Include a summary table at the top.
   - Mark source for each question (manual / path1-forum / path2-issue / path3-industry).
3. Print a summary to stdout:
   ```
   Question set generated:
     Total: {count}
     了解阶段: {count_awareness}
     使用阶段: {count_usage}
     Sources: manual({n}), path1-forum({n}), path2-issue({n}), path3-industry({n})
   Paths run: {paths_run}
   Output: questions.json, questions.md
   ```

**Step 8: Human Review Checkpoint**

1. PAUSE execution and display:
   ```
   ⏸ Human review checkpoint.
   Please review questions.md and provide feedback.
   - Delete questions that are not relevant.
   - Add missing questions.
   - Note any patterns to avoid/prefer in the future.

   After review, save feedback to feedback-rules.md.
   Then resume to continue the workflow.
   ```
2. Wait for the user to signal completion.

## Error Handling

* If `.env` is missing or `GITCODE_TOKEN` is not set, log warning and skip Path 2.
* If `$SKILL_DIR/scripts/fetch-forum-posts.py` fails (network error, API unavailable, exit code ≠ 0), fall back to LLM-generated usage questions (Step 3 fallback).
* If `GITCODE_TOKEN` fails pre-validation (HTTP ≠ 200), log warning and skip Path 2. If `$SKILL_DIR/scripts/fetch-repo-issues.py` fails at runtime, same behavior. Do not fall back to LLM generation — issue data must come from real sources.
* If `$SKILL_DIR/scripts/validate-questions.py` reports errors, display them and prompt the LLM to fix the JSON structure, then re-validate.
* If total question count is below 30 after dedup, prompt the LLM to generate additional questions to fill gaps in underrepresented intents.
* If only a subset of paths was selected and total count is low, that is expected — do not auto-fill unless below 10.
