# Plano Manual De Descoberta Para Revisao Bibliografica De TCC

## Metadados

- Data: 2026-06-02
- Ticket de origem: PIP-336
- Evidencia de origem: `validation/test-runs/conversational-pipeline-live-mood-test-2026-06-02-tcc-quimica.md`
- Rota de recursos: `capability.external.pm-skills` mais artefatos de validacao da Pipe
- PM Skills usadas: `interview-script`, `summarize-interview`, `identify-assumptions-new`, `prioritize-assumptions`, `brainstorm-experiments-new`
- Status: plano de descoberta, nao resultado de validacao com clientes
- Decisao de etapa: NAO APLICAVEL para este artefato
- Motivo: planejamento interno de entrevistas; este arquivo nao executa contato externo automatizado, busca de leads, mensagem externa, ligacao automatizada, construcao de produto, cobranca ou publicacao de fontes

## Como Usar Este Plano

Este arquivo e um roteiro operacional para voce executar a proxima etapa da Pipe sem precisar procurar outro documento.

1. Encontre 5 estudantes parecidas com a persona descrita neste plano.
2. Convide manualmente essas pessoas para conversas de 30 a 40 minutos.
3. Use o roteiro de entrevista deste arquivo sem vender a solucao.
4. Depois de cada conversa, preencha uma copia do modelo `Nota De Entrevista De Descoberta TCC`.
5. Depois das 5 conversas, preencha o modelo `Sintese Do Lote De Descoberta TCC`.
6. Entregue a sintese para a Pipe decidir a proxima etapa: `GO`, `GO CONDICIONAL`, `REFINAR`, `NO-GO` ou `BLOQUEADO`.
7. Nao avance para PRD, MVP, busca academica automatizada ou automacao de leads antes dessa decisao.

O resultado esperado desta etapa nao e uma tela, uma funcionalidade ou um PRD. O resultado esperado e evidencia suficiente para decidir se vale continuar explorando esse recorte.

## Proposito

Este plano prepara cinco entrevistas manuais de descoberta para o recorte de revisao bibliografica de TCC:

```txt
Ajudar estudantes de graduacao a transformar temas de TCC definidos pelo orientador em um rascunho de revisao bibliografica com evidencias e citacoes auditaveis.
```

O objetivo nao e vender a solucao. O objetivo e aprender se o problema e urgente, repetido, acessivel, confiavel e potencialmente pagavel antes de PRD, arquitetura ou implementacao.

## Hipotese Atual

### Hipotese De ICP

Estudantes de graduacao em Quimica, ou cursos STEM proximos, escrevendo um TCC teorico ou bibliografico com:

- tema ou lista de topicos ja definidos pelo orientador
- pressao de prazo em semanas ou poucos meses
- dificuldade para iniciar ou avancar na revisao bibliografica
- uso atual de busca improvisada, ChatGPT, SciELO, referencias do orientador, colegas, mentores ou ajuda paga

### Hipotese De Problema

A dor principal nao e apenas encontrar referencias. A estudante precisa sair de uma lista de topicos para uma revisao escrita crivel, com rastreabilidade suficiente para confiar no texto e evitar citacoes fracas, inventadas, irrelevantes ou mal sustentadas.

### Hipotese Da Primeira Entrega Pagavel

A primeira entrega pagavel e:

```txt
Texto com citacoes auditaveis para cada secao.
```

Hipotese de preco estimada pelo fundador a partir do PIP-334: R$ 100-300.

Isso nao e evidencia validada de preco.

## Decisoes Que Esta Rodada Deve Informar

- Se este recorte merece um PRD.
- Se "texto com citacoes auditaveis" e mais valioso do que apenas busca, organizacao, ABNT, metodologia ou planejamento.
- Se o primeiro ICP deve ser estudantes de Quimica, estudantes STEM de forma mais ampla ou outro segmento.
- Se a promessa do produto pode ser posicionada com seguranca como apoio, e nao como escrita integral por terceiros.
- Se rastreabilidade de citacoes e um fator real de confianca.
- Se estudantes demonstram disposicao a pagar, nao apenas interesse.
- Se qualidade das fontes academicas e um bloqueio antes de escopo de produto.

