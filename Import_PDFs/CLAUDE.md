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

PDFs are converted using model vision by default — each page is rendered to an image and the model reads it directly (no API key needed). Set `CLAUDE_VISION_API_KEY` to use the Claude Sonnet 4.6 API instead (useful for large batches). pymupdf4llm is used as a last-resort fallback.

## Skills included

| Skill   | Description                                                           |
| ------- | --------------------------------------------------------------------- |
| `run` | Full pipeline: scan PDFs → convert to markdown → import to Pachinko |

## State

Converted PDF paths are tracked in `converted_pdfs.json` in the project root. Only PDFs not listed there are processed, preventing duplicates across runs.
