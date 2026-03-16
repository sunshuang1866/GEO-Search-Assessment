# Forum API Specification (Discourse)

## Status: Confirmed ✅

This spec covers **Discourse**-based community forums. No authentication required for public data.

## Base URL

Passed via `--api-url` or defaults to the community's known forum URL.

```
Example: https://discuss.mindspore.cn
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

## Category Taxonomy

Discourse forum categories vary by community but typically fall into these functional types:

| Type | GEO Value | Examples |
|---|---|---|
| **Q&A / Help** | High — real user questions | help, questions, support, 问题求助 |
| **Sub-project** | High — domain-specific questions | mindspore-lite, plugins, extensions |
| **Tutorials / Blog** | Medium — how-to content | tech, tutorials, 经验分享 |
| **Feedback** | Medium — feature requests, pain points | feedback, suggestions, 建议反馈 |
| **Announcements** | Low — not questions | announcements, events, 活动公告 |
| **Meta / Uncategorized** | Skip | meta, staff, uncategorized |

### Dynamic Discovery

Fetch the actual category list for any Discourse forum:
```
GET {base_url}/categories.json
```
The response contains `category_list.categories[]` with `id`, `slug`, `name`, `topic_count`. Use `topic_count` to identify active categories.

### Default Fetch Mode

Global top topics across all categories via `/top.json?period=all`. Use `--category <slug>` to restrict to a specific category when needed.

## Topic Object Fields

```json
{
  "id": 12345,
  "title": "GPU 版本安装报错求助",
  "slug": "gpu-install-error",
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
