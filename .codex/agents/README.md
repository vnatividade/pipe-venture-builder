# Codex Agents

Codex agent definitions live here.

Use the shared [multi-agent operating protocol](../../execution/multi-agent-operating-protocol.md) before applying Codex-specific routing. Codex-specific instructions must not redefine repository approval gates or Linear/Git execution rules.

Start with the [core agent contracts](core-agent-contracts.md) when deciding which venture-builder agent role should own a task.

Use the [agent and skill trigger rules](agent-skill-trigger-rules.md) to load only the smallest relevant agent, skill, and template set for a task.

Use the [agent handoff protocol](agent-handoff-protocol.md) when passing context, decisions, risks, and next steps between agent roles.

Use the [conversational founder guide specialization](conversational-founder-guide-specialization.md) when the user starts from a vague founder-facing goal, raw idea, validation question, or "what should I do next?" request and should be guided through the Pipe front door instead of being asked to choose files, gates, skills, MCPs, or agents.

Use the [strategy and intake specialization](strategy-intake-specialization.md) when routing idea intake, product strategy, or MVP scope review work.

Use the [research and validation specialization](research-validation-specialization.md) when routing research orchestration, scientific validation, market intelligence, or customer discovery work.

Use the [synthetic persona validation specialization](synthetic-persona-validation-specialization.md) when routing synthetic persona generation, simulation, objection extraction, or comparison against real interviews. This agent is advisory-only and cannot treat synthetic output as market proof.

Use the [venture intelligence curator specialization](venture-intelligence-curator-specialization.md) when routing venture memory, market signals, ranking hygiene, opportunity radar review, KDR/DAR linkage, or evidence freshness work. This agent is advisory-only and cannot approve execution, ticket creation, outreach, or roadmap changes.

Use the [execution and risk specialization](execution-risk-specialization.md) when routing architecture handoff, risk review, ticket decomposition, readiness validation, PR review, or merge handoff work.

Use the [content strategy specialization](content-strategy-specialization.md) when routing founder-led content ideation from validated ICP, offer, channel, and customer-language artifacts.

Use the [distribution and growth specialization](distribution-growth-specialization.md) when routing distribution strategy, channel experiment design, launch readiness, post-launch learning, or growth backlog work.

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
