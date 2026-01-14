#!/usr/bin/env python3
"""
Fix malformed markdown links in migrated posts.
Converts [text]([url](url)) to [text](url)
"""

import re
from pathlib import Path


def fix_links_in_content(content):
    """Fix malformed markdown links."""
    # Pattern: [text]([url](url)) -> [text](url)
    # This matches cases where the link is duplicated
    pattern = r'\[([^\]]+)\]\(\[([^\]]+)\]\([^\)]+\)\)'
    fixed = re.sub(pattern, r'[\1](\2)', content)

    return fixed


def fix_links_in_file(filepath):
    """Fix links in a single markdown file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixed_content = fix_links_in_content(content)

    if original_content != fixed_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return True
    return False


def main():
    """Fix links in all markdown files."""
    script_dir = Path(__file__).parent
    content_dir = script_dir / 'content'

    print("🔧 Fixing malformed markdown links...")

    fixed_count = 0
    total_count = 0

    for md_file in content_dir.rglob('*.md'):
        total_count += 1
        if fix_links_in_file(md_file):
            fixed_count += 1
            print(f"  ✅ Fixed: {md_file.relative_to(content_dir)}")

    print()
    print(f"✅ Processed {total_count} files, fixed {fixed_count} files")


if __name__ == '__main__':
    main()
