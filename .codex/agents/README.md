# Codex Agents

Codex agent definitions live here.

Start with the [core agent contracts](core-agent-contracts.md) when deciding which venture-builder agent role should own a task.

Use the [agent and skill trigger rules](agent-skill-trigger-rules.md) to load only the smallest relevant agent, skill, and template set for a task.

Use the [agent handoff protocol](agent-handoff-protocol.md) when passing context, decisions, risks, and next steps between agent roles.

Use the [strategy and intake specialization](strategy-intake-specialization.md) when routing idea intake, product strategy, or MVP scope review work.

Each agent should define:

- purpose
- trigger
- required inputs
- expected outputs
- files or skills to read first
- allowed actions
- restricted actions
- approval requirements

Prefer several focused agents over one broad master agent.
