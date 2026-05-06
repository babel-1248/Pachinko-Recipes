# run

Process all new PDFs from PDF_FOLDER, convert them to markdown, and import them to Pachinko inbox.

## Prerequisites

1. **Check pymupdf4llm is installed**:
   ```bash
   PYTHONPATH=.packages python3 -c "import pymupdf4llm"
   ```
   If the command fails, install it:
   ```bash
   pip install --target=.packages pymupdf4llm
   ```

2. **Check anthropic is installed** (required if `CLAUDE_VISION_API_KEY` is set):
   ```bash
   PYTHONPATH=.packages python3 -c "import anthropic"
   ```
   If the command fails, install it:
   ```bash
   pip install --target=.packages anthropic
   ```

3. **PDF_FOLDER must be set** — `get_new_pdfs.py` will report an error if it isn't

4. **CLAUDE_VISION_API_KEY (optional)**: If set, conversion uses Claude vision for best quality — handles scanned PDFs, complex layouts, and image-heavy documents. Without it, falls back to pymupdf4llm which works well for text-based PDFs.

## Workflow

### Step 1: Get new PDFs

Run:
```bash
python3 get_new_pdfs.py
```

This returns a JSON array of new PDFs not yet converted:
```json
[
  {"path": "/path/to/file1.pdf", "name": "file1.pdf"},
  {"path": "/path/to/file2.pdf", "name": "file2.pdf"}
]
```

If the array is empty, report that there are no new PDFs to process and stop.

### Step 2: Process each new PDF sequentially

**IMPORTANT: Process PDFs one at a time.** Do NOT batch convert. Each iteration must:
1. Convert to markdown
2. Call `mcp__pachinko__add_note` to import to Pachinko
3. Mark as converted

For each PDF in the list:

#### 2a. Convert the PDF

Run **in the foreground** with stderr merged so page progress is visible inline:
```bash
PYTHONPATH=.packages python3 convert_pdf.py <pdf_path> 2>&1
```

The script prints `Page X of Y` lines to stderr as it works, then emits a single JSON object on the last line of stdout. Parse the **last line** as JSON:
- **Success**: `{"success": true, "markdown_path": "...", "pdf_name": "..."}`
- **Error**: `{"error": "..."}`

Do NOT run this with `run_in_background` — it mixes stderr and stdout into the same output file, making the JSON result hard to extract.

If there's an error, log a warning and continue to the next PDF.

#### 2b. Add to Pachinko (LLM tool call required)

Call `mcp__pachinko__add_note` with:
- `note_title`: The PDF filename without extension (use `pdf_name` to extract it)
- `note_body_file_path`: The `markdown_path` from the conversion result

If this call fails, log a warning and continue to the next PDF.

#### 2c. Mark as converted

Run:
```bash
python3 mark_converted.py <pdf_path>
```

This updates the state file (`converted_pdfs.json`) to prevent reprocessing.

### Step 3: Report results

Print a summary:
- Total new PDFs found
- Number successfully converted and imported to Pachinko
- Number skipped due to conversion errors
- List of PDF names that were processed

## State Management

**File**: `converted_pdfs.json` (in project root)

Format:
```json
{
  "converted": [
    "/absolute/path/to/file1.pdf",
    "/absolute/path/to/file2.pdf"
  ]
}
```

Only PDFs in this list are skipped on future runs.

## Error Handling

- **get_new_pdfs.py returns error**: Report and stop immediately (includes missing PDF_FOLDER)
- **convert_pdf.py returns error**: Log warning, skip that PDF, continue with next
- **mcp__pachinko__add_note fails**: Log warning, still mark PDF as converted, continue
- **mark_converted.py fails**: Log warning but continue

## Conversion Details

- **Claude vision** (when `CLAUDE_VISION_API_KEY` is set): renders each page at 150 DPI and sends to `claude-sonnet-4-6`. Best quality, handles scanned PDFs. Pages are joined with `---` separators.
- **pymupdf4llm** (fallback): fast, zero API cost, works well for text-based PDFs. Scanned/image-only pages will be omitted.
