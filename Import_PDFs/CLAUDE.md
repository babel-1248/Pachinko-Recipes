# Import PDFs Recipe

A Claude Code recipe that converts PDF files to markdown and imports them into your Pachinko inbox as notes.

## Usage

Say **"run"** to execute the full pipeline:

1. Scan `PDF_FOLDER` for new PDF files
2. Convert each to markdown (using pymupdf4llm)
3. Add each one to the Pachinko inbox as a markdown note
4. Track converted PDFs so nothing is processed twice

## Setup

1. Open this project in Claude Code — skills load automatically
2. Say "run" to start

**Optional:** Set `CLAUDE_VISION_API_KEY` to use Claude Sonnet 4.6 for conversion — handles scanned PDFs and complex layouts. Without it, falls back to pymupdf4llm (text-based PDFs only).

## Skills included

| Skill   | Description                                                           |
| ------- | --------------------------------------------------------------------- |
| `run` | Full pipeline: scan PDFs → convert to markdown → import to Pachinko |

## State

Converted PDF paths are tracked in `converted_pdfs.json` in the project root. Only PDFs not listed there are processed, preventing duplicates across runs.
