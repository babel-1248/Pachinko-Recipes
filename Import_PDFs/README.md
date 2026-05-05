# Import PDFs

A Claude Code and Codex recipe that converts new PDF files into your Pachinko inbox as markdown notes from the provided PDF folder.

## Customization

| Variable | Description |
| --- | --- |
| `PDF_FOLDER` | The path to the folder containing PDF files to import. |
| `CLAUDE_VISION_API_KEY` *(optional)* | An Anthropic API key to use Claude Sonnet 4.6 for conversion. Handles scanned PDFs and complex layouts. When not set, falls back to pymupdf4llm which works for text-based PDFs only. |
