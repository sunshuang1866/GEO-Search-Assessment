# Suggestion Rules

基于现象分类和回答内容分析，从 `geo-suggestions-catalog.md` 中匹配适用的优化建议。

## Category Assignment

| Phenomenon | Category | Label |
|------------|----------|-------|
| A | `content` | 内容缺口 |
| B | `seo` | 可检索性不足 |
| C | `correction` | 引用错误 |
| D | — | 无需行动（或 `monitoring` 如有小瑕疵） |
| E | `optimization` | 引用比例不足 |

## 建议生成流程

### 第一步：确定现象类型

根据 Layer 2 评分结果中的 `citation_type` 确定现象（A/B/C/D/E）。

### 第二步：获取候选建议列表

查阅 `references/geo-suggestions-catalog.md` 顶部的「现象→建议映射表」，获取该现象对应的所有候选建议 ID。

### 第三步：根据 issues_found 精准匹配

根据评分输出中的 `issues_found` 字段（具体内容问题标签），从候选列表中筛选最相关的建议。匹配规则：

| issue 标签 | 优先匹配的建议 ID |
|-----------|-----------------|
| `no_direct_answer` | CTX-02 |
| `buried_answer` | CTX-02, ORG-02 |
| `missing_faq` | CTX-09, ORG-05 |
| `ambiguous_terminology` | DIS-01, DIS-02, DIS-03, CTX-04 |
| `missing_disambiguation` | DIS-03, DIS-04 |
| `negation_missed` | NEG-01, NEG-02, NEG-03, NEG-04, NEG-05 |
| `negation_reversed` | NEG-01, NEG-02, NEG-04 |
| `outdated_info` | REF-06, VER-01, VER-02, VER-03 |
| `version_confusion` | VER-01, VER-02, VER-03, CTX-05 |
| `fabricated_claims` | REF-04, REF-10, NEG-03, DIS-03 |
| `vague_numbers` | REF-01, EXP-08 |
| `no_schema_markup` | ORG-05 |
| `poor_structure` | ORG-01, ORG-06, ORG-04 |
| `no_tables` | ORG-03 |
| `missing_summary` | ORG-02 |
| `no_query_variants` | CTX-03, KWD-01, KWD-02 |
| `missing_scope` | CTX-05, EXP-10 |
| `entity_confusion` | REF-07, DIS-01, DIS-02 |
| `shallow_content` | EXC-08, EXC-06, REF-02, REF-03 |
| `no_evidence` | REF-04, REF-05, EXC-01, EXC-03 |
| `no_alternatives` | NEG-04, CTX-08 |
| `crawl_blocked` | SITE-01, SITE-03 |
| `spa_blank_page` | SITE-03 |
| `missing_use_cases` | CTX-08, EXC-07 |
| `no_process_doc` | EXP-03, REF-05 |
| `inconsistent_data` | REF-10, EPT-03 |
| `missing_edge_cases` | EPT-06, CTX-05 |
| `no_reasoning` | EPT-08, REF-04 |

### 第四步：生成建议对象

对于每个匹配的建议，生成结构化建议对象：

```json
{
  "suggestion_id": "s_001",
  "question_id": "q_001",
  "question": "...",
  "platform": "ChatGPT",
  "citation_type": "B",
  "official_source_ratio": 0.2,
  "accuracy_score": 4,
  "severity": "P1",
  "category": "seo",
  "catalog_refs": ["CTX-02", "ORG-05", "DIS-01"],
  "suggestion_text": "结合 catalog 中建议的具体操作，针对该问题和页面的实际情况，生成可执行的改进建议",
  "details": "..."
}
```

**关键规则**：`suggestion_text` 不是照搬 catalog 原文，而是将 catalog 中的通用操作指南结合该问题的具体上下文（问题内容、平台回答、官方页面现状）转化为具体的、可执行的改进措施。

### 第五步：建议数量控制

- 每个 (question, platform) 对最多生成 5 条建议（选最相关的）。
- 多平台出现相同问题时，合并为一条建议，`platform` 字段列出所有受影响平台。
- Phenomenon D（无需行动）不生成建议，除非 accuracy_score < 8。

## Severity Override Rules

- If `citation_type` is C, severity is always P0 regardless of ratio.
- If `citation_type` is B and `content_coverage` is "full", elevate to P1 (official has complete answer but AI ignores it).
- If `citation_type` is E and `official_source_ratio` < 0.1, elevate to P1.
- Phenomenon D with `accuracy_score` >= 8 → no_action.
- Phenomenon D with `accuracy_score` < 8 → P2.
