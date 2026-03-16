# GitCode API Specification

## Status: Confirmed ✅ (requires auth)

GitCode (AtomGit) hosts open-source repositories. The API requires a `private-token` header for authentication.

## Base URL

```
https://api.gitcode.com/api/v5
```

## Authentication

All requests require a `private-token` header:

```
private-token: <GITCODE_TOKEN>
```

Token can be generated at GitCode account settings. Store in `.env` as `GITCODE_TOKEN`.

## Endpoints

### List Repository Issues

```
GET /repos/{owner}/{repo}/issues?state={state}&sort={sort}&direction={direction}&page={page}&per_page={per_page}
```

Parameters:
- `owner`: Repository owner/org
- `repo`: Repository name
- `state`: `open`, `closed`, `all` (default: `all`)
- `sort`: `created`, `updated` (default: `created`)
- `direction`: `asc`, `desc` (default: `desc`)
- `page`: Page number (default: `1`)
- `per_page`: Items per page, max 100 (default: `20`)

### Issue Object Fields

```json
{
  "id": 12345,
  "number": "I123AB",
  "title": "GPU 版本安装报错",
  "state": "open",
  "labels": [
    {"name": "bug", "color": "#d73a4a"}
  ],
  "comments": 15,
  "created_at": "2026-02-15T10:00:00+08:00",
  "updated_at": "2026-02-20T08:30:00+08:00",
  "html_url": "https://gitcode.com/{owner}/{repo}/issues/I123AB"
}
```

## Rate Limits

GitCode API rate limits are not publicly documented. The script fetches 1-3 pages typically (50-150 issues), which should be within limits.

## Token Pre-Validation

Before fetching issues, validate the token with a lightweight call:

```
GET /user
Headers: private-token: <GITCODE_TOKEN>
```

- HTTP `200`: token is valid, proceed
- HTTP `404` with body `{"error_message": "404, token not found"}`: token is invalid or expired — regenerate at gitcode.com/profile/personal_access_tokens
- HTTP `401`: token missing or malformed

## Error Responses

- `400`: Missing `private-token` header
- `401`: Malformed token
- `403`: Token lacks required permissions (needs `read_repository` scope)
- `404` with "token not found": Token is invalid or expired (⚠️ GitCode returns 404, not 403, for bad tokens)
- `404` with repo path in message: Repository not found

## Fallback

If `GITCODE_TOKEN` is not set or API fails, Path 2 (issue) is skipped entirely. No LLM fallback — issue data must come from real sources.
