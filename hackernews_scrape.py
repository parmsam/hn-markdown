from datetime import datetime
import contextkit.read as rd
import re
import os

PAGE_TYPES = {
    'main': 'Main (Live Front Page)',
    'front': 'Daily Archive (Front Page by Day)',
}

OUTPUT_DIR = 'output'


def build_hn_url(page_type='main', date=None):
    """Build the appropriate HN URL based on page type and date."""
    url_main_page = 'https://news.ycombinator.com/'
    url_day_page = 'https://news.ycombinator.com/front?day={date}'

    if page_type == 'main':
        return url_main_page, datetime.now().strftime('%Y-%m-%d')
    else:
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        return url_day_page.format(date=date), date


def fetch_hn_content(url):
    """Fetch content from HN URL."""
    return rd.read_link(url)


def extract_articles(content):
    """Extract articles from HN content using regex."""
    content_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)\s+\(\[([^\]]+)\]'
    return list(set(re.findall(content_pattern, content)))


def _markdown_header(articles, date_str, page_type):
    """Shared metadata header for all formats."""
    page_label = PAGE_TYPES.get(page_type, page_type)
    header  = f"# Hacker News — {page_label}\n\n"
    header += f"| Field   | Value |\n"
    header += f"|---------|-------|\n"
    header += f"| Date    | {date_str} |\n"
    header += f"| Page    | {page_label} |\n"
    header += f"| Fetched | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |\n"
    header += f"| Count   | {len(articles)} articles |\n\n"
    header += "---\n\n"
    return header


def generate_markdown(articles, date_str, page_type='main'):
    """Full format: one block per article with title, URL, and domain on separate lines."""
    md_content = _markdown_header(articles, date_str, page_type)
    for i, (title, url, domain) in enumerate(articles, 1):
        md_content += f"{i}. **{title}**\n"
        md_content += f"   - URL: {url}\n"
        md_content += f"   - Domain: {domain}\n\n"
    return md_content


def generate_markdown_compact(articles, date_str, page_type='main'):
    """Compact format: one line per article — title linked, domain shown."""
    md_content = _markdown_header(articles, date_str, page_type)
    for i, (title, url, domain) in enumerate(articles, 1):
        md_content += f"{i}. **{title}** — [{domain}]({url})\n"
    return md_content


def resolve_output_path(page_type, date_str, fmt='full', filename=None):
    """Resolve the output file path, creating directories as needed."""
    page_dir = os.path.join(OUTPUT_DIR, page_type)
    os.makedirs(page_dir, exist_ok=True)

    if filename is None:
        suffix = '_compact' if fmt == 'compact' else ''
        filename = f'hackernews_{page_type}_{date_str}{suffix}.md'

    return os.path.join(page_dir, filename)


def save_markdown(content, filepath):
    """Save markdown content to file."""
    with open(filepath, 'w') as f:
        f.write(content)


def save_hn_to_markdown(page_type='main', date=None, fmt='full', filename=None):
    """Main function that orchestrates the HN scraping and saving process.

    Args:
        page_type: 'main' or 'front'
        date:      YYYY-MM-DD string (only used for page_type='front')
        fmt:       'full' (default) or 'compact' (one line per article)
        filename:  override the auto-generated filename
    """
    url, date_str = build_hn_url(page_type, date)

    content = fetch_hn_content(url)
    articles = extract_articles(content)

    if fmt == 'compact':
        md_content = generate_markdown_compact(articles, date_str, page_type)
    else:
        md_content = generate_markdown(articles, date_str, page_type)

    filepath = resolve_output_path(page_type, date_str, fmt, filename)
    save_markdown(md_content, filepath)

    return filepath, len(articles)
