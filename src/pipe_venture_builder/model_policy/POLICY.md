# Política global de modelos e entregáveis

Versão 2026-10-04.1. Decisões humanas nesta conversa em 2026-10-04:
Codex e Claude, troca automática anunciada dentro do mesmo runtime, verificação,
migração de novos trabalhos e reavaliação de lançamentos somente por aviso humano.
A matriz executável é [matrix.json](matrix.json).

## Seleção por papel

| Papel | Gatilho | Codex | Claude | Entregável |
| --- | --- | --- | --- | --- |
| Worker | Busca delimitada, rename e edição mecânica com regra clara e baixo risco | Luna Low | Haiku, esforço nativo | Resultado, arquivos afetados, verificação |
| Builder, padrão | Requisitos claros, planejamento normal, implementação, testes e refactor moderado | Sol 6.1 Medium | Sonnet Medium | Plano quando necessário; diff, checks e pendências |
| Architect | Decisão arquitetural relevante, ambiguidade impeditiva ou duas hipóteses distintas fracassadas | Astra Medium | Opus Medium | Plano ou diagnóstico com evidências, decisões, riscos e critérios |
| Reviewer | Revisão solicitada ou mudança crítica em segurança, dados, contrato público ou arquitetura | Astra Low; Medium para crítica | Opus Medium | Problemas, prioridade, localização, evidência e impacto |

Ao iniciar trabalho, classifique o papel e confira modelo/esforço efetivos. Prefira
comandos determinísticos para busca/validação quando bastarem. Worker sobe para
Builder se surgir decisão semântica ou risco adicional. Duas hipóteses de Builder
fracassadas devem ter evidências distintas; repetir um comando não conta.
Architect retorna a Builder quando a decisão estiver resolvida. High somente após
duas abordagens insuficientes documentadas de Architect; bloqueio persistente gera
diagnóstico e dependência, sem escalada ilimitada. Revisão crítica usa Medium.
Mudança crítica precisa de uma etapa de revisão; autorrevisão é identificada e não
substitui o colega. Tarefa simples não precisa dos quatro papéis.

Escolha explícita do usuário para a tarefa prevalece. Sessões e contratos em
execução são preservados; os padrões passam a valer em novos trabalhos. As
exceções por tarefa devem ter referência à instrução humana. OpenWiki usa
sequencialmente o modelo da sessão: não trocar no meio de uma geração.

## Troca e passagem

Anuncie: papel anterior → próximo papel, gatilho observado, modelo/esforço e
próximo entregável. Use o mecanismo suportado pelo runtime. Quando a ferramenta
não expuser troca programática da sessão, prepare passagem e peça a troca no
seletor. Não abra agentes/tarefas adicionais por conta disso. Configuração salva,
argumentos de lançamento e texto anunciado não comprovam a troca efetiva.

Registre nos artefatos existentes da tarefa: objetivo/autorização, papel, gatilho,
modelo/esforço observados (ou não verificado), hipóteses e evidências, critérios,
checks e próximo passo. Plano inclui estado atual, decisões, componentes afetados,
passos, dependências, riscos, testes, aceite e exclusões. Passagem usa plano,
fontes relevantes, diff e checks necessários, evitando o histórico inteiro.

Modelos indisponíveis geram impedimento explícito. Não trocar provedor nem ativar
fallback silencioso. Escolha de modelo não autoriza delegação, nova tarefa,
publicação ou mudança de permissões. Percentuais e preços não são cotas ou prova
de economia na assinatura.

## Novo lançamento: gatilho manual de reavaliação

Quando o usuário disser que foi liberado um modelo ou pedir revisão por lançamento:

1. Registre o aviso por runtime e identificador/versão. Execute `agent-model release`
   para criar a avaliação; não há cron, polling ou checagem de lançamento no início.
2. Verifique fontes oficiais, versão, capacidades, esforço suportado, disponibilidade
   no runtime e limitações. Anúncio público e acesso na conta são fatos distintos.
3. Reavalie papéis, modelos, esforço, roteamento, arquitetura do fluxo dos agentes,
   contexto, entregáveis, revisão, regras e políticas. Impactos nos produtos são
   propostas por projeto, sem iniciar mudanças nos aplicativos.
4. Compare tarefas representativas dos papéis afetados. Registre observações e
   lacunas; testes com cobrança adicional dependem de autorização específica.
