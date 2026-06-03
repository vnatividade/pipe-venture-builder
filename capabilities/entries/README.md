# Capability Entries

This directory stores governed capability registry entries.

Each entry should conform to `../capability.schema.json` and must be updated only through an approved Linear ticket and PR.

PIP-153 creates initial declarative entries for external and hybrid capabilities only. It does not install tools, copy external repositories, create adapters, or authorize new external actions.

## Current Entries

| Entry | Purpose | Lifecycle |
|---|---|---|
| `capability.external.browser-playwright.json` | Browser and UI validation capability. | Pilot/restricted by entry |
| `capability.external.claude-code.json` | Claude Code executor capability. | Pilot/restricted by entry |
| `capability.external.codex.json` | Codex executor capability. | Pilot/restricted by entry |
| `capability.external.consensus.json` | Source-backed research synthesis candidate. | Proposed |
| `capability.external.github-mcp.json` | GitHub issue/PR/repository operations. | Pilot/restricted by entry |
| `capability.external.linear-mcp.json` | Linear ticket/project/status handoff. | Pilot/restricted by entry |
| `capability.external.notebooklm.json` | Approved source-set synthesis candidate. | Proposed |
| `capability.external.notion-mcp.json` | Approved Notion documentation search, publish, update, and registration. | Pilot/restricted |
| `capability.external.pm-skills.json` | PM Skills discovery, interview, PRD, GTM, and product reasoning support from `phuryn/pm-skills`. | Pilot/restricted |
| `capability.external.superpowers.json` | TDD, debugging, review, and verification discipline. | Pilot/restricted |
| `capability.future.openclaw-paperclip.json` | Future orchestration placeholder only. | Future/restricted |

Do not infer approval from this list alone. Agents must still check the assigned ticket, lifecycle, approval triggers, data boundary, and routing examples before using a capability.
