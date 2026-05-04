#!/usr/bin/env python3
"""
Convert a single PDF to markdown using Marker with OCR enabled.
Usage: convert_pdf.py <pdf_path>
"""

import sys
import json
import tempfile
from pathlib import Path

try:
    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.output import text_to_markdown
except ImportError:
    print(json.dumps({
        "error": "Marker not installed. Install with: pip install marker-pdf"
    }))
    sys.exit(1)


def convert_pdf(pdf_path: str) -> dict:
    """Convert PDF to markdown using Marker with OCR."""
    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        return {"error": f"PDF not found: {pdf_path}"}

    try:
        # Create model dict (loads models once)
        model_dict = create_model_dict()

        # Convert with OCR enabled
        converter = PdfConverter(
            artifact_dict=model_dict,
            max_workers=1,
            disable_image_bbox=False,
            enable_ocr=True  # Enable OCR for scanned documents
        )

        # Convert the PDF
        document, metadata, images = converter.convert_one(pdf_path)

        # Convert to markdown
        markdown_content = text_to_markdown(document)

        if not markdown_content.strip():
            return {"error": "PDF conversion resulted in empty markdown"}

        # Save to temp file
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
