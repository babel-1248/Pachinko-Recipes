# Sync RSS Feeds Recipe

A Claude Code recipe that fetches new articles from an RSS/Atom feed, filters them against optional instructions, and adds matching articles to your Pachinko inbox as markdown notes.

## Usage

Say **"run"** to execute the full pipeline:

1. Fetch new articles from the feed (unseen articles only)
2. Optionally filter articles against your filter instructions
3. Add matching articles to the Pachinko inbox as markdown notes
4. Update state so nothing is processed twice

## Setup

1. Set the `FEED_URL` environment variable to the RSS/Atom feed URL
2. Optionally set `FILTER_FILE` to a plain-text file with filtering instructions
3. Open this project in Claude Code — skills load automatically
4. Say "run" to start

## Skills included

| Skill   | Description                                                          |
| ------- | -------------------------------------------------------------------- |
| `run` | Full pipeline: fetch new articles → filter → add to Pachinko inbox |

## State

Seen article IDs are tracked in `feed_state.json` in the project root, keyed by feed URL. Only articles with IDs not present in that file are treated as new.

## Post-Execution: Queue Runner

After every execution — including simple responses — always perform the following steps:

**Important:** Run these commands using `echo "$VAR"` exactly as written. Do not substitute `printenv` or other alternatives.

1. Run `echo "$QUEUE_RUNNER_IDS"` in bash to read the environment variable value.
2. If the output is empty, stop here.
3. Parse the output as a comma-separated list of runner IDs (e.g. `runner-a,runner-b`).
4. Collect every note that was newly created during this execution.
5. For each runner ID in the list, call `mcp__pachinko__queue_runner` with that runner ID and the list of new note IDs.
   - If there are 10 or fewer new notes, queue all of them in a single call per runner.
   - If there are more than 10 new notes, queue them in batches of 10 per call — each runner receives one call per batch until all notes are queued.

## Creating Notes

Before creating any notes, run `echo "$SAVE_TO_PROJECT_ID"` in bash to read the environment variable value. If it is set, create notes in that project. If that project is not found, revert back to inbox. If it is not set, create notes in the inbox by default.

**Important:** Use `echo "$SAVE_TO_PROJECT_ID"` exactly as written. Do not substitute `printenv` or other alternatives.
