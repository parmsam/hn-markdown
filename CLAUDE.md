# cc-hackernews

Fetches Hacker News front page content and saves it as structured Markdown files for reading, searching, and further inquiry.

## What it does

Uses `contextkit` to pull HN pages as Markdown, extracts article titles/URLs/domains via regex, and writes the results to organised output files that include page type metadata in both the filename and document header.

## Folder structure

```
cc-hackernews/
├── CLAUDE.md                  # This file
├── INTERESTS.md               # User interests for post recommendations
├── hackernews_scrape.py       # Core scraping logic
└── output/
    ├── main/                  # Live front page snapshots
    │   ├── hackernews_main_YYYY-MM-DD.md
    │   └── hackernews_main_YYYY-MM-DD_compact.md
    └── front/                 # Daily archive (front page by date)
        ├── hackernews_front_YYYY-MM-DD.md
        └── hackernews_front_YYYY-MM-DD_compact.md
```

## Key file: `hackernews_scrape.py`

| Function | Purpose |
|---|---|
| `build_hn_url(page_type, date)` | Returns the HN URL and date string for the requested page type |
| `fetch_hn_content(url)` | Fetches the page as Markdown via `contextkit.read.read_link` |
| `extract_articles(content)` | Regex-extracts `(title, url, domain)` tuples from the Markdown |
| `_markdown_header(articles, date_str, page_type)` | Shared metadata table used by both format generators |
| `generate_markdown(articles, date_str, page_type)` | Full format: title + URL + domain on separate lines |
| `generate_markdown_compact(articles, date_str, page_type)` | Compact format: one line per article |
| `resolve_output_path(page_type, date_str, fmt, filename)` | Resolves and creates `output/<page_type>/` as needed |
| `save_hn_to_markdown(page_type, date, fmt, filename)` | Orchestrates the full pipeline; returns `(filepath, article_count)` |

## Page types

| `page_type` | URL fetched | Description |
|---|---|---|
| `main` | `https://news.ycombinator.com/` | Live front page (current moment) |
| `front` | `https://news.ycombinator.com/front?day=YYYY-MM-DD` | Historical front page for a specific date |

## Usage

```python
from hackernews_scrape import save_hn_to_markdown

# Snapshot of today's live front page (full format)
filepath, count = save_hn_to_markdown(page_type='main')

# Compact format — one line per article
filepath, count = save_hn_to_markdown(page_type='main', fmt='compact')

# Historical front page for a specific date
filepath, count = save_hn_to_markdown(page_type='front', date='2025-01-15')

print(f"Saved {count} articles to {filepath}")
```

## Output formats

Both formats share the same metadata table header. The `fmt` parameter controls the article list style.

### `fmt='full'` (default) — `hackernews_<page_type>_<date>.md`

```markdown
1. **Article Title**
   - URL: https://example.com/article
   - Domain: example.com
```

### `fmt='compact'` — `hackernews_<page_type>_<date>_compact.md`

```markdown
1. **Article Title** — [example.com](https://example.com/article)
```

Both start with the shared metadata header:

```markdown
# Hacker News — Main (Live Front Page)

| Field   | Value                    |
|---------|--------------------------|
| Date    | 2026-02-17               |
| Page    | Main (Live Front Page)   |
| Fetched | 2026-02-17 18:45:00      |
| Count   | 30 articles              |

---
```

## Dependencies

- `contextkit` — wraps web pages as Markdown (`contextkit.read.read_link`)
- Standard library: `re`, `os`, `datetime`

## Pulling articles

When the user says "pull N" (where N is an article number from the list):

- `pull N` — ask whether they want a summary, full read, just the URL, or to open in browser
- `pull N summary` — fetch and summarize the article
- `pull N read` — fetch and display the full article content in the terminal
- `pull N url` — return just the URL
- `pull N open` — open the article in the default browser via `open <url>` (macOS)

Use `WebFetch` to retrieve the content. If the site blocks fetching, say so and provide the URL so the user can open it directly.

## Recommendations

When the user asks for recommendations or "what's interesting", consult `INTERESTS.md` and cross-reference it against the current article list to surface the most relevant posts. Briefly explain why each pick matches their interests.

## Adding new page types

1. Add a new entry to `PAGE_TYPES` in `hackernews_scrape.py`
2. Add a branch in `build_hn_url` that returns the correct URL and date string
3. Output will automatically be saved under `output/<page_type>/`
