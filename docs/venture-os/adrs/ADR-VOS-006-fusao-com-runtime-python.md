# ADR-VOS-006 — Fusão com o runtime Python (pip-706..711): fronteira de responsabilidade

Status: Accepted · 2026-07-27 · Autorizada pelo fundador na thread ("pode fundir")

**Contexto.** Ao auditar para a fusão, constatou-se que as branches `pip-706..711` e `pip-716` **já
haviam sido merged** no `origin/main` (PRs #146–#152, squash), incluindo a ativação do modo
`exploration` (PIP-716, fundador, 2026-07-21). O main contém um runtime **Python**
(`src/pipe_venture_builder`, CLI `pipe`, 170 testes verificados verdes nesta auditoria) cobrindo:
intake dual (`pipe idea`/`pipe adopt` → **ProductBaseline schema-válido**), bootstrap/doctor,
manifest, connectors read-only Linear/GitHub e reconciliation planner. O checkout local estava
defasado (f4f8e01), o que fazia as branches parecerem não mergeadas na análise anterior.

**Problema.** Dois runtimes agora coexistem: Python `pipe` (intake/baseline/portabilidade, sem loop
de execução) e Node `pipe-os` (fatia vertical: máquina de estados, workflow, gates, HITL, eventos —
sem baseline). Sobreposição real: ambos fazem "intake de ideia".

**Opções.** (A) Fronteira por responsabilidade, com o ProductBaseline como contrato de integração;
(B) portar a fatia Node para Python; (C) portar o baseline para Node; (D) descartar um dos dois.

**Decisão.** **A.** O Python `pipe` é dono da **geração de estado canônico** (ProductBaseline via
idea/adopt, bootstrap, connectors, reconciliação — a sequência do ADR-001 do repo). O Node `pipe-os`
é dono do **loop de execução** (máquina de estados, workflow, gate engine, HITL, eventos). O
contrato entre eles é o `ProductBaseline` (schema canônico em `schemas/`): o próximo passo da fatia
consome/emite baseline em vez de manter contrato `Project` isolado. O brief da fatia
(`initial-brief`) permanece como artefato interno do loop; a fonte canônica de intake passa a ser o
baseline gerado por `pipe idea`.

**Trade-offs aceitos.** Dois stacks no toolkit (custo de manutenção real, mitigado por fronteira
estreita e contrato único); dedup do intake resolvida por precedência (baseline canônico > brief
operacional). B/C descartariam trabalho testado (170 testes Python / 34 Node) sem ganho funcional;
D perderia ou o estado canônico ou o loop de execução.

**Consequências.** `migration-status.md` atualizado; próxima fatia = ponte pipe-os ↔ baseline.
**Revisão quando:** a ponte existir e a dedup de intake puder ser medida; ou quando o fundador
decidir consolidar stack. **Migração:** nenhuma quebra — os dois CLIs continuam independentes até a ponte.
