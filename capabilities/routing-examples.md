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
- PM Skills should be selected proactively by the operating agent when the request implies interview planning, risky-assumption mapping, experiment design, PRD inputs, or product strategy structure. The founder should not need to ask for PM Skills by name.
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
- Interview script, synthesis template, or experiment plan when the active phase needs it.
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

## Example 4 - Conversational founder front-door request

Task:

```txt
I have an idea and want to make it work.
```

Primary routing:

- `capability.external.pm-skills` when the current ticket or approved pipeline step needs product discovery structure, interview planning, assumption mapping, or PRD input.
- Repository-native product, validation, C.O.N.T.R.O.L.E., Working Backwards, and discovery artifacts as the default fallback.
- `capability.external.linear-mcp` only when reading or updating approved execution state is part of the current scope.

Why:

- The user is expressing an abstract founder goal, not asking for an implementation task.
- The earliest safe stage is idea intake or founder focus unless durable evidence already proves a later gate is ready.
- PM Skills may help structure product reasoning and should be considered internally when its `useWhen` rules match. The user-facing experience should still be a plain next question or next action.
- Linear MCP may support state tracking after approval, but it should not create tickets or projects merely because the user described an idea.

Do not route to:

- `capability.external.github-mcp`, because there is no branch, PR, or implementation work yet.
- `capability.external.superpowers`, because the request is upstream product guidance, not implementation discipline.
- `capability.external.consensus`, unless the next approved step is source-backed research synthesis.
- `capability.external.notebooklm`, unless an approved source set exists.
- `capability.future.openclaw-paperclip`, because autonomous orchestration remains future-only.

Expected normalized output:

- User goal in plain language.
- Inferred pipeline stage.
- One next founder-facing question.
- Capability route and fallback.
- Durable context checked or missing.
- Approval gates and blocked actions.
- Evidence gaps and next internal artifact.

Example safe user-facing response:

```txt
I understand the goal: you want to turn the idea into something that can work in the market. Before we talk about building, we need to identify who feels the pain most sharply and what evidence is still missing. Tell me the idea in plain language and who you imagine needs it most.
```

## Example 5 - Manual discovery interview plan

Task:

```txt
Create the interview plan for five target users before PRD or build.
```

Primary routing:

- `capability.external.pm-skills`
- Repository-native `validation/respondent-targeting-and-interview-planner.md`
- Repository-native `validation/raw-interview-evidence-intake-and-synthesis.md`
- `capability.external.linear-mcp` for ticket handoff when approved

Why:

- PM Skills provides interview-script, assumption mapping, experiment-design, and transcript-synthesis guidance.
- Pipe validation artifacts preserve approval gates, evidence boundaries, contradiction capture, and GO/NO-GO criteria.
- Linear MCP records execution state, branch/PR links, and follow-ups after approval.

Do not route to:

- `capability.external.notion-mcp` unless the ticket explicitly asks to publish or register the final approved discovery document in Notion.
- `capability.external.consensus`, unless the interview plan also requires source-backed research.
- `capability.external.notebooklm`, unless there is an approved source set to synthesize.
- `capability.external.github-mcp`, unless the work includes repository changes and PR lifecycle.

Expected normalized output:

- Respondent profile.
- Interview objective.
- Non-leading interview script.
- Note-taking or transcript-intake template.
- Evidence categories.
- Contradiction capture.
- GO/NO-GO criteria.
- Blocked actions and approval boundaries.

## Example 6 - Approved documentation registration in Notion

Task:

```txt
Register the approved architecture or validation document in Notion so the founder can read and share it from the workspace.
```

Primary routing:

- `capability.external.notion-mcp`
- `capability.external.linear-mcp`
- Repository-native source artifact

Why:

- Notion MCP is appropriate for approved documentation publishing, registration, search, or update.
- Linear MCP records the Notion link and source artifact in the ticket handoff.
- The repository remains the canonical source for policy, validation artifacts, architecture, and execution docs.

Do not route to:

- Notion if the artifact is unreviewed, sensitive, draft-only, private, or contains raw interview/customer data without approval.
- Notion as a replacement for Git/Linear source of truth.
- Notion for automatic publication merely because a PR merged.

Expected normalized output:

- Source repository artifact.
- Notion page or document URL.
- Sync action performed.
- Approval status.
- Data boundary and residual risk.
