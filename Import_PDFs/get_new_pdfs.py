#!/usr/bin/env python3
"""
Read the state file and return a list of new PDF files in PDF_FOLDER.
"""

import json
import os
import sys
from pathlib import Path


def get_new_pdfs():
    """Return list of new PDFs not yet in the state file."""
    pdf_folder = Path(os.getenv("PDF_FOLDER", "."))

    if not pdf_folder.exists():
        print(json.dumps({"error": f"PDF_FOLDER not found: {pdf_folder}"}))
        sys.exit(1)

    # Load state file
    state_file = Path("converted_pdfs.json")
    converted = set()
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
                converted = set(data.get("converted", []))
        except json.JSONDecodeError:
            converted = set()

    # Find all PDFs
    pdf_files = sorted(pdf_folder.glob("*.pdf"))
    new_pdfs = []

    for pdf_file in pdf_files:
        pdf_path = str(pdf_file.resolve())
        if pdf_path not in converted:
            new_pdfs.append({
                "path": pdf_path,
                "name": pdf_file.name
            })

    print(json.dumps(new_pdfs))


if __name__ == "__main__":
    get_new_pdfs()
