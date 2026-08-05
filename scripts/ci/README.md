# Definição de CI (aguardando instalação)

`ci.yml` é a primeira CI do repositório (PIP-835, itens 1–3). Ele está aqui, e não
em `.github/workflows/`, por uma razão de permissão — não de desenho.

Publicar arquivo em `.github/workflows/` exige o escopo `workflow` no token. A conta
que os agentes usam como **autora** (`agents-natiivis`) tem `repo`, mas não
`workflow`. A conta `vnatividade` tem.

Empurrar como `vnatividade` resolveria em um comando, e é exatamente o que não foi
feito: `vnatividade` é a conta **revisora**. Autor igual a revisor anula o controle
cross-account de `execution/executor-grants.md`, que existe para pegar erro do
executor. Um agente não enfraquece sozinho o controle que o vigia.

Conceder `workflow` a `agents-natiivis` também não é decisão de executor: é grant
novo, e `execution/executor-grants.md` §Regras exige PR naquele arquivo com
aprovação do fundador.

## Instalar (decisão do fundador)

**Opção A — o fundador instala o arquivo**, sem mudar permissão de ninguém:

```sh
mkdir -p .github/workflows
git mv scripts/ci/ci.yml .github/workflows/ci.yml
git commit -m "PIP-835: ativar CI" && git push
```

**Opção B — conceder o escopo à conta autora**, registrando o grant primeiro:

```sh
gh auth refresh -h github.com -u agents-natiivis -s workflow
```

A opção A não amplia permissão de agente nenhum e é reversível por revert. A B
amplia, e por isso pede PR em `execution/executor-grants.md` antes.

## O que o arquivo faz

Três jobs: suíte Node, suíte Python e um check de deriva que regenera a matriz de
campos e reprova se o Markdown commitado divergir de `contracts/ticket-field-matrix.json`.
