# Agent Skills

Reusable agent skills live here.

Start with the [core skill contracts](core-skill-contracts.md) before authoring any concrete `SKILL.md`.

Use the Codex [agent and skill trigger rules](../../.codex/agents/agent-skill-trigger-rules.md) to decide when a skill should load.

Each skill should define:

- purpose
- required context
- workflow
- inputs
- outputs
- restrictions
- approval requirements

Skills should be small, composable, and invoked only when relevant.

## Shared Skills And Prompts

Default to shared artifacts that Codex and Claude Code can both consume.

Use the smallest artifact that matches the job:

| Artifact | Use When | Do Not Use When |
|---|---|---|
| Skill | A recurring workflow has clear triggers, required context, steps, outputs, and stop conditions. | The need is a one-off instruction, a broad phase playbook, or speculative future behavior. |
| Prompt | A reusable instruction shape or response pattern is needed, but there is no separate workflow contract. | The prompt would duplicate an existing skill, workflow, or agent specialization. |
| Workflow | The work defines state transitions, governance, dependencies, handoff, or cross-tool execution rules. | The work is only a narrow agent instruction. |
| Agent specialization | A durable agent role needs responsibilities, boundaries, escalation rules, and owned outputs. | The need is just a reusable prompt or task checklist. |

Shared-first rule:

- Put common behavior in shared repository artifacts before creating Codex-specific or Claude-specific variants.
- Create a tool-specific artifact only when the tool has a real interface, runtime, context-window, command, or safety difference.
- State the reason for every tool-specific artifact in the artifact itself.
- Do not import external skill or prompt libraries wholesale. Extract only the specific pattern needed by an approved ticket.
- Do not create skills or prompts for speculative future needs.

Prompt directory decision:

- Do not create a top-level `prompts/` directory until there is an approved ticket with at least one concrete shared prompt to store.
- Until then, keep prompt guidance inside the relevant skill, workflow, agent specialization, or template.
- If a future ticket creates `prompts/`, it must include a README explaining ownership, trigger rules, shared vs tool-specific boundaries, and drift prevention.
