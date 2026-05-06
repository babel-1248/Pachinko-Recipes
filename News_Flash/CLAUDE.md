# News Flash Recipe

A Claude Code recipe that searches the web for new information about a topic since the last time it was run and adds a note to the Pachinko inbox. If nothing genuinely new is found, no note is created.

## Usage

Say **"run"** to execute the full pipeline:

1. Load the last-run datetime from `news_flash_state.json` (defaults to 7 days ago on first run)
2. Search the web for news published after that datetime
3. Filter out anything already covered in the previous note
4. If new content exists, compile a News Flash note and add it to the Pachinko inbox
5. Save the updated run datetime and note metadata to `news_flash_state.json`

## Setup

1. Set the `SEARCH_QUERY` environment variable to the topic to monitor
2. Open this project in Claude Code — skills load automatically
3. Say "run" to start

## Skills included

| Skill | Description |
|-------|-------------|
| `run` | Full pipeline: check state → search web → filter new content → add to Pachinko → save state |

## State

Run history is tracked in `news_flash_state.json` in the project root. It stores the last run datetime and the URLs and headlines from the last note, used to verify that new search results are genuinely new.