## Suposicoes A Testar

| Suposicao | Por que importa | Evidencia necessaria | Risco se for falsa |
|---|---|---|---|
| Estudantes com tema definido pelo orientador ainda travam antes ou durante a revisao bibliografica. | Confirma que o recorte comeca depois da definicao do tema. | Historia recente de trava, atraso, alternativa falha ou ansiedade. | O produto pode resolver um fluxo pouco urgente. |
| Busca e escrita sao as dores de maior valor. | Define o foco do MVP. | Priorizacao contra ABNT, metodologia, organizacao, leitura e feedback do orientador. | O MVP pode investir em escrita quando usuarias precisam mais de planejamento ou formatacao. |
| Rastreabilidade de evidencia por citacao aumenta materialmente a confianca. | Diferencia a solucao de escrita generica com IA. | A estudante explica por que fonte clicavel, trecho usado e sinal de qualidade mudariam sua confianca. | O produto vira "mais um ChatGPT" com pouca defensibilidade. |
| Estudantes perto do prazo tem disposicao a pagar. | Testa viabilidade B2C. | Gasto real, gasto considerado, alternativa paga ou reacao crivel a preco. | A faixa de preco do fundador continua sendo desejo, nao evidencia. |
| Estudantes aceitam rascunho assistido se a proposta for etica. | Reduz risco de integridade academica. | Limites esperados: revisao propria, aprovacao do orientador, citacoes, sem escrita integral por terceiros. | O produto pode atrair uso inseguro ou rejeicao institucional. |
| Cinco respondentes acessiveis geram sinal util rapidamente. | Mantem a validacao manual e liderada pelo fundador. | Fundador completa cinco entrevistas com profundidade suficiente. | Pode ser necessario outro canal ou outra fonte de respondentes. |

## Perfis De Respondentes

### Respondentes P1

Entreviste estes perfis primeiro.

| Perfil | Por que essa pessoa | Evidencia esperada | Ideias de fonte manual | Criterios de exclusao | Prioridade |
|---|---|---|---|---|---|
| Estudante de graduacao em Quimica escrevendo TCC teorico ou bibliografico | Mais proxima do recorte original e do tema real | Fluxo atual, trava, urgencia, confianca em fonte, dor de escrita, disposicao a pagar | Rede do fundador, grupos de turma, colegas de curso, indicacoes proximas ao orientador | TCC experimental sem gargalo de revisao bibliografica; sem pressao de prazo; terminou ha muito tempo e lembra pouco | P1 |
| Estudante de Quimica perto do prazo e ainda sem comecar ou travada na revisao | Maior intensidade de dor | Momento de gatilho, ansiedade, alternativa paga, o que destravaria o progresso | Indicacoes quentes, grupos de estudantes, colegas da primeira entrevistada | Estudante que so quer ajuda para escolher tema ou executar laboratorio | P1 |
| Estudante que pagou, considerou pagar ou conhece colegas que pagaram ajuda para TCC | Melhor proxy de disposicao a pagar | Categoria de gasto, ancora de preco, percepcao de risco, o que comprou no lugar | Indicacoes das primeiras respondentes, colegas de turma | Apenas ouviu historias vagas sem comportamento especifico | P1 |

### Respondentes P2

Use estes perfis apenas se o acesso a P1 for insuficiente.

| Perfil | Por que essa pessoa | Evidencia esperada | Ideias de fonte manual | Criterios de exclusao | Prioridade |
|---|---|---|---|---|---|
| Estudante STEM de Farmacia, Materiais, Biologia, Engenharia ou area relacionada com TCC bibliografico | Testa se o recorte expande alem de Quimica | Similaridade da dor de busca, escrita e citacao | Rede do fundador, grupos de cursos adjacentes | Formato de TCC muito diferente ou nao bibliografico | P2 |
| Pessoa recem-formada em Quimica que terminou TCC nos ultimos 6-12 meses | Detalhe retrospectivo de fluxo e armadilhas | O que gostaria que existisse, alternativa real, aceitacao do orientador | Ex-alunos ou rede de amigos | Terminou ha tempo demais para lembrar com detalhe | P2 |

