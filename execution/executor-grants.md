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
5. **Ordem do loop cross-account:** a conta autora abre a PR, a conta revisora aprova, e **a conta
   autora executa o merge**. O arquivo descrevia o loop sem dizer quem mergeia, e a prática divergiu
   (PRs #164 a #171 foram mergeados pela conta revisora — o controle autor ≠ revisor foi preservado,
   mas o merge estava do lado errado). Corrigido a partir do PR #173.
6. **Verificar a conta ativa no mesmo comando da ação privilegiada.** A conta ativa do `gh` é estado
   compartilhado entre sessões concorrentes e **não é confiável** entre comandos: em 2026-08-06 outra
   sessão a trocou no meio de um fluxo e um PR de grant saiu assinado pela conta revisora, o que teria
   anulado o próprio controle que o PR registrava. O padrão é conferir e abortar:

   ```sh
   [ "$(gh api user --jq .login)" = "agents-natiivis" ] || { echo "ABORTANDO"; exit 1; }
   ```

## Grants ativos

| Executor | Identidades | Ações concedidas | Escopo | Origem | Registrado em |
|---|---|---|---|---|---|
| Claude Code | gh `agents-natiivis` (autor **e merge**) + gh `vnatividade` (review) | `gh pr create`, `gh pr review --approve`, `gh pr merge`, `gh auth switch` (atômicos); loop ticket→branch→PR→merge com review cross-account (autor ≠ revisor), na ordem da regra 5 | repositórios em modo `exploration` (este repo desde PIP-716); em `restricted`, só com aprovação por ação na thread | PIP-659 (modos) + PIP-716 (exploration deste repo) + allowlist salva pelo fundador em `~/.claude/settings.json` (2026-07) | 2026-07-28, PIP-731 |
| Codex | conta gh do repositório | idem Claude Code (prefixo de branch `codex/`) | idem | PIP-659/PIP-716; execução real PIP-706..712 | 2026-07-28, PIP-731 |
| Humano (fundador) | `vnatividade` | todas, incluindo gates absolutos e mudança de modo | global | — | — |
| Escrita no Linear | app OAuth `Pipe` (`viewer.id` `ea826709-3baf-4e9d-bbf1-2468d1dc403e`, e-mail `@oauthapp.linear.app`), assumido por Claude Code e Codex; `client_id`/`client_secret` no Vaultwarden | criar e atualizar issue, comentário e attachment **somente pelo caminho `apply`** (plano de reconciliação → aprovação humana registrada em `ApprovalRecord` → `execute` → `verify`); nunca escrita ad hoc | apenas o projeto declarado em `.pipe/linear.json` do repositório em execução; a **leitura** continua pela API key pessoal | PIP-838 (decisão D1 do fundador, 2026-08-05) | PIP-840 |

### Escrita no Linear — o grant é mais estreito que o token

O token do app tem `scope: read write`, que tecnicamente permite muito mais do que a linha acima
concede. **O grant é o limite de política, não o limite do token.** Quem ler esta tabela como
descrição do que a credencial consegue fazer vai errar; ela descreve o que é autorizado.

Proibido para qualquer executor, mesmo com o token na mão e mesmo em `exploration`:

- apagar ou arquivar issue, projeto, comentário ou anexo;
- criar, renomear ou remover label, estado de workflow, time ou iniciativa — mudar taxonomia é
  mudança de estrutura do workspace e exige aprovação nomeada;
- escrever em projeto que não seja o declarado no `.pipe/linear.json` do repositório em execução;
- escrever fora do caminho `apply` — em particular, criar ticket direto por MCP em sessão sem o
  plano aprovado correspondente;
- usar comentário no Linear como registro de aprovação de gate absoluto.

Este grant não altera nenhum gate absoluto. Produção, segredos, billing, dados de cliente e
comunicação externa seguem exigindo aprovação humana em todos os modos.

## O que NENHUM executor tem

Deploy de produção; segredos/credenciais (leitura ou escrita fora do fluxo Vaultwarden aprovado);
billing/pricing; ads pagos; contato com cliente/comunicação externa; dados de produção; edição de
`.pipe/mode.json`, `execution/operating-modes.md`, `execution/approval-gates.md`, `AGENTS.md`,
`CLAUDE.md` ou deste arquivo sem aprovação humana explícita na thread/ticket.
