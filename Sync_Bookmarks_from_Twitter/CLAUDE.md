# XBookmarks Recipe

A Claude Code recipe that syncs new X/Twitter bookmarks into your Pachinko inbox as markdown notes, using [fieldtheory-cli](https://github.com/afar1/fieldtheory-cli).

## Usage

Say **"run"** to execute the full pipeline:

1. Sync new bookmarks from X (via Chrome session)
2. Find bookmarks not yet sent to Pachinko
3. Add each one to the Pachinko inbox as a markdown note
4. Track sent IDs so nothing is duplicated

## Setup

1. Ensure Node.js 20+ is installed
2. Open Chrome and log into x.com (used for session-based sync)
3. Open this project in Claude Code — skills load automatically
4. Say "run" to start

## Skills included

| Skill           | Description                                                       |
| --------------- | ----------------------------------------------------------------- |
| `run`         | Full pipeline: sync bookmarks → push new ones to Pachinko inbox  |
| `fieldtheory` | Direct access to fieldtheory-cli (sync, search, classify, export) |

## State

Processed bookmark IDs are tracked in `~/.ft-bookmarks/.pachinko-sent-ids` so each bookmark is only added to Pachinko once.

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
