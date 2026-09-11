# Testes

Suíte: `runtime/tests/` (node:test nativo, zero dependências). Rodar:

```bash
node --test "runtime/tests/*.test.mjs"
```

**Estado atual: 59 testes** across 7 arquivos em `runtime/tests/*.test.mjs` (contagem estática de blocos `test(...)`; ver `runtime/tests/` para a suíte completa, incluída pelas fatias 3–5 além da fatia 1 original).

| Arquivo | Cobre |
|---|---|
| `state-machine.test.mjs` (10) | Caminho feliz completo; transições inválidas recusadas sem mutação; guards (fonte ausente, gate fail, decisões pendentes); pass_with_warnings; fluxo humano; pause/resume com estado anterior; estados terminais; FAIL exige retryExhausted; consistência da tabela de transições; registro com evento/origem/destino/guard/gate |
| `store.test.mjs` (6) | Init/load/list; duplicação recusada; concorrência otimista (VERSION_CONFLICT); escrita atômica; anti path-traversal; logs append-only; fontes ordenadas |
| `units.test.mjs` (10) | Agente (classificação, fato/hipótese, lacunas, rastreabilidade de todo fato); agente com ideia vaga; gate aprova/reprova; gate detecta requisito inventado; reviewer (escopo prematuro, não-rastreável, advisory-only); artifact manager (versão, dedup por hash, supersessão); fila de decisões (idempotência, validação de resposta, resolvida não reprocessa); context loader (precedência, hashes, limite, omissões); contratos recusam objeto inválido; feature flag default off |
| `e2e.test.mjs` (8) | **E2E feliz** (ideia completa → PRODUCT_STRATEGY_READY com eventos, transições e validação anexada); **E2E com decisão humana** (gate fail → WAITING_HUMAN → resposta → retomada → brief v2 → aprovado); cancelamento via decisão; pause/resume; idempotência (projeto, re-execução, artefato); **retomada após interrupção** (run ativa reutilizada); flag off bloqueia mutações; entrada e resposta inválidas mantêm estado |
| `baseline-artifact-typing.test.mjs` (11) | Mapeamento de `artifact_types` por definição/output; recusa de tipo fora do enum do ProductBaseline; gate de pipeline (product-strategy não produz artefato ticketizável); `external_refs` no Project e no manifesto; redação de credenciais do Linear no log |
| `strategy.test.mjs` (6) | Fase product-strategy: transições e retomada da máquina; gate aprova/reprova; E2E feliz até `MVP_REFINEMENT_READY`; E2E com gate-reprova → retry → esgotado → decisão humana; recusas de governança de estado |
| `slice2.test.mjs` (8) | Round-trip `--from-baseline`: paridade com o validador Python do `pipe idea`; recusa de baseline corrompido/inválido; seed markdown verbatim; ciclo completo até baseline v2; idempotência de import/re-run |

## Cenários de falha cobertos

Transição inválida · resposta humana inválida (opção inexistente, texto ausente, sem decided_by) ·
execução duplicada (projeto, run, artefato, decisão) · retry esgotado (via unidade da máquina:
FAIL/retryExhausted) · persistência com conflito de versão · path traversal · flag desabilitada ·
interrupção no meio da run. "Modelo indisponível" não se aplica ao normalizador determinístico —
entra na suíte quando o implementador LLM existir (o caminho de erro do engine com retry→FAILED já
está coberto por injeção de erro estrutural).

## Regressão do comportamento atual

O manual não tem código executável prévio — a regressão relevante é **ausência de efeito**: nenhum
arquivo existente do repositório é alterado pela fatia (verificado por `git status`: apenas
`runtime/` e `docs/venture-os/` novos) e, com a flag off, toda mutação é recusada (testado).
