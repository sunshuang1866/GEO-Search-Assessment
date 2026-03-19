# SIG Maillist API Specification

## Status: Confirmed ✅

This spec covers how to fetch MindSpore SIG mailing list email archives for the `maillist` path in get-question.

## Two-Step Data Flow

```
Step 1: SIG list API → extract mailing_list addresses per SIG
Step 2: HyperKitty API → fetch email threads + content from those addresses
```

## Endpoints

### Step 1: SIG List (MagicAPI)

```
GET https://www.mindspore.cn/api-magicapi/sig/all/mindspore
```

Response fields per SIG: `name`, `description`, `mailing_list`, `maintainers[]` (with email), `repositories[]`.

Each SIG has a `mailing_list` field (e.g., `dev@mindspore.cn`, `tc@mindspore.cn`).

### Step 2a: Mailing List Discovery (HyperKitty)

```
GET https://mailweb.mindspore.cn/hyperkitty/api/lists/
```

Returns all available mailing lists. 10 lists as of 2026-03:

| List | Threads | Content |
|---|---|---|
| `dev@mindspore.cn` | 71 | SIG meeting notices, technical discussions |
| `mindspore-tsc@mindspore.cn` | 53 | Technical committee discussions |
| `mindspore-discuss@mindspore.cn` | 49 | Developer discussions |
| `infra@mindspore.cn` | 8 | Infrastructure |
| `news_post_en@mindspore.cn` | 6 | English news |
| `community@mindspore.cn` | 0 | Empty |
| `mindspore-research@mindspore.cn` | 0 | Empty |
| `news@mindspore.cn` | 0 | Empty |

### Step 2b: Thread Listing (HyperKitty)

```
GET https://mailweb.mindspore.cn/hyperkitty/api/list/{addr}/threads/?limit=10&offset=0
```

Response:
```json
{
  "count": 71,
  "next": "...?limit=10&offset=10",
  "results": [
    {
      "thread_id": "2H7MEPX5NXRGKQGSKDVTGZGHYWGLXN5W",
      "subject": "[Dev] MindSpore Transformers SIG周例会",
      "date_active": "2026-02-10T10:51:08+08:00",
      "replies_count": 0,
      "starting_email": "https://mailweb.mindspore.cn/archives/api/list/dev@mindspore.cn/email/2H7MEPX5NXRGKQGSKDVTGZGHYWGLXN5W/"
    }
  ]
}
```

### Step 2c: Email Content (HyperKitty)

```
GET https://mailweb.mindspore.cn/archives/api/list/{addr}/email/{message_id_hash}/
```

Response:
```json
{
  "subject": "[Dev] MindSpore Transformers SIG周例会",
  "sender_name": "MindSpore conference",
  "date": "2026-02-10T10:51:08+08:00",
  "content": "您好！\nMindSpore Transformers 邀请您参加 2026-02-12 16:00 召开的Tencent会议...\n会议主题：...\n会议链接：...\n会议纪要：...",
  "attachments": [...]
}
```

### Step 2d: Monthly Archive (HTML, for reference)

```
https://mailweb.mindspore.cn/hyperkitty/list/{addr}/{year}/{month}/
```

### Mailing List Subscription (Mailman 3 Postorius)

```
https://mailweb.mindspore.cn/postorius/lists/
```

## Email Content Types

Emails in MindSpore mailing lists fall into these categories:

| Type | GEO Value | Example |
|---|---|---|
| **SIG meeting notice** | High — reveals active SIGs, meeting topics, schedules | "MindSpore Transformers SIG周例会" |
| **Technical discussion** | High — real developer questions/answers | TSC discussions about architecture |
| **Announcement** | Medium — version releases, events | News posts |
| **Infrastructure** | Low — CI/CD, infra changes | Infra list |

## Rate Limits

- HyperKitty API: No documented rate limit, but be conservative.
- Thread listing: paginated at 10/page. Fetching 50 threads = 5 requests per list.
- Email content: 1 request per email. Use `--fetch-content` flag only when needed.
- Default mode (no `--fetch-content`): ~1 SIG API call + ~5 list discovery + ~25 thread pages = ~31 requests.
- With `--fetch-content` and 50 threads across all lists: ~31 + ~187 = ~218 requests. Use `--limit` to control.

## Fallback

If both MagicAPI and HyperKitty are unreachable, the skill falls back to LLM-generated mailing list questions.
