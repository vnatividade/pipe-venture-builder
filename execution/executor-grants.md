# Executor Grants — registro canônico de permissões por executor

Fecha o Candidato D de `architecture/orchestration-readiness-analysis.md` (PIP-137): grants que
autorizam ações gated NÃO podem viver apenas em memória local de ferramenta. Este arquivo é o
**registro canônico versionado**; o enforcement em runtime (allowlists de comandos) vive em
configuração machine-local (`~/.claude/settings.json` e equivalentes) e deve refletir este
arquivo — divergência é um finding de auditoria, não uma autorização.

## Regras

1. **Novo grant = PR neste arquivo + aprovação do fundador.** Nenhum grant nasce em settings
   locais; settings locais implementam o que está registrado aqui.
2. Grants operam **dentro** do modo do repositório (`.pipe/mode.json` + `execution/operating-modes.md`).
   Nenhum grant sobrepõe gates absolutos (produção, segredos, billing, dados de cliente, outreach,
   comunicação externa, claims sensíveis, mudança de modo/política).
3. Comandos allowlisted rodam **atômicos** — encadear com `|`/`;`/`&&` invalida o match e cai em
   aprovação por ação (lição registrada em sessão de 2026-07).
4. Revogação: PR removendo a linha + remoção do allowlist local; efeito imediato.

## Grants ativos

| Executor | Identidades | Ações concedidas | Escopo | Origem | Registrado em |
|---|---|---|---|---|---|
| Claude Code | gh `agents-natiivis` (autor) + gh `vnatividade` (review/merge) | `gh pr create`, `gh pr review --approve`, `gh pr merge`, `gh auth switch` (atômicos); loop ticket→branch→PR→merge com review cross-account (autor ≠ revisor) | repositórios em modo `exploration` (este repo desde PIP-716); em `restricted`, só com aprovação por ação na thread | PIP-659 (modos) + PIP-716 (exploration deste repo) + allowlist salva pelo fundador em `~/.claude/settings.json` (2026-07) | 2026-07-28, PIP-731 |
| Codex | conta gh do repositório | idem Claude Code (prefixo de branch `codex/`) | idem | PIP-659/PIP-716; execução real PIP-706..712 | 2026-07-28, PIP-731 |
| Humano (fundador) | `vnatividade` | todas, incluindo gates absolutos e mudança de modo | global | — | — |

## O que NENHUM executor tem

Deploy de produção; segredos/credenciais (leitura ou escrita fora do fluxo Vaultwarden aprovado);
billing/pricing; ads pagos; contato com cliente/comunicação externa; dados de produção; edição de
`.pipe/mode.json`, `execution/operating-modes.md`, `execution/approval-gates.md`, `AGENTS.md`,
`CLAUDE.md` ou deste arquivo sem aprovação humana explícita na thread/ticket.
