# TCC Bibliographic Review Manual Discovery Plan

## Metadata

- Date: 2026-06-02
- Origin ticket: PIP-336
- Origin evidence: `validation/test-runs/conversational-pipeline-live-mood-test-2026-06-02-tcc-quimica.md`
- Capability route: `capability.external.pm-skills` plus Pipe validation artifacts
- PM Skills used: `interview-script`, `summarize-interview`, `identify-assumptions-new`, `prioritize-assumptions`, `brainstorm-experiments-new`
- Status: discovery plan, not customer validation result
- Gate decision: NOT APPLICABLE for this artifact
- Reason: internal interview planning only; no automated outreach, lead sourcing, external messaging, call automation, product build, billing, or source publication is executed here

## Purpose

This plan prepares five manual discovery interviews for the TCC bibliographic-review wedge:

```txt
Help undergraduate students turn advisor-defined TCC topics into an evidence-backed bibliographic-review draft with auditable citations.
```

The goal is not to pitch the solution. The goal is to learn whether the problem is urgent, repeated, reachable, trusted, and worth paying for before PRD, architecture, or implementation.

## Current Hypothesis

### ICP Hypothesis

Undergraduate Chemistry students, or adjacent STEM students, writing a theoretical or bibliographic TCC with:

- a theme or topic list already defined by the advisor
- deadline pressure within weeks or a few months
- difficulty starting or progressing the bibliographic review
- current reliance on improvised search, ChatGPT, SciELO, advisor references, peers, mentors, or paid help

### Problem Hypothesis

The painful job is not only finding references. The student needs to move from topic list to a credible written review, with enough evidence traceability to trust the text and avoid weak, hallucinated, irrelevant, or poorly supported citations.

### First Paid Output Hypothesis

The first paid output is:

```txt
Text plus auditable citations for each section.
```

Founder-estimated price hypothesis from PIP-334: R$ 100-300.

This is not validated pricing evidence.

## Decisions This Discovery Round Should Inform

- Whether this wedge deserves a PRD.
- Whether "text plus auditable citations" is more valuable than only search, organization, ABNT, methodology, or planning.
- Whether the first ICP should be Chemistry students specifically, broader STEM students, or a different segment.
- Whether the product promise can be positioned safely as assistance instead of ghostwriting.
- Whether citation traceability is a meaningful trust driver.
- Whether students show willingness to pay, not only interest.
- Whether academic-source quality is a blocker before product scope.

## Assumptions To Test

| Assumption | Why it matters | Evidence needed | Risk if false |
|---|---|---|---|
| Students with advisor-defined topics still get stuck before or during the bibliographic review. | Confirms the wedge starts after theme definition. | Recent story of being stuck, delay, failed workaround, or anxiety. | Product may solve a non-urgent workflow. |
| Search and writing are the highest-value pain points. | Defines MVP focus. | Ranking against ABNT, methodology, organization, reading, advisor feedback. | MVP may overinvest in writing while users need planning or formatting. |
| Citation evidence traceability materially increases trust. | Differentiates from generic AI writing. | Student explains why clickable source, excerpt, and quality signal would change trust. | Product becomes "another ChatGPT" with weak defensibility. |
| Students near deadlines have willingness to pay. | Tests B2C viability. | Actual spend, considered spend, paid workaround, or credible price reaction. | Founder price range remains wishful. |
| Students will accept assisted drafting if framed ethically. | Reduces academic integrity risk. | Boundaries they expect: review, advisor approval, citations, non-ghostwriting. | Product may attract unsafe use or trigger institutional rejection. |
| Five reachable respondents can produce useful signal quickly. | Keeps validation founder-led and manual. | Founder completes five interviews with enough depth. | Need a different channel or respondent source. |

## Respondent Targeting

### P1 Respondents

Interview these first.

| Profile | Why this person | Evidence expected | Manual source ideas | Exclusion criteria | Priority |
|---|---|---|---|---|---|
| Undergraduate Chemistry student currently writing theoretical or bibliographic TCC | Closest to the original wedge and real theme | Current workflow, blocker, urgency, source trust, writing pain, willingness to pay | Founder network, class groups, course peers, advisor-adjacent introductions | Experimental TCC with no literature-review bottleneck; no deadline pressure; already finished long ago with weak recall | P1 |
| Undergraduate Chemistry student near deadline and not yet started or stuck on review | Highest pain intensity | Trigger moment, anxiety, paid workaround, what would unlock progress | Warm introductions, student groups, peers of original interviewee | Student only wants theme selection or lab execution help | P1 |
| Student who paid, considered paying, or knows peers who paid for TCC execution/mentoring | Strongest willingness-to-pay proxy | Spend category, price anchor, risk perception, what they bought instead | Referrals from first respondents, classmates | Only heard vague stories with no specific behavior | P1 |

