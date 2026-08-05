# Definição de CI — ATIVADA

`ci.yml` vive em `.github/workflows/ci.yml` desde a ativação pelo fundador.

Este arquivo fica como registro de por que houve um passo intermediário.

## O que aconteceu

Publicar em `.github/workflows/` exige o escopo `workflow` no token. A conta que os
agentes usam como **autora** (`agents-natiivis`) tem `repo`, mas não `workflow`. A
conta `vnatividade` tem.

Empurrar como `vnatividade` resolveria em um comando, e é exatamente o que não foi
feito na entrega de PIP-835: `vnatividade` é a conta **revisora**, e autor igual a
revisor anula o controle cross-account de `execution/executor-grants.md` — que
existe para pegar erro do executor. Um agente não enfraquece sozinho o controle que
o vigia.

Conceder `workflow` a `agents-natiivis` também não seria decisão de executor: é
grant novo, e `execution/executor-grants.md` §Regras exige PR naquele arquivo com
aprovação do fundador.

O fundador escolheu a opção que **não amplia permissão de agente nenhum**: empurrar
o arquivo com a própria conta. A permissão dos executores segue inalterada.

## O que a CI faz

Três jobs: suíte Node, suíte Python e um check de deriva que regenera a matriz de
campos e reprova se o Markdown commitado divergir de `contracts/ticket-field-matrix.json`.
