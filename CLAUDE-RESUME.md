# CLAUDE-RESUME.md

Session resume file for Claude Code. Read this at the start of every new conversation to restore context.

> **Keep this file up to date**: After any task that changes project state, update the relevant sections below.

## Project Overview

GEO (Generative Engine Optimization) Search Assessment — a system that automatically evaluates how well an open-source community (initially MindSpore) is represented across mainstream AI search platforms, then generates actionable improvement suggestions.

**Core workflow**: Define questions → Sample AI platforms → Score & diagnose → Output suggestions

**Design doc**: `GEO搜索能力诊断-初步设计方案.md` contains the full specification. `INPUT.md` contains the latest requirements update.

## Architecture

The system is a **skill chain orchestrated by AGENT.md**, not a web application. Pure CLI-driven via Claude Code.

4-step pipeline (execution steps), each step is a separate skill:

1. **get-question** — Generate question set from manual input + 3 auto paths (forum, issue, industry)
2. **platform-sampler** — Call 4 AI platform APIs with questions, collect responses
3. **scoring-engine** — Two-layer evaluation (content completeness + citation accuracy), generate P0-P2 improvement suggestions
4. **issue-creator** — Auto-create GitCode Issues from improvement suggestions

Data flows as JSON between skills, with Markdown output for human review.

## Step 1 Design (get-question) — AGREED

Question sources: manual input + 4 selectable auto-generation paths (`paths` param: `forum`, `issue`, `industry`, `ai_reverse`, `all`)

- **Manual input**: Community operators write questions in `manual-questions.md` (Markdown), skill auto-parses to structured JSON. No YAML needed.
- **Path 1 (PRIMARY): Forum usage question extraction (使用阶段)** — Fetch top topics from MindSpore Discourse forum (`https://discuss.mindspore.cn`) via API. Fetches from 问题求助 Help + MindSpore Lite categories + global top. LLM rewrites titles to search questions, filters pure bugs. Forum + issues are the primary question source.
- **Path 2 (PRIMARY): Repo issue question extraction (使用阶段)** — Fetch issues from GitCode (`https://gitcode.com/mindspore/mindspore/issues`) via API (`api.gitcode.com/api/v5`). Requires `GITCODE_TOKEN`. Sorted by comments, LLM rewrites to search questions. No LLM fallback — skip if no token.
- **Path 3: Industry question discovery (了解阶段)** — LLM determines community's domain hierarchy (industry → sub-domain → positioning → competitors), then generates questions by user intent (认知/选型/趋势/场景). Uses competitors for reverse expansion.
Merge (manual + selected paths) → semantic dedup → classify → output `questions.json` + `questions.md`.

Priority: manual > forum (path1) / issue (path2) > multi-source > single-source.

**Human review checkpoint**: After generating questions, PAUSE for human review. Human filters and provides feedback. Feedback is saved to `feedback-rules.md` and incorporated into future question generation as prompt context (learning loop).

**Quantity**: 30-40 questions for MVP (adjustable based on results).

**Output format**: `questions.json` (machine) + `questions.md` (human review). Bilingual zh/en.

## Design Doc Structure

`GEO搜索能力诊断-初步设计方案.md` sections:

- **总览**: 系统架构 + 执行步骤(1-4) + 总体开发路线 + 待讨论问题汇总
- **第一部分(一~五)**: 主流 AI 搜索平台分析 — 平台分类、优先级、API 可用性、MVP 结论
- **第二部分(六~九)**: 关键词定义策略 — 手动输入(Markdown)、自动生成(3 paths)、合并去重、技术要点
- **第三部分(十~十四)**: 评分体系与输出规范（待讨论）— 评分指标、GEO 评分体系、改进建议、Excel 导出、技术方案

已删除的节: 定期更新机制(原九)、中英文双语方案(原十)

## Key Files