### P2 Respondents

Use these only if P1 access is insufficient.

| Profile | Why this person | Evidence expected | Manual source ideas | Exclusion criteria | Priority |
|---|---|---|---|---|---|
| STEM undergraduate student in Pharmacy, Materials, Biology, Engineering, or related field with bibliographic TCC | Tests whether wedge expands beyond Chemistry | Similarity of search/writing/citation pain | Founder network, adjacent course groups | TCC format is too different or not bibliographic | P2 |
| Recent Chemistry graduate who finished TCC in the last 6-12 months | Retrospective workflow detail and pitfalls | What they wish existed, actual workaround, advisor acceptance | Alumni or friend network | Finished too long ago to remember specifics | P2 |

### Do Not Interview In This Round

- Professors or advisors as primary respondents.
- Professional academic writers or agencies.
- Students looking only for full ghostwriting.
- Students outside undergraduate TCC context.
- People with no current or recent TCC workflow.

Advisors may be useful later for risk and acceptance review, but this round should learn from the first buyer/user hypothesis: students.

## Manual Outreach Guidance

This plan does not authorize automated outreach.

Founder may manually ask for conversations through warm paths after deciding to contact people. Keep the message simple and transparent:

```txt
Estou conversando com estudantes que estão fazendo TCC para entender onde a revisão bibliográfica trava. Não quero vender nada nessa conversa; é só para aprender com sua experiência. Você toparia conversar por 25-35 minutos?
```

Avoid:

- pitching the solution before the interview
- saying "eu tenho uma ferramenta que resolve isso"
- asking "você usaria?"
- promising confidentiality, pricing, output, approval, or academic correctness beyond what is true
- automated messages, scraping, lead lists, AI calls, or bulk outreach

## Interview Structure

Recommended length: 30-40 minutes.

### Opening

Use this script:

```txt
Obrigado por conversar comigo. Eu estou entendendo como estudantes passam pela revisão bibliográfica do TCC. Não é uma venda e não existe resposta certa. Quero entender sua experiência real: o que aconteceu, o que você tentou, onde travou e o que teria ajudado. Se alguma pergunta não fizer sentido, pode falar.
```

If recording:

```txt
Você autoriza que eu grave só para eu não perder detalhes da conversa? A gravação não será publicada. Se preferir, eu faço apenas anotações.
```

For Pipe repository storage, keep only synthesis unless a specific ticket approves raw transcript retention.

### Warm-Up

1. Qual curso você faz e em que etapa do TCC você está?
2. Seu TCC é mais experimental, teórico, bibliográfico ou misto?
3. O tema já veio definido pelo orientador ou você precisou definir?
4. Quais tópicos ou partes da revisão o orientador espera que você cubra?
5. Quanto tempo falta para entrega ou para a próxima cobrança importante?

### Current Workflow And Past Behavior

Ask about the last real attempt, not opinions.

1. Me conta a última vez que você tentou avançar na revisão bibliográfica. O que você fez primeiro?
2. Onde exatamente travou ou ficou mais lento?
3. Quais ferramentas, bases, sites, pessoas ou materiais você usou?
4. Você usou ChatGPT, SciELO, Google Scholar, artigos enviados pelo orientador, TCCs anteriores ou outra fonte?
5. Quanto tempo você gastou tentando avançar?
6. O que saiu dessa tentativa: lista de artigos, fichamento, texto escrito, tópicos, nada, outra coisa?
7. O que você fez quando percebeu que não estava avançando?

### Pain Ranking

Ask the respondent to rank, then probe the top two.

```txt
Se você tivesse que escolher os dois maiores problemas da revisão bibliográfica, quais seriam?
```

Options to mention only if needed:

- saber por onde começar
- achar referências confiáveis
- ler e entender os artigos
- organizar ideias e tópicos
- escrever o texto
- conectar citações com afirmações
- ABNT/formatação
- metodologia
- medo de citação errada ou fonte fraca
- lidar com orientador
- falta de tempo

Follow-ups:

1. Por que esses dois são os mais difíceis?
2. O que acontece se eles não forem resolvidos?
3. Qual deles você pagaria para resolver primeiro?
4. Qual deles você acha chato, mas não pagaria para resolver?

