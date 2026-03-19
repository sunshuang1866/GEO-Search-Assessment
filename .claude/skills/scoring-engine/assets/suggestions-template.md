# GEO 评分报告

> 生成时间: {scored_at}
> 标准答案: {has_standard_answers}
> 官方域名: {official_domains}

## 一、概览

| 指标 | 数值 |
|------|------|
| 评估问题数 | {total_questions} |
| 评估平台数 | {total_platforms} |
| 评估对数 | {scored_pairs}/{total_pairs} |
| 平均引用比例 | {avg_ratio:.1%} |
| 内容源问题数 | {content_origin_count}（≥3 平台出现相同问题） |

## 二、核心发现

1. {finding_1}
2. {finding_2}
3. {finding_3}

## 三、现象分布

| 现象 | 数量 | 占比 | 说明 |
|------|------|------|------|
| A — 官网无内容 | {a_count} | {a_pct:.0%} | 内容缺口，需补内容 |
| B — 有内容未引用 | {b_count} | {b_pct:.0%} | SEO/结构化优化 |
| C — 引用错误 | {c_count} | {c_pct:.0%} | 紧急纠错 |
| D — 引用比例大 | {d_count} | {d_pct:.0%} | 健康，持续监控 |
| E — 引用比例小 | {e_count} | {e_pct:.0%} | 内容深度优化 |

## 四、严重级别分布

| 级别 | 数量 | 说明 |
|------|------|------|
| P0 | {p0_count} | 立即行动 |
| P1 | {p1_count} | 计划改进 |
| P2 | {p2_count} | 低优先级 |
| 无需行动 | {ok_count} | 持续监控 |

## 五、平台对比

| 平台 | 平均得分 | 平均引用比例 | 主要现象 |
|------|---------|-------------|---------|
{platform_rows}

## 六、跨平台模式分析

### 幻觉模式
{hallucination_patterns}

### 消歧义问题
{disambiguation_patterns}

### 否定传递失败
{negation_failures}

### 引用盲区
{citation_gaps}

### 内容源问题（≥3 平台）
{content_origin_issues}

## 七、改进建议（按优先级）

> 建议来源：[GEO 优化建议目录](references/geo-suggestions-catalog.md)（72 条标准化建议）。
> 每条建议标注了关联的目录编号（catalog_refs），可查阅目录获取通用操作指南。

### P0 — 立即行动（1-2 周内完成）

{p0_suggestions}

### P1 — 计划改进（2-4 周内完成）

{p1_suggestions}

### P2 — 低优先级（持续优化）

{p2_suggestions}

## 八、逐题详情

{question_details}

## 九、执行路线图

### 阶段一：紧急修复（1-2 周）— P0 项目
- [ ] {p0_item_1}
- [ ] {p0_item_2}

### 阶段二：短期改进（2-4 周）— P1 项目
- [ ] {p1_item_1}
- [ ] {p1_item_2}

### 阶段三：持续优化（长期）— P2 项目
- [ ] {p2_item_1}

## 十、KPI 跟踪

| 指标 | 定义 | 当前 | 目标 |
|------|------|------|------|
| 官方引用率 | 回答中引用官方源的比例 | {current_citation_rate}% | ≥60% |
| 事实准确率 | 回答与标准答案匹配的比例 | {current_accuracy_rate}% | ≥80% |
| 否定传递率 | 限制性信息被正确传递的比例 | {current_negation_rate}% | ≥70% |
| 上下文正确率 | 术语在正确产品语境下使用的比例 | {current_context_rate}% | ≥90% |
| 版本新鲜度 | 引用最新稳定版的比例 | {current_freshness_rate}% | ≥70% |

---

> 此报告由 GEO Search Assessment scoring-engine 自动生成。
> 建议人工抽检 20% 的评分结果，校准记录保存到 `scoring-calibration.md`。
