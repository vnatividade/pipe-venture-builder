# Onboarding da política de modelos

Ao adequar um projeto com `repo-padrao`, consulte a política central instalada em
`~/.agents/model-policy/POLICY.md` e execute `agent-model inspect` e `check` para
Codex e Claude. Escolhas explícitas da tarefa prevalecem; preserve execuções antigas.
Em outra máquina use a fonte versionada, sem copiar sessões ou credenciais.

Inventarie projetos registrados em Codex e Orca e consolide clones/worktrees pela
identidade Git. Diretórios de scratch, raiz `/` e projetos ChatGPT sem executor
local não recebem alterações de repositório. A instrução global cobre novas sessões
locais; overrides e pontos de entrada precisam de conferência própria.

Registre uma matriz por projeto com seleção recomendada/configurada/observada,
referência das instruções, divergências, impedimentos e evidências. Não conte a
mesma worktree como projeto independente nem leia `.env` ou secrets no inventário.

Para migrar um override do projeto, leia suas instruções e ticket do projeto certo,
prepare o ajuste em worktree própria e valide preservação das demais chaves. Não
use IDs Linear da venture de origem em outra venture. Se acesso/mapeamento/contrato faltar,
registre impedimento; não sobrescreva o checkout em andamento nem declare conformidade.

Para projetos futuros, a política global define os padrões. Acrescente referência
portável à política na governança local quando autorizado e verifique seleção real
na primeira sessão. Não copie toda a infraestrutura ou regras de produto de outra venture.
