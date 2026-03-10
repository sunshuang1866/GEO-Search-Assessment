# CLAUDE-RESUME.md

Session resume file for Claude Code. Read this at the start of every new conversation to restore context.

> **Keep this file up to date**: After any task that changes project state, update the relevant sections below.

## Project Overview

GEO (Generative Engine Optimization) Search Assessment — a system that automatically evaluates how well an open-source community (initially openEuler) is represented across mainstream AI search platforms, then generates actionable improvement suggestions.

**Core workflow**: Define keywords → Sample AI platforms → Score & diagnose → Output suggestions

**Design doc**: `GEO搜索能力诊断-初步设计方案.md` contains the full specification. `INPUT.md` contains the latest requirements update.

## Architecture

The system is a **skill chain orchestrated by AGENT.md**, not a web application. Pure CLI-driven via Claude Code.

4-step pipeline, each step is a separate skill:

1. **keyword-generator** — Generate question set from community name + seed keywords
2. **platform-sampler** — Call AI platform APIs with questions, collect responses
3. **scoring-engine** — LLM-based scoring across 4 dimensions, output comparison report
4. **improvement-advisor** — Generate P0-P2 improvement suggestions based on scores

Data flows as JSON between skills, with Markdown output for human review.

## Step 1 Design (keyword-generator) — AGREED

Three parallel generation paths:

- **Path 1: Industry question discovery (了解阶段)** — LLM determines community's domain hierarchy (industry → sub-domain → positioning → competitors), then generates questions by user intent (认知/选型/趋势/场景). Uses competitors for reverse expansion.
- **Path 2: Usage question extraction (使用阶段)** — Extract from Gitee/GitHub Issues + community forums. Filter pure bugs, cluster similar issues, LLM rewrites to natural language questions. (No official doc directory for now.)
- **Path 3: AI platform reverse extraction** — Ask multiple AI platforms "what are the most common questions about {community}" and take intersection.

Merge → semantic dedup → classify → output `questions.json` + `questions.md`.

**Human review checkpoint**: After generating questions, PAUSE for human review. Human filters and provides feedback. Feedback is saved to `feedback-rules.md` and incorporated into future question generation as prompt context (learning loop).

**Quantity**: 30-40 questions for MVP (adjustable based on results).

**Output format**: `questions.json` (machine) + `questions.md` (human review). Bilingual zh/en.

## Current Status

- **Phase**: Designing Step 1 (keyword-generator skill)
- **Branch**: `main`
- **Last updated**: 2026-03-10

## TODO

- [ ] Create keyword-generator skill using `/skill-creator`
- [ ] Create platform-sampler skill
- [ ] Create scoring-engine skill
- [ ] Create improvement-advisor skill
- [ ] Create AGENT.md to orchestrate the full workflow
- [ ] Design feedback-rules.md format and integration

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
| 2026-03-10 | Agreed on Step 1 design: 3 paths, human review checkpoint, feedback loop |

## Key Decisions

- Architecture is skill chain + AGENT.md, NOT web app (FastAPI/frontend deferred)
- Data format: JSON between skills, Markdown for human review
- CHANGELOG only in English (`CHANGELOG.md`)
- Every commit must run `/release-skills` to update changelog
- New skills must use `/skill-creator` and conform to agentskills.io spec
- MVP platforms: Perplexity + ChatGPT + DeepSeek
- Two scenarios in parallel: 了解阶段 (industry discovery) + 使用阶段 (usage extraction)
- Human review checkpoint after question generation, feedback saved to `feedback-rules.md`
- MVP question count: 30-40 (adjustable)
- No official doc directory as data source for now
