# Import PDFs

A Claude Code and Codex recipe that converts new PDF files into your Pachinko inbox as markdown notes from the provided PDF folder.

## Customization

| Variable                                 | Description                                                                                                                                                                                                          |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `PDF_FOLDER`                           | The path to the folder containing PDF files to import.                                                                                                                                                               |
| `CLAUDE_VISION_API_KEY` *(optional)* | ADVANCED: An Anthropic API key to use Claude Sonnet 4.6 for conversions.  When not set, falls back to the current models Vision capabilities and as a last resort pymupdf4llm which works for text-based PDFs only. |