5. Preencha o relatório e o diff proposto. Inclua manter o estado atual como opção,
   benefícios, riscos, critérios de adoção e reversão. A recomendação pode ser não adotar.
6. Aguarde aprovação explícita do usuário. Só então implemente a proposta sob o
   contrato/ticket aplicável, incremente a versão e reinstale a política. Preserve
   sessões/contratos em execução e revalide novos trabalhos.

O registro deduplica runtime/versão. `--reopen MOTIVO` abre nova avaliação por nova
evidência ou pedido humano e preserva a anterior. O helper prepara avaliação e
proposta, não realiza pesquisa por modelo nem aprova ou adota lançamentos.

## Uso local

Requer Python 3.11+; a instalação fixa o intérprete usado no wrapper.

```sh
pipe model-policy install --plan
pipe model-policy install --apply
agent-model select --runtime codex --task feature
agent-model select --runtime claude --task bug --failed-hypotheses 2
agent-model select --runtime codex --task architecture --resolved
agent-model inspect --runtime codex --project /caminho/projeto
agent-model check --runtime codex --project /caminho/projeto
agent-model check --runtime codex --observed /caminho/observacao.json
agent-model launch --runtime claude --role builder --project /caminho/projeto
agent-model release --runtime codex --model NOVA_VERSAO --notice 'Aviso do usuário nesta tarefa'
```

`select` aceita tarefa, papel, criticidade, ambiguidade, hipóteses fracassadas e
resolução. `--explicit-model` exige `--authorization`; `--explicit-effort` é opcional.
Seleção fora do provedor é recusada. `launch` é uma nova sessão interativa para o
próprio usuário; não muda uma sessão aberta e não envia prompt nem cria worktree.
Sempre use worktree/contrato próprios quando o projeto exigir.

`inspect` lê apenas campos de seleção dos arquivos conhecidos, sem imprimir
permissões, secrets ou configuração completa. Arquivos inválidos geram erro.
Não executa launchers nem interpreta código de projeto. Flags, ambiente, perfis,
política gerenciada e seleção conservada no aplicativo podem prevalecer: nesses
casos a configuração efetiva fica parcialmente verificada.

`check` compara recomendação, configuração resolvida dos arquivos e observação
fornecida pelo runtime. Sem observação, nunca declara conformidade da sessão.
Observação JSON: `runtime`, `model`, `effort`, `source`, `observed_at` (UTC ISO),
`session_id` e `project` absoluto; limite de frescor de 24 horas. É evidência
informada pelo operador, não atestação criptográfica. Sessão atual deve ser conferida
por `/status`/seletor no Codex e `/model` no Claude. Aliases Claude são comparados à
família; o identificador real observado fica registrado.

## Instalação e distribuição

Fonte canônica no pacote Pipe (`pipe_venture_builder/model_policy/`); cópia instalada em `~/.agents/model-policy/`.
`pipe model-policy install` e `agent-model install` exibem plano por padrão; somente `--apply` escreve.
Clone ou wheel transportam a política, nunca receipts, backups, autenticação ou estado deste Mac.
Instalação global automática: macOS/Linux; Windows possui seleção/inspeção e configuração manual.
Destinos customizados via CODEX_HOME/CLAUDE_CONFIG_DIR bloqueiam instalação padrão até reconciliação.
Instalação acrescenta blocos delimitados às instruções globais e ajusta somente
as chaves de modelo/esforço globais. Preserva configurações restantes e grava
backups privados e hashes em receipt local. `--dry-run` não escreve.

Arquivos centrais de versão diferente não são sobrescritos automaticamente: uma
atualização usa `--replace-version --approval-reference REFERENCIA` após a aprovação
real. A string registra sua origem e não substitui aprovação humana. Se arquivos
instalados tiverem drift em relação ao receipt, a instalação recusa atualização.
Sem efeito em sessões existentes; reinicie a sessão para carregar as instruções.

[Onboarding e auditoria de projetos](ONBOARDING.md) explicam a
cobertura. Herança global não certifica overrides locais nem a sessão. Instalação
em outro computador exige pedido próprio, sem copiar autenticação.

Fontes sobre controles e precedência: [Codex](https://learn.chatgpt.com/docs/developer-settings),
[Claude modelos](https://code.claude.com/docs/en/model-config) e
[Claude instruções](https://code.claude.com/docs/en/memory).