| File | Purpose |
|------|---------|
| `GEO搜索能力诊断-初步设计方案.md` | Full design specification |
| `INPUT.md` | Original user requirements |
| `CLAUDE.md` | Development rules (11 rules) |
| `CLAUDE-RESUME.md` | Session recovery (this file) |
| `README.md` | Usage rules for developers |
| `CHANGELOG.md` | Release changelog (English only) |
| `VERSION` | Current version (0.1.0) |
| `.env.example` | API token template (6 platforms) |
| `.gitignore` | Excludes `.env` from git |
| `manual-questions.md` | (To create) Manual question input for get-question |
| `feedback-rules.md` | (To create) Human review feedback for learning loop |
| `GEO-Improvement-Report-Q8-Q10.md` | GEO improvement report for FAQ questions Q8-Q10 |
| `GEO-Improvement-Report-Q4-Q7.md` | GEO improvement report for Q4-Q7 (activities, contribution, migration, version) |
| `GEO-Improvement-Report-Q1-Q3.md` | GEO improvement report for Q1-Q3 (broad questions: install, version cadence, data sharding) |
| `Answers/1.md` - `Answers/10.md` | Raw AI platform responses for Q1-Q10 |
| `scoring-results.json` | Scoring engine output: 28 scored (question, platform) pairs |
| `suggestions.md` | GEO scoring report with prioritized improvement suggestions |

## Skills Created

| Skill | Directory | Status |
|-------|-----------|--------|
| get-question | `.claude/skills/get-question/` | ✅ Complete |
| platform-sampler | `.claude/skills/platform-sampler/` | ✅ Complete |
| scoring-engine | `.claude/skills/scoring-engine/` | ✅ Complete |
| issue-creator | `.claude/skills/issue-creator/` | ✅ Complete |
| improvement-advisor | `.claude/skills/improvement-advisor/` | ✅ Complete |

### get-question
- 8-step procedure: Load config → Parse manual → Path 1 (forum) → Path 2 (issue) → Path 3 (industry LLM) → Merge & dedup → Output → Human review
- Path 4 (AI reverse extraction) removed — data must come from real sources, not AI self-report
- Forum: all content types included (technical, events, blogs, announcements) — views are relevance filter, not content type
- Forum endpoint: `/c/{slug}/{id}/l/top.json?period=all` (views-sorted, not latest activity)
- Scripts: `parse-manual-questions.py`, `fetch-forum-posts.py`, `fetch-repo-issues.py`, `validate-questions.py`
- References: `forum-api-spec.md`, `gitcode-api-spec.md`
- Assets: `questions-template.md`

### platform-sampler
- 5-step procedure: Load config → Load questions → Sample platforms → Post-process (LLM metadata extraction) → Validate & output
- Scripts: `sample-platform.py`, `validate-input.py`, `validate-responses.py`
- References: `platform-rate-limits.md`
- Assets: `responses-template.md`
- Post-processing extracts: mentions_community, community_description, competitors_mentioned, recommendation_position, citations_to_official

### scoring-engine
- 6-step procedure: Validate inputs → Layer 1 (content completeness) → Layer 2 (citation accuracy, LLM) → Assign severity & suggestions → Compile output → Human spot-check
- Scripts: `validate-inputs.py`, `parse-llm-score.py`, `select-spot-check.py`
- References: `scoring-prompt-template.md`, `suggestion-rules.md`
- Assets: `suggestions-template.md`
- Two-layer model: Layer 1 = human-labeled `content_exists`, Layer 2 = LLM evaluates phenomena B/C/D/E
- Outputs: `scoring-results.json`, `suggestions.md`

### issue-creator
- 5-step procedure: Load config → Parse scoring results → Deduplicate & group → Generate Issue payloads → Output summary
- Scripts: `parse-suggestions.py`, `create-issue.py`
- References: `gitcode-api-spec.md`
- Assets: `issue-template.md`
- Supports dry-run mode, outputs `created-issues.json`

## Current Status

