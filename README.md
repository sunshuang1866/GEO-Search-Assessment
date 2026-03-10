# GEO Search Assessment

GEO（Generative Engine Optimization）搜索能力诊断系统 —— 自动评估开源社区在主流 AI 搜索平台中的表现，并生成可执行的改进建议。

初始目标社区：**MindSpore**。

## 系统架构

本系统是一个由 Claude Code 驱动的 **Skill 链式流水线**，纯 CLI 运行，无 Web 界面。

4 步流水线，每步对应一个独立 Skill：

```
questions.json        responses.json        scores.json        suggestions.json
     │                     │                     │                     │
     ▼                     ▼                     ▼                     ▼
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────────┐
│ keyword  │────▶│   platform   │────▶│   scoring    │────▶│   improvement    │
│ generator│     │   sampler    │     │   engine     │     │   advisor        │
└──────────┘     └──────────────┘     └──────────────┘     └──────────────────┘
  生成问题集         采样 AI 平台          评分诊断            生成改进建议
```

**数据流**：Skill 之间通过 JSON 文件传递数据，同时输出 Markdown 供人工审阅。

## Skill 进度

| Skill | 目录 | 状态 |
|-------|------|------|
| keyword-generator | `.claude/skills/keyword-generator/` | ✅ 已完成 |
| platform-sampler | `.claude/skills/platform-sampler/` | ✅ 已完成 |
| scoring-engine | — | 🔲 待创建 |
| improvement-advisor | — | 🔲 待创建 |

### keyword-generator（问题集生成）

从 4 个来源生成问题集并合并去重：

- **手动输入**：社区运营者在 `manual-questions.md` 中编写问题
- **Path 1 — 行业发现**：LLM 推导社区所属行业层级，按用户意图（认知/选型/趋势/场景）生成问题
- **Path 2 — 社区论坛**：从 Gitee/GitHub Issues 和社区论坛提取使用阶段问题
- **Path 3 — AI 平台反向提取**：询问多个 AI 平台"关于该社区最常见的问题"，取交集

输出 `questions.json`（机器读取）+ `questions.md`（人工审阅），生成后暂停等待人工反馈。

### platform-sampler（平台采样）

将问题集发送到 5 个 AI 搜索平台，收集原始回答：

- Perplexity、ChatGPT、DeepSeek、豆包、通义千问

采样后通过 LLM 后处理提取结构化元数据（是否提及社区、描述准确性、竞品排位等）。

输出 `responses.json` + `responses.md`。

## 快速开始

### 1. 配置 API Token

```bash
cp .env.example .env
# 编辑 .env，填入各平台的 API Key
```

需要配置的平台：Perplexity、OpenAI、DeepSeek、豆包（火山引擎）、通义千问（阿里云百炼）、Kimi（月之暗面）。

### 2. 准备手动问题（可选）

创建 `manual-questions.md`，按 Markdown 格式编写社区相关问题。

### 3. 运行 Skill

在 Claude Code 中按顺序调用各 Skill，每步产出的 JSON 文件作为下一步的输入。

## 项目文件

| 文件 | 用途 |
|------|------|
| `GEO搜索能力诊断-初步设计方案.md` | 完整设计文档 |
| `INPUT.md` | 原始需求文档 |
| `.env.example` | API Token 配置模板（6 个平台） |
| `CLAUDE.md` | Claude Code 开发规则 |
| `CLAUDE-RESUME.md` | 会话恢复文件，记录项目状态和待办 |
| `CHANGELOG.md` | 变更日志，由 `/release-skills` 自动维护 |
| `VERSION` | 当前版本号 |

## 使用 Claude Code 开发

本仓库使用 [Claude Code](https://claude.ai/code) 作为主要开发工具，配置了自动化工作流和会话恢复机制。

### CLAUDE-RESUME.md —— 会话恢复

每次开启新的 Claude Code 会话时，Claude 会自动读取 `CLAUDE-RESUME.md` 来恢复项目上下文，无需重复说明背景。

该文件包含以下段落，**每次任务完成后自动更新**：

- **Project Overview** — 项目概述和架构
- **Current Status** — 当前开发阶段
- **TODO** — 待办事项清单
- **Recent Changes** — 近期变更记录
- **Key Decisions** — 已确定的关键决策

**约束**：
- 不要手动编辑此文件，由 Claude Code 自动维护
- 如需修正内容，在会话中告知 Claude 更新即可

### /release-skills —— 发布与变更日志

在 Claude Code 中执行 `/release-skills`，自动完成版本管理和 CHANGELOG.md 更新。

```
/release-skills              # 自动检测版本变更
/release-skills --dry-run    # 仅预览，不执行
/release-skills --major      # 强制主版本号升级
/release-skills --minor      # 强制次版本号升级
/release-skills --patch      # 强制补丁版本号升级
```

**约束**：
- 每次 git commit 前**必须**先执行 `/release-skills` 更新 CHANGELOG.md
- 不允许跳过此步骤直接提交
- CHANGELOG 仅维护英文版本（`CHANGELOG.md`）

### /skill-creator —— 创建新 Skill

在 Claude Code 中执行 `/skill-creator`，按照 [agentskills.io](https://agentskills.io) 规范创建新的 skill。

**工作流**：

1. 定义 skill 的 `name` 和 `description`，执行元数据校验脚本
2. 创建目录结构：`scripts/`、`references/`、`assets/`
3. 基于模板撰写 `SKILL.md`，使用第三人称祈使语气
4. 识别脆弱任务，封装为 `scripts/` 下的独立脚本
5. 最终校验，对照 `references/checklist.md` 检查

**约束**：
- 创建新 skill 时**必须**使用 `/skill-creator`，不允许手动创建
- `SKILL.md` 主体逻辑不超过 500 行，超出部分拆分到 `references/`
- `name` 仅允许小写字母、数字和单连字符，1-64 字符
- `description` 不超过 1024 字符，使用第三人称，包含反向触发条件

## 开发规则摘要

完整规则见 `CLAUDE.md`，以下为关键要求：

1. 写代码前先描述方案，等待批准
2. 需求不明确时先提问，不要猜测
3. 单次任务涉及超过 3 个文件时，先拆分为小任务
4. 修 bug 先写复现测试
5. 每次 commit 前执行 `/release-skills`
6. 创建 skill 使用 `/skill-creator`
7. 每次任务完成后更新 `CLAUDE-RESUME.md`

## License

MIT
