#!/usr/bin/env python3
"""
Split a PDF into one PNG image per page.

Usage: pdf_to_images.py <pdf_path>

Outputs JSON on stdout:
  success: {"success": true, "images": ["/tmp/.../page_001.png", ...], "total_pages": N, "pdf_name": "..."}
  error:   {"error": "..."}
"""

import json
import sys
import tempfile
from pathlib import Path

try:
    import fitz
except ImportError:
    print(json.dumps({"error": "PyMuPDF not installed. Install with: pip install pymupdf4llm"}))
    sys.exit(1)


def pdf_to_images(pdf_path: str) -> dict:
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        return {"error": f"PDF not found: {pdf_path}"}

    try:
        doc = fitz.open(pdf_path)
        total = len(doc)

        out_dir = Path(tempfile.gettempdir()) / "claude_pdf_imports" / pdf_file.stem
        out_dir.mkdir(parents=True, exist_ok=True)

        image_paths = []
        # 150 DPI — good balance of quality vs file size for vision models
        mat = fitz.Matrix(150 / 72, 150 / 72)

        for i in range(total):
            print(f"  Rendering page {i + 1} of {total}", file=sys.stderr, flush=True)
            pix = doc[i].get_pixmap(matrix=mat)
            img_path = out_dir / f"page_{i + 1:03d}.png"
            pix.save(str(img_path))
            image_paths.append(str(img_path))

        doc.close()

        return {
            "success": True,
            "images": image_paths,
            "total_pages": total,
            "pdf_name": pdf_file.name,
        }

    except Exception as e:
        return {"error": f"Failed to render {pdf_path}: {str(e)}"}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: pdf_to_images.py <pdf_path>"}))
        sys.exit(1)

    result = pdf_to_images(sys.argv[1])
    print(json.dumps(result))
