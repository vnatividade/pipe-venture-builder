# Capability Routing Examples

These examples validate the initial registry entries from PIP-153.

They are routing checks only. They do not authorize tool installation, external calls, customer contact, production access, or autonomous orchestration.

## Example 1 - Code ticket with tests and review

Task:

```txt
Implement a scoped bug fix with tests, open a PR, address review comments, merge when ready, and update Linear.
```

Primary routing:

- `capability.external.codex`
- `capability.external.superpowers`
- `capability.external.github-mcp`
- `capability.external.linear-mcp`

Why:

- Codex is the default executor for repository-grounded implementation, GitHub, and Linear lifecycle work.
- Superpowers is appropriate for TDD, debugging, review, and verification discipline.
- GitHub MCP is appropriate for PR metadata, review comments, and merge-state checks when approved.
- Linear MCP is appropriate for ticket state, PR attachment, and final delivery handoff when approved.

Do not route to:

- `capability.external.pm-skills`, because product scope is already fixed.
- `capability.external.consensus`, because no research synthesis is requested.
- `capability.future.openclaw-paperclip`, because this is not a future orchestration-prep ticket.

Expected normalized output:

- Branch name.
- PR URL.
- Validation commands and results.
- Review findings by severity.
- Merge commit.
- Linear delivery update.

## Example 2 - Upstream idea validation before code

Task:

```txt
Organize an early venture idea into assumptions, C.O.N.T.R.O.L.E. evaluation, research questions, PRD inputs, and validation plan before implementation.
```

Primary routing:

- `capability.external.pm-skills`
- `capability.external.consensus`
- `capability.external.notebooklm`
- `capability.external.linear-mcp`

Why:

- PM Skills is appropriate for discovery, validation framing, PRD, GTM, and upstream product judgment support.
- Consensus may be appropriate only when the ticket explicitly asks for source-backed research synthesis.
- NotebookLM may be appropriate only when an approved source set exists and external synthesis is approved.
- Linear MCP is appropriate for recording status and handoff, not for inventing evidence.

Do not route to:

- `capability.external.codex` for implementation, because the task is upstream validation before code.
- `capability.external.github-mcp`, unless a PR is part of the approved documentation workflow.
- `capability.future.openclaw-paperclip`, because runtime orchestration is out of scope.

Expected normalized output:

- Assumptions and unknowns.
- Evidence needed.
- Source-backed synthesis with citations if external research is approved.
- Explicit non-evidence boundaries.
- Recommended next Linear tickets or blockers.

## Example 3 - Future orchestration readiness discussion

Task:

```txt
Assess whether OpenClaw or Paperclip should orchestrate Codex and Claude Code after the multi-agent baseline is stable.
```

Primary routing:

- `capability.future.openclaw-paperclip`
- `capability.external.codex`
- `capability.external.claude-code`
- `capability.external.linear-mcp`

Why:

- OpenClaw/Paperclip is visible only as a future evaluation placeholder.
- Codex and Claude Code baseline evidence is required before any runtime comparison.
- Linear MCP may record the future analysis ticket and status when explicitly approved.

Do not route to:

- Any capability that would install, run, schedule, or dispatch OpenClaw/Paperclip now.
- GitHub MCP for merge automation unless the future ticket explicitly includes repository changes.
- Browser/Playwright unless a real UI/runtime validation surface exists.

Expected normalized output:

- Baseline evidence reviewed.
- Orchestration-readiness gaps.
- Comparison criteria.
- Risks and approval gates.
- Future adaptation plan.