### Trust And Citation Evidence

Do not pitch too early. Frame as a hypothetical after current workflow is clear.

```txt
Imagina que você recebesse um rascunho de revisão bibliográfica em que cada afirmação importante tivesse uma citação clicável, o trecho de evidência usado e um alerta sobre a qualidade da fonte. O que você iria checar antes de confiar?
```

Follow-ups:

1. O que faria você desconfiar desse texto?
2. Que tipo de fonte você considera aceitável para TCC?
3. O que você espera que o orientador aceite ou rejeite?
4. Você preferiria receber só as referências organizadas, um rascunho escrito, ou rascunho com citações auditáveis?
5. O que seria perigoso ou antiético nesse tipo de ferramenta?
6. O que teria que ficar sob sua responsabilidade como estudante?

### Willingness To Pay And Existing Spend

Ask about past behavior before price hypotheticals.

1. Você já pagou, pensou em pagar, ou conhece alguém que pagou ajuda para TCC?
2. O que exatamente foi contratado: orientação, revisão, formatação, busca, escrita, execução completa?
3. Você lembra a faixa de preço ou como a pessoa decidiu que valia pagar?
4. O que faria você considerar pagar por ajuda na revisão bibliográfica?
5. Se algo economizasse uma ou duas semanas e entregasse um rascunho auditável, qual faixa pareceria aceitável?
6. Em que ponto do prazo você pagaria: agora, perto da entrega, depois de travar, ou nunca?

Do not treat stated willingness as proof. Prefer actual spend, considered spend, or concrete trade-off.

### Academic Integrity And Safety

1. Onde fica a linha entre ajuda aceitável e alguém fazer o TCC por você?
2. O que você precisaria revisar pessoalmente antes de entregar?
3. Você contaria para o orientador que usou uma ferramenta de apoio? Por quê?
4. Que aviso ou controle deixaria a ferramenta mais segura?
5. O que a ferramenta jamais deveria prometer?

### Closing

1. O que eu não perguntei e deveria ter perguntado?
2. Quem mais vive esse problema e poderia conversar comigo?
3. Você toparia ver um exemplo manual depois, se ele existisse?
4. Posso te procurar para tirar uma dúvida rápida depois?

## Note-Taking Template

Use one copy per respondent. Do not store names, phone numbers, email, social handles, or raw private details in repository artifacts unless a future ticket explicitly approves retention.

```md
# TCC Discovery Interview Note

## Metadata

- Respondent label: P01 / P02 / P03 / P04 / P05
- Date:
- Interviewer:
- Course:
- TCC type: theoretical / bibliographic / experimental / mixed
- TCC stage:
- Deadline pressure: low / medium / high
- Recording exists outside repo: yes/no
- Transcript exists outside repo: yes/no
- Repository-safe summary only: yes/no

## Context

- Theme already defined by advisor: yes/no/partial
- Required topics:
- Current stage in bibliographic review:
- Trigger moment:

## Current Workflow

- Last attempt to work on review:
- Tools/sources used:
- Output produced:
- What got stuck:
- Time spent:

## Pain Ranking

- Top pain 1:
- Top pain 2:
- Other pains:
- Pain intensity: low / medium / high
- Evidence type: behavior / quote / spend / workaround / assumption

## Workaround And Spend

- Current workaround:
- Paid help used or considered:
- Known peer behavior:
- Price anchor:
- Commitment signal:

## Trust And Citation Evidence

- Would citation traceability help? yes/no/mixed
- What they would check:
- Source-quality expectations:
- Trust blockers:
- Advisor acceptance concern:

## Academic Integrity

- Acceptable assistance:
- Unacceptable / ghostwriting boundary:
- Student responsibility:
- Required warnings or controls:

## First Output Preference

- References only:
- Structure + references:
- Draft text:
- Draft text + auditable citations:
- Other:

## Quotes Or Exact Language

Store only repository-safe anonymized quotes.

- Quote 1:
- Quote 2:

## Contradictions

- Evidence supporting thesis:
- Evidence weakening thesis:
- Ambiguous signal:
- New risk:

## Interviewer Synthesis

- Strongest signal:
- Weakest signal:
- Confidence change: increased / unchanged / decreased
- Recommended decision: GO / CONDITIONAL GO / REFINE / NO-GO / BLOCKED
- Follow-up needed:
```

## Batch Synthesis Template

Use this after the five interviews. This is the format the founder can paste back into Pipe after completing the conversations.