### Nao Entrevistar Nesta Rodada

- Professores ou orientadores como respondentes principais.
- Escritores academicos profissionais ou agencias.
- Estudantes buscando apenas escrita integral por terceiros.
- Pessoas fora do contexto de TCC de graduacao.
- Pessoas sem fluxo atual ou recente de TCC.

Orientadores podem ser uteis depois para revisao de risco e aceitacao, mas esta rodada deve aprender com a primeira hipotese de compradora/usuaria: estudantes.

## Orientacao De Convite Manual

Este plano nao autoriza contato externo automatizado.

O fundador pode pedir conversas manualmente por caminhos quentes, depois de decidir com quem falar. Mantenha a mensagem simples e transparente:

```txt
Estou conversando com estudantes que estao fazendo TCC para entender onde a revisao bibliografica trava. Nao quero vender nada nessa conversa; e so para aprender com sua experiencia. Voce toparia conversar por 25-35 minutos?
```

Evite:

- vender a solucao antes da entrevista
- dizer "eu tenho uma ferramenta que resolve isso"
- perguntar "voce usaria?"
- prometer confidencialidade, preco, entrega, aprovacao ou correcao academica alem do que e verdadeiro
- mensagens automatizadas, raspagem de dados, listas de leads, ligacoes com IA ou contato externo em massa

## Estrutura Da Entrevista

Duracao recomendada: 30-40 minutos.

### Abertura

Use este roteiro:

```txt
Obrigado por conversar comigo. Eu estou entendendo como estudantes passam pela revisao bibliografica do TCC. Nao e uma venda e nao existe resposta certa. Quero entender sua experiencia real: o que aconteceu, o que voce tentou, onde travou e o que teria ajudado. Se alguma pergunta nao fizer sentido, pode falar.
```

Se for gravar:

```txt
Voce autoriza que eu grave so para eu nao perder detalhes da conversa? A gravacao nao sera publicada. Se preferir, eu faco apenas anotacoes.
```

Para armazenamento no repositorio da Pipe, mantenha apenas sintese, a menos que um ticket especifico aprove retencao de transcricao bruta.

### Aquecimento

1. Qual curso voce faz e em que etapa do TCC voce esta?
2. Seu TCC e mais experimental, teorico, bibliografico ou misto?
3. O tema ja veio definido pelo orientador ou voce precisou definir?
4. Quais topicos ou partes da revisao o orientador espera que voce cubra?
5. Quanto tempo falta para entrega ou para a proxima cobranca importante?

### Fluxo Atual E Comportamento Passado

Pergunte sobre a ultima tentativa real, nao sobre opinioes.

1. Me conta a ultima vez que voce tentou avancar na revisao bibliografica. O que voce fez primeiro?
2. Onde exatamente travou ou ficou mais lento?
3. Quais ferramentas, bases, sites, pessoas ou materiais voce usou?
4. Voce usou ChatGPT, SciELO, Google Scholar, artigos enviados pelo orientador, TCCs anteriores ou outra fonte?
5. Quanto tempo voce gastou tentando avancar?
6. O que saiu dessa tentativa: lista de artigos, fichamento, texto escrito, topicos, nada, outra coisa?
7. O que voce fez quando percebeu que nao estava avancando?

### Priorizacao Das Dores

Peca para a respondente priorizar e depois aprofunde nas duas principais.

```txt
Se voce tivesse que escolher os dois maiores problemas da revisao bibliografica, quais seriam?
```

Opcoes para mencionar apenas se necessario:

