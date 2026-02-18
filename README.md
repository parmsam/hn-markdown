# cc-hackernews

Fetches the Hacker News [front page](https://news.ycombinator.com/) and saves it as structured Markdown — useful for reading, searching, and piping into LLMs for further inquiry.

## Quick start

```python
from hackernews_scrape import save_hn_to_markdown

# Today's live front page
filepath, count = save_hn_to_markdown(page_type='main')

# Compact format (one line per article)
filepath, count = save_hn_to_markdown(page_type='main', fmt='compact')

# Past front page by date — HN archives go back to 2006
filepath, count = save_hn_to_markdown(page_type='front', date='2025-01-15')
filepath, count = save_hn_to_markdown(page_type='front', date='2007-06-01')  # early HN!
```

## Past front pages

Use `page_type='front'` with a `date` string (`YYYY-MM-DD`) to fetch any historical front page. HN's archives go back to 2006, so you can pull what was trending on any given day:

```python
# What was on HN the day the iPhone launched?
save_hn_to_markdown(page_type='front', date='2007-01-09')

# A year ago today
save_hn_to_markdown(page_type='front', date='2025-02-17')
```

## Output formats

### Full (default)

```
1. **Article Title**
   - URL: https://example.com/article
   - Domain: example.com
```

### Compact

```
1. **Article Title** — [example.com](https://example.com/article)
```

Both formats include a metadata table (date, page type, fetch time, article count) at the top of the file.

## Output location

Files are saved to `output/<page_type>/`:

```
output/
├── main/
│   ├── hackernews_main_2026-02-17.md
│   └── hackernews_main_2026-02-17_compact.md
└── front/
    └── hackernews_front_2025-01-15.md
```

## Dependencies

- [`contextkit`](https://pypi.org/project/contextkit/) — fetches web pages as Markdown
- Python standard library: `re`, `os`, `datetime`
