# CLAUDE-RESUME.md

Session resume file for Claude Code. Read this at the start of every new conversation to restore context.

> **Keep this file up to date**: After any task that changes project state, update the relevant sections below.

## Project Overview

GEO (Generative Engine Optimization) Search Assessment — a system that automatically evaluates how well an open-source community (initially MindSpore) is represented across mainstream AI search platforms, then generates actionable improvement suggestions.

**Core workflow**: Define questions → Sample AI platforms → Score & diagnose → Output suggestions

**Design doc**: `GEO搜索能力诊断-初步设计方案.md` contains the full specification. `INPUT.md` contains the latest requirements update.

## Architecture

The system is a **skill chain orchestrated by AGENT.md**, not a web application. Pure CLI-driven via Claude Code.

4-step pipeline, each step is a separate skill:

1. **keyword-generator** — Generate question set from manual input + 3 auto paths
2. **platform-sampler** — Call 5 AI platform APIs with questions, collect responses
3. **scoring-engine** — LLM-based scoring across 4 dimensions, output comparison report
4. **improvement-advisor** — Generate P0-P2 improvement suggestions based on scores

Data flows as JSON between skills, with Markdown output for human review.

## Step 1 Design (keyword-generator) — AGREED

Question sources: manual input + 3 parallel auto-generation paths:

- **Manual input**: Community operators write questions in `manual-questions.md` (Markdown), skill auto-parses to structured JSON. No YAML needed.
- **Path 1: Industry question discovery (了解阶段)** — LLM determines community's domain hierarchy (industry → sub-domain → positioning → competitors), then generates questions by user intent (认知/选型/趋势/场景). Uses competitors for reverse expansion.
- **Path 2: Usage question extraction (使用阶段)** — Extract from Gitee/GitHub Issues + community forums. Filter pure bugs, cluster similar issues, LLM rewrites to natural language questions. (No official doc directory for now.)
- **Path 3: AI platform reverse extraction (使用阶段)** — Ask multiple AI platforms "what are the most common questions about {community}" and take intersection.

Merge (manual + 3 paths) → semantic dedup → classify → output `questions.json` + `questions.md`.

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
| `manual-questions.md` | (To create) Manual question input for keyword-generator |
| `feedback-rules.md` | (To create) Human review feedback for learning loop |

## Current Status

- **Phase**: Design complete for Step 1, ready to implement keyword-generator skill
- **Branch**: `main`
- **Last updated**: 2026-03-10

## TODO

- [ ] Create keyword-generator skill using `/skill-creator`
- [ ] Create platform-sampler skill
- [ ] Create scoring-engine skill
- [ ] Create improvement-advisor skill
- [ ] Create AGENT.md to orchestrate the full workflow
- [ ] Design feedback-rules.md format and integration
- [ ] Discuss 第一部分 (主流 AI 搜索平台分析) with user
- [ ] Discuss 第三部分 scoring weights for 5 platforms

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
| 2026-03-10 | Design doc: deleted 定期更新机制/中英文双语方案, renumbered sections, updated all references |

## Key Decisions

- Architecture is skill chain + AGENT.md, NOT web app (FastAPI/frontend deferred to Phase 3)
- Target community: MindSpore (AI computing framework, competitors: TensorFlow/PyTorch/PaddlePaddle/JAX)
- Data format: JSON between skills, Markdown for human review
- Manual questions: write in `manual-questions.md` (Markdown), skill auto-converts to JSON
- CHANGELOG only in English (`CHANGELOG.md`)
- Every commit must run `/release-skills` to update changelog
- New skills must use `/skill-creator` and conform to agentskills.io spec
- MVP platforms (5): Perplexity + ChatGPT + DeepSeek + 豆包 + Qwen
- API tokens stored in `.env`, template in `.env.example`
- Two scenarios in parallel: 了解阶段 (industry discovery) + 使用阶段 (usage extraction)
- Human review checkpoint after question generation, feedback saved to `feedback-rules.md`
- MVP question count: 30-40 (adjustable)
- No official doc directory as data source for now
- Scoring weights for 5 platforms: TBD (was 0.35/0.40/0.25 for 3 platforms)
