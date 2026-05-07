# run

Process all new PDFs from PDF_FOLDER, convert them to markdown, and import them to Pachinko inbox.

**IMPORTANT: Run every bash command as a single, standalone tool call. Never concatenate commands with `&&`, `;`, `||`, or pipe them together. Each command must be its own separate Bash tool call.**

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

5. **CLAUDE_VISION_API_KEY (optional)**: Check whether it is set:
   ```bash
   echo "$CLAUDE_VISION_API_KEY"
   ```
   If the output is non-empty, use Option B (Claude Sonnet API). Otherwise use Option A (model vision).

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

Two paths depending on `CLAUDE_VISION_API_KEY` (check with `echo "$CLAUDE_VISION_API_KEY"` — non-empty means set).

---

**Option A — Model vision (primary, when `CLAUDE_VISION_API_KEY` is NOT set)**

This path is mandatory when `CLAUDE_VISION_API_KEY` is not set. Do not skip it or switch to Option B for speed, convenience, document length, text-native PDFs, or any other optimization. Option B is allowed only after an actual error occurs during rendering, image reading, or direct image-to-markdown conversion.

**No text-layer shortcuts in Option A.** After pages render successfully, the markdown must be produced from the rendered page images themselves. Do not use `pymupdf4llm`, PyMuPDF text extraction, `convert_pdf.py`, `pdftotext`, embedded PDF text layers, copy/paste from a PDF viewer, or any other text-layer extractor as a substitute for reading the page images. This remains true even when the PDF is text-native, searchable, long, table-heavy, or easier to extract from the text layer.

**No local OCR substitutes in Option A.** Do not use local OCR tools, Apple Vision OCR, Tesseract, OCR libraries, or other non-model OCR as a substitute for the model reading the rendered page images. This remains true when the PDF is large, dense, table-heavy, or when local OCR seems more accurate, faster, cheaper, or easier. Accuracy concerns are not a reason to bypass direct model vision; instead, read the rendered images directly and preserve the visible content as well as possible.

**Step 1**: Render the PDF to images:
```bash
PYTHONPATH=.packages python3 pdf_to_images.py <pdf_path> 2>&1
```
Parse the **last line** as JSON:
- **Success**: `{"success": true, "images": [...], "total_pages": N, "pdf_name": "..."}`
- **Error**: `{"error": "..."}` → fall through to Option B

**Step 2**: For each path in the `images` array, read the image with the Read tool and convert it to clean markdown using only the visual content visible in that rendered image. Preserve all text, headings, tables (markdown table syntax), and structure. Do not add commentary about images — extract text content only.

If a page image cannot be read or cannot be converted directly to markdown from the image pixels, treat that as an error and fall through to Option B for the whole PDF. Do not fall through after successful image reads just because another converter may be faster, more accurate, cheaper, or available through the PDF text layer.

**Step 3**: Join the per-page markdown strings with `\n\n---\n\n` separators, then write the result to a unique path. Generate a timestamp first:
```bash
date +%Y%m%dT%H%M%S
```
Then write to `/tmp/claude_pdf_imports/<pdf_stem>_<timestamp>.md` using `write_markdown.py` — do NOT use the Write tool or shell redirection, as they are blocked for `/tmp`.

**IMPORTANT: Do NOT pass the markdown content as a shell argument.** The sandbox blocks multiline strings (and strings containing `#` after a newline) passed as shell arguments. Instead, call `write_markdown.py` via an inline Python script:
```bash
python3 - <<'PYEOF'
content = """<markdown_content>"""
import subprocess, sys
result = subprocess.run(
    [sys.executable, "write_markdown.py", "<pdf_stem>_<timestamp>", content],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr)
PYEOF
```
The script creates `/tmp/claude_pdf_imports/` if needed and prints the absolute output path on success. Use that printed path as `markdown_path` in step 2b.

If rendering fails, an image cannot be read, or direct image-to-markdown conversion errors, fall through to Option B. Otherwise use this `markdown_path` and continue to step 2b.

---

**Option B — convert_pdf.py (fallback after direct-conversion error, or when `CLAUDE_VISION_API_KEY` is set)**

When `CLAUDE_VISION_API_KEY` is not set, run this option only after Option A has produced an actual error. Do not use `convert_pdf.py`, `pymupdf4llm`, PyMuPDF text extraction, or any other text-layer extractor as an optimization or shortcut after Option A succeeds.

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
- **model-vision conversion succeeds**: Use its generated markdown from the rendered images; do not run `convert_pdf.py`, `pymupdf4llm`, PyMuPDF text extraction, or any other text-layer extractor as an optimization
- **model-vision conversion errors**: Fall back to `convert_pdf.py`
- **convert_pdf.py returns error**: Log warning, skip that PDF, continue with next
- **mcp__pachinko__add_note fails**: Log warning, still mark PDF as converted, continue
- **mark_converted.py fails**: Log warning but continue

## Conversion Details

- **Model vision (primary)**: `pdf_to_images.py` renders each page at 150 DPI with PyMuPDF. The model reads each image directly and converts to markdown — no extra API key needed. Handles scanned PDFs and complex layouts.
- **Claude Sonnet API** (when `CLAUDE_VISION_API_KEY` is set): `convert_pdf.py` calls `claude-sonnet-4-6` per page using base64-encoded images. Best for large batches where you want a separate API key.
- **pymupdf4llm** (fallback when model vision fails and no `CLAUDE_VISION_API_KEY`): fast, zero API cost, text-based PDFs only. Scanned/image-only pages will be omitted.
