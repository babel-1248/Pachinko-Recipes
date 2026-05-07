#!/usr/bin/env python3
"""
Write markdown content to /tmp/claude_pdf_imports/<filename>.md
Usage: write_markdown.py <filename_stem> <markdown_content>
Prints the absolute output path on success.
"""

import os
import sys

OUTPUT_DIR = "/tmp/claude_pdf_imports"


def write_markdown(filename_stem: str, content: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, f"{filename_stem}.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: write_markdown.py <filename_stem> <markdown_content>")
        sys.exit(1)

    stem = sys.argv[1]
    markdown = sys.argv[2]

    path = write_markdown(stem, markdown)
    print(path)