- saber por onde comecar
- achar referencias confiaveis
- ler e entender os artigos
- organizar ideias e topicos
- escrever o texto
- conectar citacoes com afirmacoes
- ABNT/formatacao
- metodologia
- medo de citacao errada ou fonte fraca
- lidar com orientador
- falta de tempo

Perguntas de aprofundamento:

1. Por que esses dois sao os mais dificeis?
2. O que acontece se eles nao forem resolvidos?
3. Qual deles voce pagaria para resolver primeiro?
4. Qual deles voce acha chato, mas nao pagaria para resolver?

### Confianca E Evidencia Das Citacoes

Nao apresente a solucao cedo demais. Use esta hipotese depois de entender o fluxo atual.

```txt
Imagina que voce recebesse um rascunho de revisao bibliografica em que cada afirmacao importante tivesse uma citacao clicavel, o trecho de evidencia usado e um alerta sobre a qualidade da fonte. O que voce iria checar antes de confiar?
```

Perguntas de aprofundamento:

1. O que faria voce desconfiar desse texto?
2. Que tipo de fonte voce considera aceitavel para TCC?
3. O que voce espera que o orientador aceite ou rejeite?
4. Voce preferiria receber so as referencias organizadas, um rascunho escrito, ou rascunho com citacoes auditaveis?
5. O que seria perigoso ou antietico nesse tipo de ferramenta?
6. O que teria que ficar sob sua responsabilidade como estudante?

### Disposicao A Pagar E Gasto Existente

Pergunte sobre comportamento passado antes de hipotese de preco.

1. Voce ja pagou, pensou em pagar, ou conhece alguem que pagou ajuda para TCC?
2. O que exatamente foi contratado: orientacao, revisao, formatacao, busca, escrita, execucao completa?
3. Voce lembra a faixa de preco ou como a pessoa decidiu que valia pagar?
4. O que faria voce considerar pagar por ajuda na revisao bibliografica?
5. Se algo economizasse uma ou duas semanas e entregasse um rascunho auditavel, qual faixa pareceria aceitavel?
6. Em que ponto do prazo voce pagaria: agora, perto da entrega, depois de travar, ou nunca?

Nao trate disposicao declarada como prova. Prefira gasto real, gasto considerado ou troca concreta.

### Integridade Academica E Seguranca

1. Onde fica a linha entre ajuda aceitavel e alguem fazer o TCC por voce?
2. O que voce precisaria revisar pessoalmente antes de entregar?
3. Voce contaria para o orientador que usou uma ferramenta de apoio? Por que?
4. Que aviso ou controle deixaria a ferramenta mais segura?
5. O que a ferramenta jamais deveria prometer?

### Encerramento

1. O que eu nao perguntei e deveria ter perguntado?
2. Quem mais vive esse problema e poderia conversar comigo?
3. Voce toparia ver um exemplo manual depois, se ele existisse?
4. Posso te procurar para tirar uma duvida rapida depois?

## Modelo De Nota De Entrevista

Use uma copia por respondente. Nao armazene nomes, telefones, e-mails, perfis sociais ou detalhes privados brutos em artefatos do repositorio, a menos que um ticket futuro aprove explicitamente essa retencao.

