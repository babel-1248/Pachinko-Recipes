# run

Process all new PDFs from PDF_FOLDER, convert them to markdown, and import them to Pachinko inbox.

## Prerequisites

1. **Check PyMuPDF is installed** (required for `pdf_to_images.py` and fallback):
   ```bash
   PYTHONPATH=.packages python3 -c "import fitz"
   ```
   If the command fails, install it (installing pymupdf4llm also installs PyMuPDF):
   ```bash
   pip install --target=.packages pymupdf4llm
   ```

2. **Check pymupdf4llm is installed** (required for fallback when `CLAUDE_VISION_API_KEY` is not set):
   ```bash
   PYTHONPATH=.packages python3 -c "import pymupdf4llm"
   ```
   If the command fails, install it:
   ```bash
   pip install --target=.packages pymupdf4llm
   ```

3. **Check anthropic is installed** (required if `CLAUDE_VISION_API_KEY` is set):
   ```bash
   PYTHONPATH=.packages python3 -c "import anthropic"
   ```
   If the command fails, install it:
   ```bash
   pip install --target=.packages anthropic
   ```

4. **PDF_FOLDER must be set** — `get_new_pdfs.py` will report an error if it isn't

5. **CLAUDE_VISION_API_KEY (optional)**: If set, skips model-vision and calls Claude Sonnet directly via the API instead — useful for large batches where you want a separate API key.

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

Two paths depending on whether `CLAUDE_VISION_API_KEY` is set.

---

**Option A — Model vision (primary, when `CLAUDE_VISION_API_KEY` is NOT set)**

**Step 1**: Render the PDF to images:
```bash
PYTHONPATH=.packages python3 pdf_to_images.py <pdf_path> 2>&1
```
Parse the **last line** as JSON:
- **Success**: `{"success": true, "images": [...], "total_pages": N, "pdf_name": "..."}`
- **Error**: `{"error": "..."}` → fall through to Option B

**Step 2**: For each path in the `images` array, read the image with the Read tool and convert it to clean markdown. Preserve all text, headings, tables (markdown table syntax), and structure. Do not add commentary about images — extract text content only.

**Step 3**: Join the per-page markdown strings with `\n\n---\n\n` separators, then write the result to:
```
/tmp/claude_pdf_imports/<pdf_stem>.md
```
Use the absolute path `/tmp/claude_pdf_imports/<pdf_stem>.md`. Create the directory first if needed:
```bash
mkdir -p /tmp/claude_pdf_imports
```

Use this `markdown_path` in step 2b.

If rendering fails **or** you cannot read the images, fall through to Option B.

---

**Option B — convert_pdf.py (fallback, or when `CLAUDE_VISION_API_KEY` is set)**

Run **in the foreground** with stderr merged:
```bash
PYTHONPATH=.packages python3 convert_pdf.py <pdf_path> 2>&1
```
When `CLAUDE_VISION_API_KEY` is set this calls Claude Sonnet via the API. Otherwise uses pymupdf4llm.

Parse the **last line** as JSON:
- **Success**: `{"success": true, "markdown_path": "...", "pdf_name": "..."}`
- **Error**: `{"error": "..."}`

Do NOT run this with `run_in_background`.

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

- **Model vision (primary)**: `pdf_to_images.py` renders each page at 150 DPI with PyMuPDF. The model reads each image directly and converts to markdown — no extra API key needed. Handles scanned PDFs and complex layouts.
- **Claude Sonnet API** (when `CLAUDE_VISION_API_KEY` is set): `convert_pdf.py` calls `claude-sonnet-4-6` per page using base64-encoded images. Best for large batches where you want a separate API key.
- **pymupdf4llm** (fallback when model vision fails and no `CLAUDE_VISION_API_KEY`): fast, zero API cost, text-based PDFs only. Scanned/image-only pages will be omitted.
