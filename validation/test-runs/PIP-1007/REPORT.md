# PIP-1007 — entrega local de política portátil de modelos

Pedido humano: levar a lógica construída nesta conversa ao Pipe Venture Builder
para importar o projeto em outra máquina e configurar a mesma lógica no ambiente destino.
Responsável Vitor; executor Codex atual, modelo/esforço observados não verificados;
revisor esperado outro desenvolvedor, pendente. Risco medium; execução serial.
Ticket https://linear.app/pipe-venture-builder/issue/PIP-1007/portar-politica-de-modelos-codexclaude-para-instalacao-do-pipe-em
Branch codex/pip-1007-model-policy; base origin/main em 1e7a67bf2d892e861a051d7ae19198e487ae5606.

## Entrega e fonte canônica

Pacote pipe_venture_builder.model_policy contém matriz, engine, POLICY e ONBOARDING.
CLI pipe model-policy oferece select, inspect, check, launch, install, release.
Instalação por plano (padrão), --apply explícito, backups privados e receipt gerados
no destino. Matriz 2026-10-04.1 preservada sem mudança de modelos/gatilhos/entregáveis.
Proteção de symlinks ancestrais, limites de plataforma, UTF-8 e homes customizadas
bloqueadas evitam portabilidade presumida. Guia docs/install/model-policy.md.

AGENTS comum aponta à política; CLAUDE já adapta AGENTS, sem política concorrente.
ProductManifest/operating mode/bootstrap, Hermes e contratos ativos preservados.
Artefatos locais exportados: wheel, patch revisável, guia, smoke e hashes. Nenhum
estado de configuração do Mac, autenticação, secrets, receipts ou inventário exportado.
Configuração global atual deste Mac foi preservada; instalação feita em fixtures isoladas.
O checkout principal do Pipe tinha alterações preexistentes e não foi sobrescrito.

## Evidências

- Suíte Python: 935 testes e 1433 subtests passaram em 118.58s, Python 3.14.
- Após simplificar a resolução de recursos empacotados, os 29 testes focados passaram
  novamente e o wheel final foi reconstruído e validado isoladamente.
- Runtime Node: 59 testes passaram.
- Matriz de governança gerada: em sincronia; git diff --check passou.
- Wheel final instalado em venv nova, caminho com espaços, cwd fora do checkout,
  sem PYTHONPATH e home ausente. Plano zero escrita, aplicação Sol6.1 Medium /
  Sonnet Medium, repetição zero escrita. Wrapper instalado independente do toolkit.
- Check retornou 2 (sem observação), com arquivos correspondentes. Não certifica runtime.
- Wheel contém todos os recursos; nenhum arquivo .py/.json/.md contém caminho fixo
  /Users/agents. Nenhum receipt/registro de lançamentos está no wheel.
- package-smoke.json registra hash do wheel final. Não houve inferência ou custo de modelos.

## Revisão e pendências

Autorrevisão apenas: preservação de permissões/gates, defaults, erro sanitizado,
conflitos, pacote e exportação verificados; nenhum P0/P1 identificado. Sem revisão independente.
Sem commit, push, PR, merge, release ou deploy. Ticket não Done. O pacote exportado
é artefato local desta branch não publicada, ainda usando a versão-base Pipe 0.1.0;
não é uma release oficial. Publicação e revisão pelo colega permanecem pendentes.
macOS arm64 testado por fixtures e instalação isolada; Linux sem aceite nativo;
Windows instalação/release bloqueados explicitamente. Outro computador e acesso
Codex/Claude nessa conta ainda não foram validados. Runtime deve autenticar localmente.

## Validação pelo usuário

Transporte o pacote exportado e siga GUIA.md. Instale em ambiente virtual novo com
python -m pip install /caminho/pipe_venture_builder-0.1.0-py3-none-any.whl.
Depois pipe model-policy install --plan e --apply; inspect nas duas ferramentas.
Verifique na sessão efetiva /status ou /model. Não existe URL de app para esta entrega.
Nenhuma tarefa de produto/Finance OS foi iniciada. Próximo passo recomendado:
revisão independente e, quando solicitado, publicação da branch no Pipe.


## Autorização posterior de publicação — 04/10/2026

Vitor pediu explicitamente que a implementação esteja no codebase remoto do Pipe.
A limitação de publicação acima descreve a entrega local anterior, agora superada
para este escopo. Autorizados commit/push/PR e integração em main pelo caminho de
revisão do Pipe; sem deploy ou alteração de operating mode/gates. Resultados remotos
serão registrados no PR e ticket; este relatório preserva as verificações locais.
