# GEO 搜索能力诊断：初步设计方案

## 背景与目标

### 场景定义

随着 ChatGPT、豆包、千问、DeepSeek 等 AI 搜索平台的普及，开发者越来越倾向于直接向 AI 提问而非使用传统搜索引擎。AI 平台的回答质量直接影响用户对开源社区的认知与选择——若 AI 给出错误或缺失的信息，用户往往归因于社区文档质量差，而非 AI 平台的局限性。

**GEO（Generative Engine Optimization，生成式引擎优化）** 是针对这一场景的系统性优化方法，目标是让 AI 搜索平台能够准确、完整地引用社区官方内容进行回答。

### 评估场景

目标用户为 **AI 开发者与研究人员**，其在 AI 搜索平台上的提问行为分为两个阶段：

| 阶段 | 典型场景 | 用户意图 | GEO 优化目标 |
|------|---------|---------|-------------|
| **了解阶段** | 搜索行业大类问题（如"主流深度学习框架有哪些"） | 尚未了解社区，处于认知与选型阶段 | 确保社区在 AI 回答中被提及，且定位描述准确 |
| **使用阶段**（重点）| 搜索具体操作问题（如"MindSpore 安装教程"） | 已知社区，寻求具体技术指引 | 确保 AI 回答准确引用官方文档，不出现错误信息或编造内容 |

当前 MVP 阶段聚焦**使用阶段**，以 **MindSpore** 为初始评估社区。

## 目标用户

本工具面向**开源社区运营人员**，给定一个开源社区，自动完成主流 AI 平台的 GEO 搜索能力判断，输出结构化的改进建议报告（`suggestions.md`），并自动将每条建议创建为社区 Issue。

## 系统架构

采用 **skill chain + AGENT.md 编排**，纯 CLI 驱动，通过 Claude Code 自动执行。

```
AGENT.md（工作流编排）
  │
  ├── Step 1: get-question skill
  │     输入：社区名称
  │     输出：questions.json + questions.md
  │     ⏸ 人工审阅检查点
  │     ⏸ 人工标注 content-labels.json（每个问题标注官网是否有内容）
  │
  ├── Step 2: platform-sampler skill
  │     输入：questions.json
  │     输出：responses.json + responses.md
  │
  ├── Step 3: scoring-engine skill
  │     输入：responses.json + content-labels.json
  │     输出：scoring-results.json + suggestions.md
  │     ⏸ 人工抽检校准（20%）
  │
  └── Step 4: issue-creator skill
        输入：suggestions.md / scoring-results.json
        输出：GitCode Issues（每条建议 → 一个 Issue）
```

数据流：JSON 在 skill 之间传递，Markdown 供人类审阅。

---

## 执行步骤

### 步骤一：生成问题集（get-question skill）

**目标**：输入社区名称，输出覆盖场景的问题集。

问题来源：手动输入 + 三条自动生成路径（可在 skill 中单选或全选）

**0: 开发者采访反馈**

社区运营人员提供 Markdown 文档（`manual-questions.md`），skill 自动解析并转换为结构化 JSON。

**1：论坛使用问题提取（主要）**

目标：从社区论坛的真实用户问题中提取高频使用类问题。论坛和 Issue 是最主要的问题来源。

```
Discourse API (discuss.mindspore.cn)
  → 获取问题求助、MindSpore Lite 等分类
  → 按浏览量排序（/l/top.json?period=all）
  → LLM 改写为自然语言搜索问题，过滤博客/活动帖子
```

**2：仓库 Issue 提取（主要）**

目标：从社区仓库的真实 Issue 中提取高频使用类问题。Issue 和论坛同为主要问题来源。

```
GitCode API (api.gitcode.com) → 需要 GITCODE_TOKEN
  → 获取 mindspore/mindspore 仓库 Issue
  → 按评论数排序（参与度代理）
  → LLM 改写为自然语言搜索问题，过滤纯 bug 报告
```

**3：行业问题发现**

目标：生成用户在不知道 MindSpore 时可能搜索的行业大类问题，覆盖「了解阶段」。

```
社区名称 → LLM 确定领域层级（行业/细分/定位/竞品）
         → 按用户意图分类生成问题（认知/选型/趋势/场景）
         → 用竞品做反向扩展
```

合并（手动 + 已选路径）→ 语义去重 → 分类标注 → 输出 `questions.json` + `questions.md`

