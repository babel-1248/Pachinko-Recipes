# Custom Prompt Recipe

A Claude Code recipe that runs a custom prompt with the Pachinko MCP server enabled.

## Post-Execution: Queue Runner

After every execution — including simple responses — always perform the following steps:

1. Run `echo "$QUEUE_RUNNER_IDS"` in bash to read the environment variable value.
2. If the output is empty, stop here.
3. Parse the output as a comma-separated list of runner IDs (e.g. `runner-a,runner-b`).
4. Collect every note that was newly created during this execution.
5. For each runner ID in the list, call `mcp__pachinko__queue_runner` with that runner ID and the list of new note IDs.
   - If there are 10 or fewer new notes, queue all of them in a single call per runner.
   - If there are more than 10 new notes, queue them in batches of 10 per call — each runner receives one call per batch until all notes are queued.
