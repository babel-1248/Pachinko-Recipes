# Import PDFs Recipe

A Claude Code recipe that converts PDF files to markdown and imports them into your Pachinko inbox as notes.

## Usage

Say **"run"** to execute the full pipeline:

1. Scan `PDF_FOLDER` for new PDF files
2. Convert each to markdown (using Marker)
3. Add each one to the Pachinko inbox as a markdown note
4. Track converted PDFs so nothing is processed twice

## Setup

1. Open this project in Claude Code — skills load automatically
2. Say "run" to start

## Skills included

| Skill   | Description                                                           |
| ------- | --------------------------------------------------------------------- |
| `run` | Full pipeline: scan PDFs → convert to markdown → import to Pachinko |

## State

Converted PDF paths are tracked in `converted_pdfs.json` in the project root. Only PDFs not listed there are processed, preventing duplicates across runs.
