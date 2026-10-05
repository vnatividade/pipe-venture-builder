# Modelos e entregáveis em outra máquina

PIP-1007 leva a política de Codex/Claude para o pacote instalável do Pipe.
A fonte canônica é `src/pipe_venture_builder/model_policy/`: matriz, helper e
POLICY/ONBOARDING. A lógica foi importada da entrega PIP-1001; decisões de papéis
permanecem iguais. Não copie a pasta de configuração, receipt, sessão ou cofre da
máquina anterior. O pacote contém apenas código e política versionada.

## Importar e configurar

Transporte um clone/arquivo versionado do Pipe que contenha esta entrega ou instale
seu wheel revisado. Uma cópia de um produto sem o toolkit Pipe não contém o comando.
Python 3.11+ é necessário. macOS/Linux suportam instalação automática; Windows
pode usar seleção e inspeção, mas a instalação global e registro de lançamento
retornam bloqueio explícito antes de escrever. Windows não foi validado nativamente.

No clone, em um ambiente virtual:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
pipe model-policy --json install --plan
pipe model-policy --json install --apply
```

`install` sem opção é plano. Examine `changed_paths` antes de aplicar: a instalação
é **global para o usuário local**, separada de `pipe bootstrap` do produto. Nenhum
runtime é instalado ou autenticado pelo comando. Instale/autentique Codex/Claude
no ambiente novo por seus próprios fluxos; não transporte credenciais. Modelos
indisponíveis são impedimentos; não há fallback de provedor.

A instalação grava somente política em `~/.agents/model-policy/`, blocos delimitados
em `~/AGENTS.md`, `~/.codex/AGENTS.md` e `~/.claude/CLAUDE.md`, chaves de modelo/esforço
nas configurações globais e wrapper `~/.local/bin/agent-model`. Se `repo-padrao` já
estiver instalado, acrescenta apenas o bloco de onboarding à skill existente.
Backups privados e hashes ficam em `~/.local/state/agent-model/backups/`; receipt
em `~/.agents/model-policy/INSTALLATION.json`. Os caminhos absolutos nesses receipts
são gerados **na máquina destino**, não fazem parte dos artefatos de produto.

`~/.local/bin` precisa estar no PATH para usar `agent-model`; `pipe model-policy`
continua disponível pelo ambiente virtual. O wrapper fixa o Python que instalou;
se remover esse ambiente, ele deixará de funcionar. Preserve o ambiente ou faça
uma atualização revisada para um Python estável do destino.

O instalador usa as homes padrão. `CODEX_HOME` ou `CLAUDE_CONFIG_DIR` customizados
bloqueiam instalação padrão para evitar configurar arquivos ignorados pelo runtime.
`--home /caminho` (antes de `install`) é uma home destino explícita para fixtures
ou ambiente isolado, não transporte de configurações entre usuários.

## Verificar no projeto importado

```sh
pipe model-policy --json inspect --runtime codex --project /caminho/projeto
pipe model-policy --json inspect --runtime claude --project /caminho/projeto
pipe model-policy --json select --runtime codex --task feature
pipe model-policy --json check --runtime codex --project /caminho/projeto
```

No plano por arquivos: builder Codex `gpt-6.1-sol`/`medium`, Claude `sonnet`/`medium`.
Worker usa Luna Low/Haiku; Architect usa Astra/Opus Medium; Reviewer usa Astra Low
(Medium para crítico)/Opus Medium. Dois fracassos documentados orientam escalada;
consulte a POLICY para gatilhos, entregáveis, exceções e retorno a Builder.

Arquivos não provam o modelo da sessão, acesso ou inferência. `check` retorna 2
quando os arquivos correspondem mas não existe observação; 1 para divergência;
0 somente quando a observação fresca também corresponde. Confirme `/status`/seletor
Codex ou `/model` Claude na nova sessão. Observação por arquivo usa o contrato
completo da POLICY; não invente a observação.

Overrides e launchers do projeto importado podem prevalecer. O instalador não os
reescreve. Leia as regras locais e reconcilie-os sob ticket/contrato/worktree próprios,
com backup e preservação das demais chaves. Contratos/sessões antigos e escolhas
humanas explícitas prevalecem. Bootstrap mantém seu próprio runtime desejado;
essa instalação não modifica ProductManifest, Hermes ou operating mode.

## Lançamentos e atualização

Quando a pessoa avisar que saiu um modelo:

```sh
pipe model-policy --json release --runtime codex --model gpt-NOVA-VERSAO --notice 'Aviso humano nesta tarefa'
```

Cria avaliação deduplicada, relatório e PROPOSAL.diff locais. Não pesquisa, monitora,
adota ou inicia novos agentes automaticamente. Verifique fontes oficiais e acesso,
reavalie arquitetura operacional/regras/políticas, compare tarefas representativas,
entregue proposta e aguarde aprovação antes de mudar a matriz. Impacto no produto é
somente proposta. Sem cron, polling ou checagem automática de lançamentos.

Em atualização de pacote, se o payload instalado for diferente, faça plano e
aplique só após aprovação real, usando `--replace-version --approval-reference`.
Drift local e symlinks bloqueiam até reconciliação; flags não autorizam sobrescrita
de drift. Repetição sem mudança não escreve. Permissões do Codex/Claude e regras
fora dos blocos gerenciados são preservadas. Não há comando de rollback automático:
compare hashes atuais com o receipt e restaure somente os arquivos desta instalação
usando seus backups, preservando mudanças posteriores. Não copie backups entre máquinas.

## Limites da entrega

Testes isolados simulam home nova e pacote instalado em caminho com espaços. Não
substituem aceite no computador destino nem comprovam acesso aos modelos nessa
conta. Esta entrega é local: publicação/merge precisam de autorização e revisão.
