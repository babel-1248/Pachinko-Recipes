# WebSearch Dossier

Research a topic using multiple targeted web searches, compile the findings into a structured markdown dossier, and add it to the Pachinko inbox as a new note.

## Prerequisites

The environment variable `SEARCH_QUERY` must be set to the topic to research. If it is not set, stop immediately and report: `SEARCH_QUERY environment variable is not set.`

## Steps

### 1. Check environment variable

Run:

```bash
echo "$SEARCH_QUERY"
```

If the output is empty, stop and report: `SEARCH_QUERY environment variable is not set.`

### 2. Plan search queries

Decompose `SEARCH_QUERY` into 4–6 targeted search queries that cover different angles:

- Core definition, background, and context
- Recent news and developments (last 6–12 months)
- Key people, organizations, or products involved
- Analysis, expert opinions, or commentary
- Related trends or adjacent topics (if relevant)

### 3. Execute searches

Run each planned search query using the WebSearch tool. For each result, collect the title, URL, publication date, and the most relevant content.

### 4. Compile the dossier

Synthesize all search results into a structured markdown dossier using the format below. Use only information found in the search results — do not speculate or invent. Omit any section for which no relevant results were found.

```
# {SEARCH_QUERY} — Research Dossier

**Query:** {SEARCH_QUERY}
**Researched:** {current date in YYYY-MM-DD format}

## Overview

{2–4 sentence summary of the topic based on search results}

## Key Findings

### {Thematic heading}
{Concrete findings with inline citations as markdown links: [source title](URL)}

### {Thematic heading}
...

## Recent Developments

{Chronological bullet list of recent news or events, each with source link and date}

## Key Players

{Bullet list of people, organisations, or products central to the topic, with brief descriptions}

## Sources

{Numbered list of every source cited: [Title](URL) — Publisher, Date}
```

### 5. Add to Pachinko

Call `mcp__pachinko__add_note` with:
- `note_title`: `{SEARCH_QUERY} — Dossier`
- `note_body`: the compiled dossier markdown

If the MCP call fails, print the full dossier to the terminal so the content is not lost, then report the error.

### 6. Report results

Print a brief summary:
- Query researched
- Number of web searches performed
- Number of sources cited in the dossier
- Confirmation that the note was added to Pachinko (or the error if it failed)