```md
# Nota De Entrevista De Descoberta TCC

## Metadados

- Rotulo da respondente: P01 / P02 / P03 / P04 / P05
- Data:
- Entrevistador:
- Curso:
- Tipo de TCC: teorico / bibliografico / experimental / misto
- Etapa do TCC:
- Pressao de prazo: baixa / media / alta
- Existe gravacao fora do repositorio: sim/nao
- Existe transcricao fora do repositorio: sim/nao
- Apenas sintese segura para repositorio: sim/nao

## Contexto

- Tema ja definido pelo orientador: sim/nao/parcial
- Topicos exigidos:
- Etapa atual na revisao bibliografica:
- Momento de gatilho:

## Fluxo Atual

- Ultima tentativa de trabalhar na revisao:
- Ferramentas/fontes usadas:
- Entrega produzida:
- Onde travou:
- Tempo gasto:

## Priorizacao Das Dores

- Dor principal 1:
- Dor principal 2:
- Outras dores:
- Intensidade da dor: baixa / media / alta
- Tipo de evidencia: comportamento / fala / gasto / alternativa / suposicao

## Alternativa Atual E Gasto

- Alternativa atual:
- Ajuda paga usada ou considerada:
- Comportamento conhecido de colegas:
- Ancora de preco:
- Sinal de compromisso:

## Confianca E Evidencia Das Citacoes

- Rastreabilidade de citacao ajudaria? sim/nao/misto
- O que ela checaria:
- Expectativas de qualidade das fontes:
- Bloqueios de confianca:
- Preocupacao de aceitacao pelo orientador:

## Integridade Academica

- Ajuda aceitavel:
- Limite inaceitavel / escrita integral por terceiros:
- Responsabilidade da estudante:
- Avisos ou controles necessarios:

## Preferencia Da Primeira Entrega

- Apenas referencias:
- Estrutura + referencias:
- Texto rascunhado:
- Texto rascunhado + citacoes auditaveis:
- Outro:

## Falas Ou Linguagem Exata

Armazene apenas falas anonimizadas e seguras para o repositorio.

- Fala 1:
- Fala 2:

## Contradicoes

- Evidencia que apoia a tese:
- Evidencia que enfraquece a tese:
- Sinal ambiguo:
- Novo risco:

## Sintese Do Entrevistador

- Sinal mais forte:
- Sinal mais fraco:
- Mudanca de confianca: aumentou / igual / diminuiu
- Decisao recomendada: GO / GO CONDICIONAL / REFINAR / NO-GO / BLOQUEADO
- Continuidade necessaria:
```

## Modelo De Sintese Do Lote

Use este modelo depois das cinco entrevistas. Este e o formato que o fundador pode trazer de volta para a Pipe depois de concluir as conversas.

```md
# Sintese Do Lote De Descoberta TCC

## Metadados

- Ticket de origem: PIP-336
- Lote de evidencia: 5 entrevistas manuais
- Dados brutos tratados no repositorio: nao por padrao
- Artefato do repositorio contem: sintese anonimizada

## Cobertura Das Fontes

| Rotulo da fonte | Curso | Tipo de TCC | Pressao de prazo | Qualidade da evidencia |
|---|---|---|---|---|
| P01 |  |  | Baixa / Media / Alta | Baixa / Media / Alta |
| P02 |  |  | Baixa / Media / Alta | Baixa / Media / Alta |
| P03 |  |  | Baixa / Media / Alta | Baixa / Media / Alta |
| P04 |  |  | Baixa / Media / Alta | Baixa / Media / Alta |
| P05 |  |  | Baixa / Media / Alta | Baixa / Media / Alta |

## Padroes Encontrados

- Dor repetida:
- Momento de gatilho:
- Alternativa atual:
- Alternativa paga:
- Requisito de confianca:
- Preocupacao de integridade academica:
- Preferencia da primeira entrega:
- Sinal de preco:

## Tabela De Evidencias

| Evidencia | Tipo | Fontes | Confianca | Observacoes |
|---|---|---|---|---|
|  | comportamento / fala / gasto / alternativa / objecao / compromisso | P01, P02... | Baixa / Media / Alta |  |

## Revisao De Contradicoes

- Evidencias que apoiam a tese atual:
- Evidencias que contradizem a tese atual:
- Sinais ambiguos ou mistos:
- Evidencia que enfraquece especificidade do ICP:
- Evidencia que enfraquece intensidade da dor:
- Evidencia que enfraquece disposicao a pagar:
- Novo risco ou objecao:

## Decisao

- Impacto da decisao: GO / GO CONDICIONAL / REFINAR / NO-GO / BLOQUEADO
- Motivo:
- Proxima etapa permitida:
- Etapas bloqueadas:
- Tickets de continuidade necessarios:
```

