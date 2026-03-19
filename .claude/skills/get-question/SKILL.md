---
name: get-question
description: Generates a structured question set for GEO search assessment. Supports 4 source paths (forum, issue, maillist, industry) — select individually or all. Reads manual questions from Markdown, fetches real data from forum/issues/SIG community info, generates industry questions via LLM, merges and deduplicates, then outputs questions.json and questions.md. Use when starting a new GEO assessment or refreshing the question set. Do not use for platform sampling, scoring, or improvement suggestions.
---

# Get Question

## I/O

| Param | Required | Default | Notes |
|---|---|---|---|
| `community` | yes | — | e.g. "MindSpore" |
| `seed_keywords` | no | LLM-derived | comma-separated |
| `paths` | no | `all` | `forum` / `issue` / `maillist` / `industry` / `all` |
| `sig_url` | no | `https://www.mindspore.cn/sig` | Entry point for SIG data (maillist path) |
| `forum_url` | no | — | Discourse forum base URL (e.g. `https://discuss.mindspore.cn`) |
| `repo_owner` | no | — | GitCode repo owner/org for issue path |
| `repo_name` | no | — | GitCode repo name for issue path |
| `limit` | no | `50` | Chinese format ok: "前10" → `10` |

**Outputs**: `questions.json`, `questions.md` in project root

**Constant**: `SD=.claude/skills/get-question`

---

## Step 1 — Init

1. Load `.env` from project root.
2. Resolve inputs. If `seed_keywords` missing → LLM: `"List 3-5 comma-separated technical keywords for '{community}'. Keywords only."`
3. Log: `Community={community} keywords={seed_keywords} paths={paths} limit={limit}`

---

## Step 2 — Manual Questions

If `manual-questions.md` exists → run `python3 $SD/scripts/parse-manual-questions.py manual-questions.md`, capture stdout → `manual_questions`. Otherwise `manual_questions=[]`.

---

## Step 3 — Path 1: Forum [PRIMARY]

Skip if `paths` excludes `forum`.

1. Run `python3 $SD/scripts/fetch-forum-posts.py --community "{community}" --limit {limit} [--api-url "{forum_url}"]`.
2. **exit=0** → Read `$SD/assets/prompt-templates.md` section `REWRITE_TO_QUESTIONS`, apply forum variant, send LLM call with fetched data. Capture → `path1_questions`.
3. **exit≠0** → Read `$SD/assets/prompt-templates.md` section `FORUM_FALLBACK`, send LLM call. Capture → `path1_questions`.

---

## Step 4 — Path 2: Issues [PRIMARY]

Skip if `paths` excludes `issue`.

1. Pre-validate: `curl -s -o /dev/null -w "%{http_code}" -H "private-token: {GITCODE_TOKEN}" "https://api.gitcode.com/api/v5/user"`.
   - **≠ 200** → log `SKIP: GITCODE_TOKEN invalid (HTTP {status})`, set `path2_questions=[]`, go to Step 5.
2. Run `GITCODE_TOKEN={GITCODE_TOKEN} python3 $SD/scripts/fetch-repo-issues.py --owner {repo_owner} --repo {repo_name} --limit {limit}`.
3. **success** → Read `$SD/assets/prompt-templates.md` section `REWRITE_TO_QUESTIONS`, apply issue variant, send LLM call. Capture → `path2_questions`.
4. **failure** → log warning, set `path2_questions=[]`. No LLM fallback.

---

## Step 5 — Path 3: Maillist (SIG)

Skip if `paths` excludes `maillist`.

1. Run `python3 $SD/scripts/fetch-sig-info.py --community "{community}" --limit {limit} --fetch-content`.
2. **exit=0** → Read `$SD/assets/prompt-templates.md` section `MAILLIST_REWRITE`, send LLM call with fetched data. Capture → `path3_questions`.
3. **exit≠0** → Read `$SD/assets/prompt-templates.md` section `MAILLIST_FALLBACK`, send LLM call. Capture → `path3_questions`.

Two-step data flow:
1. Fetch SIG list from `www.mindspore.cn/api-magicapi/sig/all/mindspore` → extract `mailing_list` addresses per SIG
2. Fetch email archives from HyperKitty API at `mailweb.mindspore.cn` → thread subjects + email content (meeting notices, discussions, announcements)

---

## Step 6 — Path 4: Industry

Skip if `paths` excludes `industry`.

1. Read `$SD/assets/prompt-templates.md` section `INDUSTRY_DISCOVERY`, send LLM call.
2. Extract `questions` array → `path4_questions`.

---

## Step 7 — Merge & Deduplicate

1. Combine: `all_questions = manual_questions + path1_questions + path2_questions + path3_questions + path4_questions`.
2. Read `$SD/assets/prompt-templates.md` section `MERGE_DEDUP`, send LLM call with combined data.
3. Validate: `echo '{merged_json}' | python3 $SD/scripts/validate-questions.py`.
   - **errors** → show errors, LLM fixes JSON, re-validate once.
   - **still invalid** → abort.
4. If total < 30 (all paths) or < 10 (subset) → LLM fills gaps in underrepresented intents.

---

## Step 8 — Output

1. Write validated JSON → `questions.json`.
2. Render `questions.md` using `$SD/assets/questions-template.md` — group by intent, include summary table, mark source per question.
3. Print: `Generated {total} questions | Sources: manual={n} forum={n} issue={n} maillist={n} industry={n} | Paths: {paths_run}`.

---

## Step 9 — Review Checkpoint

PAUSE: `⏸ Review questions.md — delete irrelevant, add missing. Resume when done.`
