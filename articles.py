"""
articles.py

Utility for looking up individual articles from saved HN output files.
Used by Claude Code pull commands to resolve article URLs without loading
the full article list into the main context.

Usage (CLI):
    python articles.py 3              # print title, url, domain for article 3
    python articles.py 3 --page front # look in output/front/ instead

Usage (module):
    from articles import get_article
    title, url, domain = get_article(3)
"""

import argparse
import glob
import os
import re
import sys
from datetime import datetime

from hn import OUTPUT_DIR

ARTICLES_DIR = os.path.join(OUTPUT_DIR, 'articles')


def get_latest_hn_file(page_type='main'):
    """Return the most recently modified full-format HN output file for a page type."""
    pattern = os.path.join(OUTPUT_DIR, page_type, f'hackernews_{page_type}_*.md')
    files = [f for f in glob.glob(pattern) if '_compact' not in f]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def get_article(n, page_type='main', filepath=None):
    """Return (title, url, domain) for article number n from the saved HN file.

    Args:
        n:          1-based article number
        page_type:  'main' or 'front'
        filepath:   explicit path to an HN output file (overrides page_type lookup)

    Returns:
        (title, url, domain) tuple, or raises ValueError if not found.
    """
    if filepath is None:
        filepath = get_latest_hn_file(page_type)
    if filepath is None:
        raise FileNotFoundError(
            f"No saved HN file found for page_type='{page_type}'. "
            "Run save_hn_to_markdown() first."
        )

    with open(filepath) as f:
        content = f.read()

    # Match the full-format block: "N. **Title**\n   - URL: ...\n   - Domain: ..."
    pattern = (
        rf'(?m)^{n}\.\s+\*\*(.+?)\*\*\n'
        rf'\s+- URL:\s+(https?://\S+)\n'
        rf'\s+- Domain:\s+(\S+)'
    )
    match = re.search(pattern, content)
    if match:
        return match.group(1), match.group(2), match.group(3)

    # Fallback: compact format "N. **Title** — [domain](url)"
    compact_pattern = rf'(?m)^{n}\.\s+\*\*(.+?)\*\*\s+—\s+\[([^\]]+)\]\((https?://\S+?)\)'
    match = re.search(compact_pattern, content)
    if match:
        return match.group(1), match.group(3), match.group(2)

    raise ValueError(f"Article {n} not found in {filepath}")


def article_filepath(n, title, date_str=None):
    """Return the output path for a saved article file.

    Filename format: output/articles/YYYY-MM-DD_NN_slug.md
    """
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:50]
    return os.path.join(ARTICLES_DIR, f'{date_str}_{n:02d}_{slug}.md')


def build_article_header(title, url, domain, n):
    """Return the markdown metadata header for a saved article."""
    fetched = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header  = f"# {title}\n\n"
    header += f"| Field   | Value |\n"
    header += f"|---------|-------|\n"
    header += f"| Article | #{n} |\n"
    header += f"| URL     | {url} |\n"
    header += f"| Domain  | {domain} |\n"
    header += f"| Fetched | {fetched} |\n\n"
    header += "---\n\n"
    return header


def open_in_browser(url):
    """Open a URL in the default browser (macOS)."""
    import subprocess
    subprocess.run(['open', url])


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description='Look up an article from a saved HN file.')
    parser.add_argument('number', type=int, help='Article number (1-based)')
    parser.add_argument('--page', default='main', help="Page type: 'main' or 'front' (default: main)")
    parser.add_argument('--file', default=None, help='Explicit path to an HN output file')
    args = parser.parse_args()

    try:
        title, url, domain = get_article(args.number, page_type=args.page, filepath=args.file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Title:  {title}")
    print(f"URL:    {url}")
    print(f"Domain: {domain}")


if __name__ == '__main__':
    main()
