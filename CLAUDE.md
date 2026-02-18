# cc-hackernews

Fetches Hacker News front page content and saves it as structured Markdown files for reading, searching, and further inquiry.

## What it does

Uses `contextkit` to pull HN pages as Markdown, extracts article titles/URLs/domains via regex, and writes the results to organised output files that include page type metadata in both the filename and document header.

## Folder structure

```
cc-hackernews/
├── CLAUDE.md                  # This file
├── INTERESTS.md               # User interests for post recommendations
├── hn.py                      # Core scraping logic
├── articles.py                # Article URL lookup + save helper
└── output/
    ├── main/                  # Live front page snapshots
    │   ├── hackernews_main_YYYY-MM-DD.md
    │   └── hackernews_main_YYYY-MM-DD_compact.md
    ├── front/                 # Daily archive (front page by date)
    │   ├── hackernews_front_YYYY-MM-DD.md
    │   └── hackernews_front_YYYY-MM-DD_compact.md
    └── articles/              # Individual pulled articles
        └── YYYY-MM-DD_NN_article-title-slug.md
```

## Key file: `hn.py`

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
from hn import save_hn_to_markdown

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
- Standard library: `re`, `os`, `datetime`, `glob`, `argparse`

## Key file: `articles.py`

| Function | Purpose |
|---|---|
| `get_latest_hn_file(page_type)` | Returns the most recently modified full-format output file for a page type |
| `get_article(n, page_type, filepath)` | Returns `(title, url, domain)` for article number n; handles both full and compact formats |
| `article_filepath(n, title, date_str)` | Returns the output path for a saved article (`output/articles/YYYY-MM-DD_NN_slug.md`) |
| `build_article_header(title, url, domain, n)` | Returns the markdown metadata header to prepend to saved article content |
| `open_in_browser(url)` | Opens a URL in the default browser via `open` (macOS) |

CLI usage:

```bash
python3 articles.py 3              # look up article 3 from output/main/
python3 articles.py 3 --page front # look up from output/front/
python3 articles.py 3 --file path/to/file.md
```

## Pulling articles

When the user says "pull N" (where N is an article number from the list):

- `pull N` — ask whether they want a summary, full read, just the URL, or to open in browser
- `pull N summary` — resolve the URL via `articles.py`, then use a **Task subagent** to fetch and summarize
- `pull N read` — resolve the URL via `articles.py`, then use a **Task subagent** to fetch and display the full content
- `pull N url` — run `python3 articles.py N` and return just the URL line
- `pull N open` — resolve the URL and run `open <url>` (macOS)

### Why subagents for summary/read

Raw article content is 5,000–30,000+ tokens. Running a Task subagent keeps that content out of the main context — only the summary or processed output (~200–500 tokens) is returned here. Always use subagents for `summary` and `read` operations.

### Subagent prompt template for summaries

Before launching the subagent, resolve the article metadata with Bash:

```bash
python3 articles.py <N>
# outputs: Title, URL, Domain
```

Then get the save path:

```bash
python3 -c "
from articles import article_filepath, build_article_header
title = '<TITLE>'
url   = '<URL>'
domain = '<DOMAIN>'
n = <N>
path = article_filepath(n, title)
header = build_article_header(title, url, domain, n)
print('PATH:', path)
print('---HEADER---')
print(header)
"
```

Then launch a Task subagent with this prompt:

```
Fetch the article at <URL> using WebFetch.

Save the full content as a markdown file at: <FILEPATH>
Prepend exactly this header before the article content:

<HEADER>

After saving, write a concise summary (4–6 sentences) covering:
- What the article is about
- Key argument or finding
- Why it's relevant or interesting

Return only the summary and the saved filepath — no other preamble.

If the site blocks WebFetch, return: "Blocked: <URL>"
```

If the site blocks fetching, say so and provide the URL so the user can open it directly.

## Recommendations

When the user asks for recommendations or "what's interesting", consult `INTERESTS.md` and cross-reference it against the current article list to surface the most relevant posts. Briefly explain why each pick matches their interests.

## Adding new page types

1. Add a new entry to `PAGE_TYPES` in `hackernews_scrape.py`
2. Add a branch in `build_hn_url` that returns the correct URL and date string
3. Output will automatically be saved under `output/<page_type>/`
