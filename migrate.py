#!/usr/bin/env python3
"""
Migration script to convert Gatsby blog posts to Hugo format.
Converts MDX to Markdown and adjusts front matter for Hugo.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path


def parse_frontmatter(content):
    """Extract and parse YAML frontmatter from markdown file."""
    match = re.match(r'^---\s*\n(.*?\n)---\s*\n', content, re.DOTALL)
    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    body = content[match.end():]

    # Parse frontmatter fields
    fm = {}
    for line in frontmatter_str.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            if key == 'tags':
                continue  # Handle tags separately
            elif key == 'date':
                fm[key] = value
            else:
                fm[key] = value

    # Parse tags (array format)
    tags_match = re.search(r'tags:\s*\n((?:\s*-\s*.+\n?)+)', frontmatter_str)
    if tags_match:
        tags_str = tags_match.group(1)
        tags = [tag.strip().lstrip('-').strip() for tag in tags_str.split('\n') if tag.strip()]
        fm['tags'] = tags

    return fm, body


def create_hugo_frontmatter(fm):
    """Create Hugo-compatible YAML frontmatter."""
    hugo_fm = ['---']

    # Title
    if 'title' in fm:
        hugo_fm.append(f'title: "{fm["title"]}"')

    # Date
    if 'date' in fm:
        date_str = fm['date']
        # Ensure date is in proper format
        if len(date_str) == 10:  # YYYY-MM-DD format
            date_str = f"{date_str}T00:00:00+09:00"
        hugo_fm.append(f'date: {date_str}')

    # Slug/URL
    if 'slug' in fm:
        hugo_fm.append(f'slug: "{fm["slug"]}"')

    # Description/Summary
    if 'excerpt' in fm and fm['excerpt'] != '-':
        hugo_fm.append(f'summary: "{fm["excerpt"]}"')
    elif 'description' in fm:
        hugo_fm.append(f'summary: "{fm["description"]}"')

    # Tags
    if 'tags' in fm and fm['tags']:
        hugo_fm.append('tags:')
        for tag in fm['tags']:
            hugo_fm.append(f'  - {tag}')

    # Add default values
    hugo_fm.append('draft: false')
    hugo_fm.append('ShowToc: true')
    hugo_fm.append('TocOpen: false')

    hugo_fm.append('---')
    return '\n'.join(hugo_fm)


def sanitize_filename(title):
    """Create a safe filename from post title."""
    # Remove special characters, replace spaces with hyphens
    safe = re.sub(r'[^\w\s-]', '', title)
    safe = re.sub(r'[-\s]+', '-', safe)
    return safe.lower().strip('-')


def migrate_post(source_dir, ko_dest_dir):
    """Migrate a single blog post from Gatsby to Hugo format."""
    index_file = source_dir / 'index.md'

    if not index_file.exists():
        print(f"  ⚠️  No index.md found in {source_dir.name}")
        return False

    # Read original content
    with open(index_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse frontmatter and body
    fm, body = parse_frontmatter(content)

    if not fm.get('title'):
        print(f"  ⚠️  No title found in {source_dir.name}")
        return False

    # Create Hugo frontmatter
    hugo_frontmatter = create_hugo_frontmatter(fm)

    # Combine frontmatter and body
    new_content = f"{hugo_frontmatter}\n\n{body}"

    # Create destination directory
    # Use sanitized title for directory name
    post_slug = sanitize_filename(fm.get('slug', fm['title']))
    dest_dir = ko_dest_dir / post_slug
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Write new index.md
    dest_file = dest_dir / 'index.md'
    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Copy images and other assets
    for item in source_dir.iterdir():
        if item.name != 'index.md' and item.is_file():
            shutil.copy2(item, dest_dir / item.name)
            print(f"    📎 Copied: {item.name}")

    print(f"  ✅ Migrated: {fm['title']}")
    return True


def main():
    """Main migration function."""
    script_dir = Path(__file__).parent
    source_posts = Path('/tmp/myanglog/content/posts')
    ko_dest = script_dir / 'content' / 'ko' / 'posts'

    if not source_posts.exists():
        print(f"❌ Source directory not found: {source_posts}")
        return

    ko_dest.mkdir(parents=True, exist_ok=True)

    print("🚀 Starting migration from Gatsby to Hugo...")
    print(f"📂 Source: {source_posts}")
    print(f"📂 Destination (Korean): {ko_dest}")
    print()

    # Get all post directories
    post_dirs = [d for d in source_posts.iterdir() if d.is_dir()]

    success_count = 0
    fail_count = 0

    for post_dir in sorted(post_dirs):
        print(f"📝 Processing: {post_dir.name}")
        if migrate_post(post_dir, ko_dest):
            success_count += 1
        else:
            fail_count += 1

    print()
    print("=" * 60)
    print(f"✅ Successfully migrated: {success_count} posts")
    if fail_count > 0:
        print(f"⚠️  Failed: {fail_count} posts")
    print("=" * 60)
    print()
    print("📌 Next steps:")
    print("  1. Review migrated posts in content/ko/posts/")
    print("  2. English versions will need to be created manually or with translation")
    print("  3. Run 'hugo server' to preview the site")


if __name__ == '__main__':
    main()
