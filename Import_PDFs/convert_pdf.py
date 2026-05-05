#!/usr/bin/env python3
"""
Convert a single PDF to markdown.
- If CLAUDE_VISION_API_KEY is set: uses Claude vision (best quality, handles scanned PDFs)
- Otherwise: uses pymupdf4llm (fast, text-based PDFs only)

Usage: convert_pdf.py <pdf_path>
"""

import os
import sys
import json
import base64
import tempfile
from pathlib import Path

try:
    import fitz  # PyMuPDF, bundled with pymupdf4llm
except ImportError:
    print(json.dumps({"error": "pymupdf4llm not installed. Install with: pip install pymupdf4llm"}))
    sys.exit(1)

try:
    import pymupdf4llm
except ImportError:
    print(json.dumps({"error": "pymupdf4llm not installed. Install with: pip install pymupdf4llm"}))
    sys.exit(1)


def convert_with_claude(pdf_path: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_VISION_API_KEY"))
    doc = fitz.open(pdf_path)
    total = len(doc)
    pages_markdown = []

    for page_num in range(total):
        print(f"  Page {page_num + 1} of {total}", file=sys.stderr, flush=True)
        page = doc[page_num]
        # Render at 150 DPI — good balance of quality vs token cost
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        image_data = base64.standard_b64encode(pix.tobytes("png")).decode()

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "Convert this PDF page to clean markdown. "
                            "Preserve all text, tables, headings, and structure. "
                            "For tables use markdown table syntax. "
                            "Do not add commentary or descriptions of images — just extract the text content. "
                            "Output only the markdown, nothing else."
                        ),
                    },
                ],
            }],
        )
        pages_markdown.append(response.content[0].text)

    doc.close()
    return "\n\n---\n\n".join(pages_markdown)


def convert_with_pymupdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    total = len(doc)
    doc.close()
    print(f"  Converting {total} pages with pymupdf4llm...", file=sys.stderr, flush=True)
    result = pymupdf4llm.to_markdown(pdf_path)
    print(f"  Done ({total} pages)", file=sys.stderr, flush=True)
    return result


def convert_pdf(pdf_path: str) -> dict:
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        return {"error": f"PDF not found: {pdf_path}"}

    try:
        if os.environ.get("CLAUDE_VISION_API_KEY"):
            markdown_content = convert_with_claude(pdf_path)
        else:
            markdown_content = convert_with_pymupdf(pdf_path)

        if not markdown_content.strip():
            return {"error": "PDF conversion resulted in empty markdown"}

        temp_dir = Path(tempfile.gettempdir()) / "claude_pdf_imports"
        temp_dir.mkdir(exist_ok=True)

        md_file = temp_dir / f"{pdf_file.stem}.md"
        md_file.write_text(markdown_content, encoding="utf-8")

        return {
            "success": True,
            "markdown_path": str(md_file),
            "pdf_name": pdf_file.name
        }

    except Exception as e:
        return {"error": f"Failed to convert {pdf_path}: {str(e)}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: convert_pdf.py <pdf_path>"}))
        sys.exit(1)

    result = convert_pdf(sys.argv[1])
    print(json.dumps(result))