**人工审阅检查点**：生成后暂停，等待人工筛选反馈。反馈保存到 `feedback-rules.md`，后续自动融入生成 prompt（学习循环）。

---

### 步骤二：多平台搜索采样（platform-sampler skill）

**目标**：调用各 AI 平台 API，用问题集采样，采集原始回答。

**判断逻辑**：

- **用户-产品匹配**：MindSpore 的目标用户是 AI 开发者和研究人员，优先关注开发者浓度高的平台
- **API 可用性**：自动方案需要 API 支持，这也是一个筛选条件

MVP 阶段聚焦 **ChatGPT + DeepSeek + 豆包 + Qwen** 四个平台：

- **ChatGPT**：全球通用，用户基数最大，代表主流 AI 搜索行为
- **DeepSeek**：国内技术社区，开发者浓度高
- **豆包**：国内年轻用户群体，字节系流量入口
- **Qwen**：阿里系，国内开发者和企业用户覆盖

四者均有 API 支持，可实现自动化采样。

---

### 步骤三：分析和建议（scoring-engine skill）

**目标**：对采样结果进行两层评估，生成分优先级的可执行改进建议。

**评估框架（两层）**：

```
第一层：内容完整性（官方有没有内容）
  → 每个问题预先人工标注 content_exists: true/false
  → content_exists = false → 直接标记 P0 内容缺口，不进入第二层

第二层：引用准确性（仅对 content_exists = true 的问题）
  → LLM 判定 AI 回答属于哪种现象（B/C/D/E）
  → 计算官方源引用比例
```

**五种现象分类**：

| 代号 | 现象 | 评分 | GEO 优化方向 |
|------|------|------|-------------|
| A | 官网无内容 | 不评分（无基准） | **P0: 补内容** — 社区内容缺失 |
| B | 官网有但没引用 | 低分 | **SEO/结构化** — 提升官方内容可检索性和权威信号 |
| C | 官网有但引用了错误信息 | 最低分 | **P0: 纠错** — 比没引用更危险（细分：过时信息 vs 幻觉） |
| D | 官网有，引用比例大 | 高分 | 持续监控，无需行动 |
| E | 官网有但引用比例小 | 中等分 | **优化内容密度** — 增加官方内容深度和覆盖面 |

**引用比例定义**：来源级别 — 回答引用的所有来源中，官方源（官网、官方仓库等）占比。

**评分输出（每个问题 × 每个平台）**：

```json
{
  "question_id": "q_001",
  "platform": "ChatGPT",
  "content_exists": true,
  "citation_type": "B",
  "official_source_ratio": 0.2,
  "accuracy_score": 4,
  "severity": "P1",
  "details": "..."
}
```

**优先级规则**：

- **P0**：现象 A（内容缺口）或 C（错误引用）
- **P1**：现象 B（有内容未引用）或 E（引用比例低）
- **P2**：现象 D 但有小瑕疵
- 无需行动：现象 D 且无瑕疵

**输入**：
- `responses.json`（平台采样结果）
- `content-labels.json`（人工标注：每个问题的 `content_exists` + 官方内容 URL）

**输出**：
- `scoring-results.json`（机器可读评分结果）
- `suggestions.md`（改进建议报告）

**人工抽检校准**：

```
LLM 自动评分 → scoring-results.json
  → 人工分层抽检 20%（每个 severity 级别各抽几个）
  → 校准偏差记录到 scoring-calibration.md
  → 下一轮评分时作为 prompt context 融入 LLM（学习循环）
```

---

### 步骤四：Issue 自动创建（issue-creator skill）

**目标**：将改进建议自动创建为 GitCode 仓库 Issue，便于社区跟踪和分配。

**输入**：`suggestions.md` 或 `scoring-results.json`

**输出**：GitCode Issue（每条改进建议 → 一个 Issue）

**Issue 格式**：

```
标题: [GEO-{severity}] {问题简述} — {平台}
标签: geo-improvement, {severity}, {category}
正文:
  ## 问题
  {具体现象描述，含现象代号 A/B/C/D/E}
  ## 影响平台
  {受影响的 AI 平台列表}
  ## 建议改进
  {具体操作步骤}
  ## 参考
  {原始问题 + AI 回答截取}
```

**API**：`POST api.gitcode.com/api/v5/repos/{owner}/{repo}/issues`（复用 `GITCODE_TOKEN`）