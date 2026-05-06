#!/usr/bin/env python3
"""
Add a PDF path to the converted state file.
Usage: mark_converted.py <pdf_path>
"""

import json
import sys
from pathlib import Path


def mark_converted(pdf_path: str):
    """Add PDF to the converted state file."""
    pdf_file = Path(pdf_path).resolve()

    # Load or create state file
    state_file = Path("converted_pdfs.json")
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {"converted": []}
    else:
        data = {"converted": []}

    # Add if not already present
    pdf_str = str(pdf_file)
    if pdf_str not in data["converted"]:
        data["converted"].append(pdf_str)

    # Save updated state
    with open(state_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Marked as converted: {pdf_file.name}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: mark_converted.py <pdf_path>")
        sys.exit(1)

    mark_converted(sys.argv[1])
