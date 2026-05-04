# run

Process all new PDFs from PDF_FOLDER, convert them to markdown using Marker with OCR, and import them to Pachinko inbox.

## Prerequisites

1. **Check if Marker is installed**:
   ```bash
   python3 -c "import marker; print('Marker installed')" 2>/dev/null
   ```
   If you see "Marker installed", you're good. If not, install it:
   ```bash
   pip install marker-pdf
   ```

2. **PDF_FOLDER must be set** — the skill checks this before continuing

## Workflow

### Step 0: Check environment variable

Run:
```bash
echo "$PDF_FOLDER"
```

If the output is empty, stop immediately and report: `PDF_FOLDER environment variable is not set. Set it with: export PDF_FOLDER=/path/to/your/pdfs`

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

### Step 2: For each new PDF

For each PDF in the list:

#### 2a. Convert the PDF

Run:
```bash
python3 convert_pdf.py <pdf_path>
```

This returns either:
- **Success**: `{"success": true, "markdown_path": "...", "pdf_name": "..."}`
- **Error**: `{"error": "..."}`

If there's an error, log a warning and continue to the next PDF.

#### 2b. Add to Pachinko

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

- **get_new_pdfs.py returns error**: Report and stop immediately
- **convert_pdf.py returns error**: Log warning, skip that PDF, continue with next
- **mcp__pachinko__add_note fails**: Log warning, still mark PDF as converted, continue
- **mark_converted.py fails**: Log warning but continue

## Marker Details

- Marker converts PDFs to markdown with full layout preservation
- OCR is enabled to handle scanned PDFs and image-based content
- Conversion is single-worker (max_workers=1) for stability
