# Forum API Specification

## Status: Confirmed ✅

MindSpore community forum at `https://discuss.mindspore.cn` runs **Discourse** and exposes standard Discourse REST API endpoints. No authentication required for public data.

## Base URL

```
https://discuss.mindspore.cn
```

## Endpoints

### Global Top Topics

```
GET /top.json?page={N}&per_page=50
```

Returns topics sorted by activity/views across all categories. Pagination: `page=0,1,2...`

### Category Topics (Latest)

```
GET /c/{slug}/{category_id}.json?page={N}
```

Returns latest topics within a specific category (sorted by activity).

### Category Topics (Top by Views) ✅ Preferred for question extraction

```
GET /c/{slug}/{category_id}/l/top.json?period=all&page={N}
```

Returns topics sorted by views (all-time). Use `period=all` for global top; `period=yearly` / `period=monthly` for recency. This is the correct endpoint for question discovery — it surfaces the most-viewed threads rather than the newest ones.

### Categories List

```
GET /categories.json
```

Returns all forum categories with metadata.

### Search

```
GET /search.json?q={query}
```

Full-text search across topics and posts.

## Key Categories

| ID | Slug | Name | Topics |
|----|------|------|--------|
| 4 | help | 问题求助 Help | 103 |
| 38 | mindspore-lite | MindSpore Lite推理部署 | 43 |
| 14 | activities | 活动公告 Activities | 17 |
| 15 | tech | 经验分享 Tech Blogs | 6 |
| 2 | feedback | 建议与反馈 Feedback | 2 |
| 39 | mindspore-transformers | 大模型套件 MindSpore Transformers | 1 |
| 36 | mindspore-llm-inference-serving | 大模型推理部署 LLM Inference Serving | 1 |

**Primary sources for question extraction**: `help` (id:4) and `mindspore-lite` (id:38).

## Topic Object Fields

```json
{
  "id": 12345,
  "title": "MindSpore GPU 版本安装报错求助",
  "slug": "mindspore-gpu",
  "views": 1520,
  "reply_count": 23,
  "like_count": 5,
  "posts_count": 24,
  "category_id": 4,
  "tags": ["安装", "GPU"],
  "has_accepted_answer": true,
  "pinned": false,
  "closed": false,
  "created_at": "2026-02-15T10:00:00Z",
  "last_posted_at": "2026-02-20T08:30:00Z"
}
```

## Rate Limits

Discourse default: 60 requests/minute for anonymous users. The script fetches 2-4 pages typically, well within limits.

## Fallback

If the API is unreachable (network error, 5xx), the skill falls back to LLM-generated usage questions.
