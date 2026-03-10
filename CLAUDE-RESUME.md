# CLAUDE-RESUME.md

Session resume file for Claude Code. Read this at the start of every new conversation to restore context.

> **Keep this file up to date**: After any task that changes project state, update the relevant sections below.

## Project Overview

GEO (Generative Engine Optimization) Search Assessment — a system that automatically evaluates how well an open-source community (initially openEuler) is represented across mainstream AI search platforms, then generates actionable improvement suggestions.

**Core workflow**: Define keywords → Sample AI platforms → Score & diagnose → Output suggestions

**Design doc**: `GEO搜索能力诊断-初步设计方案.md` contains the full specification with open design questions tracked in tables.

## Architecture (Planned)

The system follows a 4-step pipeline:

1. **Keyword Management** — Manual YAML input + auto-extraction from Gitee/GitHub Issues and forums. Bilingual (zh/en). Weekly incremental + monthly full re-clustering.
2. **Multi-Platform Sampling** — Unified sampler interface with per-platform adapters (PerplexitySampler, ChatGPTSampler, DeepSeekSampler). Results stored with citations, mentions, and raw responses.
3. **Diagnostic Scoring** — LLM-based scoring across 4 dimensions: mention (0-3), citation (0-3), accuracy (0-2), ranking (0-2). Per-keyword per-platform, aggregated with weights: Perplexity×0.35 + ChatGPT×0.40 + DeepSeek×0.25.
4. **Output** — Frontend dashboard (React/Vue + ECharts), Excel export (openpyxl), improvement suggestions with P0-P2 priority.

**Planned tech stack**: Python (FastAPI), PostgreSQL, LLM APIs (Perplexity/OpenAI/DeepSeek), Celery Beat for scheduling.

## Current Status

- **Phase**: Design & planning (pre-code)
- **Branch**: `main`
- **Last updated**: 2026-03-10

## TODO

- [ ] Finalize open design questions in `GEO搜索能力诊断-初步设计方案.md`
- [ ] Set up Python project structure (FastAPI scaffold)
- [ ] Design keyword YAML config format
- [ ] Implement platform sampler adapters
- [ ] Design LLM scoring prompt templates
- [ ] Set up PostgreSQL schema

## Recent Changes

| Date | Change |
|------|--------|
| 2026-03-10 | Initialized repository with design doc |
| 2026-03-10 | Installed release-skills and skill-creator to `.claude/skills/` |
| 2026-03-10 | Configured CLAUDE.md development rules (rules 1-10) |
| 2026-03-10 | Created CLAUDE-RESUME.md for session context recovery |

## Key Decisions

- CHANGELOG only in English (`CHANGELOG.md`), no multi-language variants
- Every commit must run `/release-skills` to update changelog
- New skills must use `/skill-creator` and conform to agentskills.io spec
- MVP platforms: Perplexity + ChatGPT + DeepSeek
