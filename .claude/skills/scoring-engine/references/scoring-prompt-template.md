# Scoring Prompt Template

Use this template to construct the LLM evaluation prompt for each (question, platform) pair in Layer 2.

## Prompt

```
你是一个 GEO（Generative Engine Optimization）评分专家。请分析以下 AI 平台回答，评估其对官方内容的引用准确性。

## 待评估信息

**问题**: {question}
**平台**: {platform}
**AI 回答**:
{response_text}

**官方内容参考**:
- 内容覆盖度: {content_coverage}
- 官方 URL: {official_urls}

{calibration_context}

## 评估任务

1. **识别来源**: 列出回答中引用或提及的所有信息来源（显式 URL、命名来源、隐含引用）。
2. **分类来源**: 将每个来源标记为 "official"（匹配以下官方域名）或 "third-party"。
   - 官方域名: mindspore.cn, gitcode.com/mindspore, github.com/mindspore-ai, gitee.com/mindspore
3. **计算引用比例**: official_source_ratio = 官方源数量 / 总来源数量（如无来源，ratio = 0）。
4. **判定现象类型**:
   - **B（有内容未引用）**: 官方有内容，但回答未引用或未提及任何官方源。ratio = 0 或极低。
   - **C（引用错误信息）**: 回答引用了官方源但信息不准确（版本错误、过时信息、与官方内容矛盾）。这是最严重的问题。
   - **D（引用比例大）**: 回答主要引用官方源，信息准确。ratio > 0.5。
   - **E（引用比例小）**: 回答引用了官方源但比例低。0 < ratio ≤ 0.5。
5. **评分**: 给出 1-10 分的 accuracy_score:
   - 9-10: 主要引用官方源，信息完全准确
   - 7-8: 引用官方源，信息基本准确但有小瑕疵
   - 5-6: 部分引用官方源，或信息有遗漏
   - 3-4: 很少引用官方源，主要依赖第三方信息
   - 1-2: 未引用官方源，或引用了错误信息
6. **识别内容问题**: 从以下标签中选出所有适用的内容问题（用于后续匹配优化建议）:
   - `no_direct_answer` — 回答未在开头直接给出答案
   - `buried_answer` — 核心答案被埋在大量背景信息中
   - `missing_faq` — 缺少常见追问的覆盖
   - `ambiguous_terminology` — 术语使用模糊，可能与其他产品/概念混淆
   - `missing_disambiguation` — 缺少消歧义声明
   - `negation_missed` — 限制/不支持信息被遗漏
   - `negation_reversed` — 限制信息被反转（不支持说成支持）
   - `outdated_info` — 引用了过时的版本信息
   - `version_confusion` — 混淆了不同版本的特性
   - `fabricated_claims` — 包含虚构的功能、API 或特性声明
   - `vague_numbers` — 使用模糊数字（"很快""很多"）而非精确数据
   - `no_schema_markup` — 官方页面缺少结构化标记（通过回答质量推断）
   - `poor_structure` — 回答反映出官方内容组织结构不佳
   - `no_tables` — 本应用表格呈现的对比/参数信息以文本呈现
   - `missing_summary` — 缺少要点摘要
   - `no_query_variants` — 仅覆盖单一提问方式
   - `missing_scope` — 未说明适用范围/版本/条件
   - `entity_confusion` — 将本产品与其他产品混淆
   - `shallow_content` — 内容浅显，缺乏深度
   - `no_evidence` — 声明缺少证据支撑
   - `no_alternatives` — 提到限制但未给出替代方案
   - `missing_use_cases` — 缺少使用场景/决策框架
   - `no_process_doc` — 缺少完整的操作过程记录
   - `inconsistent_data` — 数据自相矛盾
   - `missing_edge_cases` — 未讨论边界条件或例外情况
   - `no_reasoning` — 推荐方案但未解释选择原因

## 输出格式

严格按以下 JSON 格式输出，不要添加任何其他内容:

{
  "citation_type": "B|C|D|E",
  "official_source_ratio": 0.0-1.0,
  "accuracy_score": 1-10,
  "details": "一句话说明判定理由",
  "issues_found": ["issue标签1", "issue标签2"],
  "sources_identified": [
    {"url_or_name": "来源名称或URL", "type": "official|third-party"}
  ]
}
```

## Template Variables

| Variable | Source | Description |
|----------|--------|-------------|
| `{question}` | `responses.json` → `question` | Original question text |
| `{platform}` | `responses.json` → `platform` | AI platform name |
| `{response_text}` | `responses.json` → `response_text` | Full AI response |
| `{content_coverage}` | `content-labels.json` → `content_coverage` | full / partial |
| `{official_urls}` | `content-labels.json` → `official_urls` | Comma-separated official URLs |
| `{calibration_context}` | `scoring-calibration.md` (if exists) | Human correction context from prior rounds |

## Calibration Context Format

When `scoring-calibration.md` exists, insert this block:

```
## 校准上下文（来自人工抽检）

以下是之前评分中人工校准的修正记录，请参考这些修正避免类似偏差：

{calibration_entries}
```

If no calibration file exists, omit this block entirely.