```md
# TCC Discovery Batch Synthesis

## Metadata

- Origin ticket: PIP-336
- Evidence batch: 5 manual interviews
- Raw data handled in repository: no by default
- Repository artifact contains: anonymized synthesis

## Source Coverage

| Source label | Course | TCC type | Deadline pressure | Evidence quality |
|---|---|---|---|---|
| P01 |  |  | Low / Medium / High | Low / Medium / High |
| P02 |  |  | Low / Medium / High | Low / Medium / High |
| P03 |  |  | Low / Medium / High | Low / Medium / High |
| P04 |  |  | Low / Medium / High | Low / Medium / High |
| P05 |  |  | Low / Medium / High | Low / Medium / High |

## Pattern Summary

- Repeated pain:
- Trigger moment:
- Current workaround:
- Paid workaround:
- Trust requirement:
- Academic integrity concern:
- First output preference:
- Price signal:

## Evidence Table

| Evidence | Type | Sources | Confidence | Notes |
|---|---|---|---|---|
|  | behavior / quote / spend / workaround / objection / commitment | P01, P02... | Low / Medium / High |  |

## Contradiction Review

- Evidence supporting current thesis:
- Evidence contradicting current thesis:
- Ambiguous or mixed signals:
- Evidence weakening ICP specificity:
- Evidence weakening pain intensity:
- Evidence weakening willingness to pay:
- New risk or objection:

## Decision

- Decision impact: GO / CONDITIONAL GO / REFINE / NO-GO / BLOCKED
- Reason:
- Next allowed stage:
- Blocked stages:
- Follow-up tickets needed:
```

## GO Criteria

Use these as a directional gate before PRD. Do not force a positive conclusion.

- At least 4 of 5 respondents fit the target profile or a clearly adjacent high-fit profile.
- At least 3 of 5 describe a recent concrete struggle starting or progressing the bibliographic review.
- At least 3 of 5 rank search plus writing, citation evidence, or source trust among the top two pains.
- At least 3 of 5 say citation traceability would materially increase trust.
- At least 2 of 5 have paid, considered paying, or know a concrete peer example of paying for TCC help.
- At least 2 of 5 react credibly to a price range near R$ 100-300 for urgent deadline support.
- No dominant academic-integrity objection makes the first promise unsafe as an assisted workflow.

## Conditional GO Criteria

Use this when there is enough signal to continue learning, but not enough to create product scope.

- Pain is strong, but willingness to pay is unclear.
- Students want search and organization, but not generated text.
- Citation traceability is trusted only with strict review controls.
- Chemistry is too narrow, but adjacent STEM students show stronger signal.
- Students want the result, but advisor acceptance is a blocker.

Allowed next action after CONDITIONAL GO:

- refine ICP
- run a second interview batch
- run a manual concierge sample with one approved non-sensitive topic
- create a research spike for academic-source coverage only after validation evidence supports it

## NO-GO Or Pivot Criteria

- Fewer than 2 of 5 report a recent concrete pain.
- Most respondents say generic ChatGPT/SciELO is enough.
- Main pain is only ABNT formatting, not search/writing/evidence.
- Students want full ghostwriting as the primary value.
- Students would not pay and have no meaningful workaround cost.
- Advisor/institution acceptance risk dominates the value.
- The first ICP is unreachable manually.

## Blocked Actions

These remain blocked after this plan:

- PRD as accepted product scope
- MVP build
- academic search integration
- automated lead sourcing
- automated outreach
- AI phone calls
- billing or paid collection
- public claims of validation
- storing raw recordings or raw identifiable transcripts in the repository

## Allowed Next Action

Run five manual discovery conversations and return to Pipe with either:

- the completed note-taking templates, sanitized enough for repository synthesis, or
- a batch synthesis using the template above, or
- a blocker explaining why five interviews could not be completed.

## Capability Handoff

Future agents processing this round should use:

- `capability.external.pm-skills` for interview synthesis patterns
- `validation/raw-interview-evidence-intake-and-synthesis.md` for evidence boundaries
- `validation/market-validation-before-code-gate.md` before PRD or build
- `capability.external.linear-mcp` for status and follow-up tracking

Do not use:

- `capability.external.consensus` until the validation round justifies academic-source research
- `capability.external.notebooklm` unless an approved source set exists
- `capability.external.notion-mcp` unless the ticket explicitly asks to register the final approved discovery artifact in Notion
- `capability.future.openclaw-paperclip` for any current execution
