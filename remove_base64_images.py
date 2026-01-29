#!/usr/bin/env python3
"""
Script to remove base64 images from markdown files.
"""

import re
import sys


def remove_base64_images(input_file, output_file=None):
    """
    Remove base64 images from markdown file.
    Pattern: ![...](data:image/...;base64,...)
    """
    if output_file is None:
        output_file = input_file

    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    original_size = len(content)

    # Match markdown image syntax with base64 data
    # Pattern: ![alt text](data:image/xxx;base64,xxx)
    pattern = r'!\[[^\]]*\]\(data:image/[^;]+;base64,[^)]+\)'
    
    # Count matches
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} base64 images")

    # Replace with empty string or placeholder
    cleaned_content = re.sub(pattern, '[image removed]', content)

    new_size = len(cleaned_content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)

    print(f"Original size: {original_size:,} characters")
    print(f"New size: {new_size:,} characters")
    print(f"Reduced: {original_size - new_size:,} characters ({(1 - new_size/original_size)*100:.1f}%)")
    print(f"Saved to: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python remove_base64_images.py <input_file> [output_file]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    remove_base64_images(input_file, output_file)