## Criterios De GO

Use estes criterios como ponto de decisao direcional antes de PRD. Nao force uma conclusao positiva.

- Pelo menos 4 de 5 respondentes se encaixam no perfil-alvo ou em perfil adjacente claramente aderente.
- Pelo menos 3 de 5 descrevem uma dificuldade concreta e recente para iniciar ou avancar na revisao bibliografica.
- Pelo menos 3 de 5 colocam busca + escrita, evidencia de citacao ou confianca em fontes entre as duas maiores dores.
- Pelo menos 3 de 5 dizem que rastreabilidade de citacao aumentaria materialmente a confianca.
- Pelo menos 2 de 5 pagaram, consideraram pagar ou conhecem exemplo concreto de colega que pagou ajuda para TCC.
- Pelo menos 2 de 5 reagem de forma crivel a uma faixa proxima de R$ 100-300 para apoio urgente perto do prazo.
- Nenhuma objecao dominante de integridade academica torna a primeira promessa insegura como fluxo assistido.

## Criterios De GO Condicional

Use estes criterios quando ha sinal suficiente para continuar aprendendo, mas nao suficiente para criar escopo de produto.

- A dor e forte, mas a disposicao a pagar e incerta.
- Estudantes querem busca e organizacao, mas nao texto gerado.
- Rastreabilidade de citacoes so gera confianca com controles rigidos de revisao.
- Quimica parece estreito demais, mas estudantes STEM adjacentes mostram sinal mais forte.
- Estudantes querem o resultado, mas aceitacao do orientador e bloqueio.

Acao permitida depois de GO CONDICIONAL:

- refinar ICP
- rodar um segundo lote de entrevistas
- executar uma amostra manual assistida com um tema aprovado e nao sensivel
- criar um spike de pesquisa sobre cobertura de fontes academicas somente depois que a evidencia de validacao sustentar isso

## Criterios De NO-GO Ou Pivot

- Menos de 2 de 5 relatam uma dor concreta e recente.
- A maioria diz que ChatGPT/SciELO generico e suficiente.
- A dor principal e apenas formatacao ABNT, nao busca/escrita/evidencia.
- Estudantes querem escrita integral por terceiros como valor principal.
- Estudantes nao pagariam e nao tem custo relevante de alternativa atual.
- Risco de aceitacao por orientador/instituicao domina o valor.
- O primeiro ICP nao e alcancavel manualmente.

## Acoes Bloqueadas

Estas acoes continuam bloqueadas depois deste plano:

- PRD como escopo de produto aceito
- construcao de MVP
- integracao de busca academica
- busca automatizada de leads
- contato externo automatizado
- ligacoes com IA
- cobranca ou coleta de pagamento
- alegacoes publicas de validacao
- armazenamento de gravacoes brutas ou transcricoes identificaveis no repositorio

## Proxima Acao Permitida

Rode cinco conversas manuais de descoberta e volte para a Pipe com uma destas entradas:

- modelos de nota preenchidos, sanitizados o suficiente para sintese no repositorio, ou
- uma sintese de lote usando o modelo acima, ou
- um bloqueio explicando por que cinco entrevistas nao puderam ser concluidas.

## Repasse De Recursos

Agentes futuros que processarem esta rodada devem usar:

- `capability.external.pm-skills` para padroes de sintese de entrevistas
- `validation/raw-interview-evidence-intake-and-synthesis.md` para limites de evidencia
- `validation/market-validation-before-code-gate.md` antes de PRD ou construcao
- `capability.external.linear-mcp` para status e rastreamento de tickets de continuidade

Nao use:

- `capability.external.consensus` ate que a rodada de validacao justifique pesquisa academica
- `capability.external.notebooklm` a menos que exista um conjunto de fontes aprovado
- `capability.external.notion-mcp` a menos que o ticket peca explicitamente para registrar o artefato final aprovado no Notion
- `capability.future.openclaw-paperclip` para qualquer execucao atual