- **Phase**: All 4 pipeline skills created. Scoring-engine analysis completed for Q1,Q4,Q5,Q7,Q9,Q10. GEO improvement reports created for all Q1-Q10.
- **Scoring results**: `scoring-results.json` (28 scored pairs) + `suggestions.md` (7-section report)
- **Key findings**: 5 P0 issues (all Type C citation errors), concentrated in 豆包 (3) and DeepSeek (2). Perplexity and 千问 perform best. Q1 (install) is benchmark case — 0% hallucination. Q9 (model format) has highest divergence across platforms.
- **Q1-Q3 analysis**: Q1 (install) best-answered across all platforms (proves good docs→good AI answers). Q2: no official version strategy doc → platforms guess wildly. Q3: all correct (num_shards/shard_id).
- **Q4-Q7 analysis**: SPA pages (activities/contribution) are root GEO blocker. Q6: 3/5 platforms fabricate non-existent APIs. Q7: 豆包 fabricates extensive fake features. 千问 and Perplexity perform best.
- **Q8-Q10 analysis**: Q9 is the worst — 3/4 platforms incorrectly claim MindSpore can "directly read" PyTorch/TF models. Q10: 豆包 completely off-topic (answered as big data ETL), DeepSeek returned irrelevant content. 千问 is the best performer across all 3 questions.
- **Branch**: `main`
- **Last updated**: 2026-03-13

## TODO

- [x] Create get-question skill using `/skill-creator`
- [x] Create platform-sampler skill using `/skill-creator`
- [x] Create scoring-engine skill (design agreed, needs `/skill-creator`)
- [x] Create issue-creator skill
- [x] Create improvement-advisor skill
- [ ] Create AGENT.md to orchestrate the full workflow
- [ ] Design feedback-rules.md format and integration
- [ ] Discuss 第一部分 (主流 AI 搜索平台分析) with user
- [x] Create `content-labels.json` template (human labels: content_exists per question)
- [ ] Design scoring LLM Prompt template (待设计 3.3)

## Recent Changes

| Date | Change |
|------|--------|
| 2026-03-10 | Initialized repository with design doc |
| 2026-03-10 | Installed release-skills and skill-creator to `.claude/skills/` |
| 2026-03-10 | Configured CLAUDE.md development rules (rules 1-11) |
| 2026-03-10 | Created CLAUDE-RESUME.md for session context recovery |
| 2026-03-10 | Created README.md with usage rules |
| 2026-03-10 | Released v0.1.0 |
| 2026-03-10 | Agreed on total architecture: skill chain + AGENT.md orchestration |
| 2026-03-10 | Agreed on Step 1 design: 3 paths + manual input, human review checkpoint, feedback loop |
| 2026-03-10 | Changed target community from openEuler to MindSpore (competitors: TensorFlow/PyTorch) |
| 2026-03-10 | Revised 第二部分: manual input via Markdown, auto-generation aligned with 3 paths |
| 2026-03-10 | MVP platforms expanded to 5: +豆包(火山引擎) +Qwen(阿里云百炼), scoring weights TBD |
| 2026-03-10 | Created `.env.example` (6 platform API keys) and `.gitignore` |
| 2026-03-10 | Created get-question skill (8 steps, 4 scripts, follows agentskills.io spec) |
| 2026-03-10 | Path 2 simplified: removed Issue extraction, forum posts only |
| 2026-03-10 | Created platform-sampler skill (5 steps, 3 scripts, follows agentskills.io spec) |
| 2026-03-12 | Analyzed Q8-Q10 (official FAQ) across 5 AI platforms, identified critical issues |
| 2026-03-12 | Created GEO-Improvement-Report-Q8-Q10.md with root cause analysis and optimization roadmap |
| 2026-03-12 | Added universal GEO recommendations (5.1-5.7) to improvement report |
| 2026-03-12 | Created improvement-advisor skill (7 steps, 2 scripts, 2 references, 1 asset template) |
| 2026-03-12 | 设计文档重新排版：执行步骤合并为三步，MVP 平台调整为 4 个（移除 Perplexity） |
| 2026-03-12 | get-question: Forum→Path 1 (primary), Industry→Path 2, AI reverse→Path 3. Added `paths` selector. |
| 2026-03-12 | fetch-forum-posts.py: Implemented Discourse API integration (discuss.mindspore.cn), no longer placeholder |
| 2026-03-12 | forum-api-spec.md: Updated with real Discourse endpoints, categories, and topic object schema |
| 2026-03-12 | Design doc 步骤一: Reordered paths, forum as primary, added path selectability |
| 2026-03-12 | Added Path 2 (issue): GitCode repo issue extraction via api.gitcode.com (requires GITCODE_TOKEN) |
| 2026-03-12 | Created fetch-repo-issues.py and references/gitcode-api-spec.md |
| 2026-03-12 | Now 4 paths: forum, issue, industry, ai_reverse (was 3) |
| 2026-03-16 | Removed Path 4 (ai_reverse): circular reasoning risk, replaced by real data sources only |
| 2026-03-16 | Fixed forum fetch endpoint to /l/top.json (views-sorted) instead of latest activity |
| 2026-03-16 | Removed QUESTION_CATEGORY_IDS filter: all forum content types now included |
| 2026-03-16 | Added SKILL_DIR variable to SKILL.md Step 1 to fix script path resolution |
| 2026-03-16 | Added GitCode token pre-validation (curl) before running fetch-repo-issues.py |
| 2026-03-12 | Scoring design agreed: two-layer (content completeness + citation accuracy), 5 phenomena (A-E) |
| 2026-03-12 | content_exists = human pre-labeled, citation ratio = source-level, human spot-check 20% |
| 2026-03-12 | Issue auto-creation = separate skill (issue-creator), not inside scoring-engine |
| 2026-03-12 | Pipeline expanded to 4 steps: get-question → platform-sampler → scoring-engine → issue-creator |
| 2026-03-12 | Ran scoring-engine on Q1,Q4,Q5,Q7,Q9,Q10 (28 pairs). Output: scoring-results.json + suggestions.md |
| 2026-03-13 | Created GEO-Improvement-Report-Q8-Q10.md: analyzed Q8-Q10 against official FAQ sources, identified P0 issues |
| 2026-03-13 | Created GEO-Improvement-Report-Q4-Q7.md: analyzed Q4-Q7 (activities, contribution, PyTorch migration, v2.8.0 features) |
| 2026-03-13 | Created GEO-Improvement-Report-Q1-Q3.md: analyzed Q1-Q3 (install, version cadence, data sharding), completed full Q1-Q10 analysis |

## Key Decisions

- Architecture is skill chain + AGENT.md, NOT web app (FastAPI/frontend deferred to Phase 3)
- Target community: MindSpore (AI computing framework, competitors: TensorFlow/PyTorch/PaddlePaddle/JAX)
- Data format: JSON between skills, Markdown for human review
- Manual questions: write in `manual-questions.md` (Markdown), skill auto-converts to JSON
- CHANGELOG only in English (`CHANGELOG.md`)
- Every commit must run `/release-skills` to update changelog
- New skills must use `/skill-creator` and conform to agentskills.io spec
- MVP platforms (4): ChatGPT + DeepSeek + 豆包 + Qwen（Perplexity 已移除）
- API tokens stored in `.env`, template in `.env.example`
- Two scenarios in parallel: 了解阶段 (industry discovery) + 使用阶段 (usage extraction)
- Forum (Discourse API) is primary question source; all 3 paths selectable via `paths` param (forum, issue, industry)
- Path 4 (AI reverse extraction) permanently removed — circular reasoning risk; real data only
- Forum includes all content types (not filtered by category type); views = relevance signal
- Forum URL: https://discuss.mindspore.cn/ (Discourse, public API, no auth needed)
- Human review checkpoint after question generation, feedback saved to `feedback-rules.md`
- MVP question count: 30-40 (adjustable)
- No official doc directory as data source for now
- Pipeline is 4 execution steps: get-question → platform-sampler → scoring-engine → issue-creator
- Scoring uses two-layer model: Layer 1 = content completeness (human pre-labeled), Layer 2 = citation accuracy (LLM)
- Five phenomena: A (no content), B (not cited), C (wrong citation), D (high ratio), E (low ratio)
- Citation ratio = source-level (official sources / total sources), not content word count
- `content_exists` per question is human pre-labeled in `content-labels.json`
- Scoring results require human spot-check calibration (20% stratified sampling → `scoring-calibration.md`)
- Issue auto-creation is a separate skill (issue-creator), uses same GITCODE_TOKEN
