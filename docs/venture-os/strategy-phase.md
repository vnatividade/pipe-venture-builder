# Fase product-strategy (fatia 3)

Primeira fase pós-intake rodando pelo motor — prova o padrão genérico de fase e o Prompt Compiler v0.

```txt
PRODUCT_STRATEGY_READY ──run-phase──► PRODUCT_STRATEGY_IN_PROGRESS (run: awaiting_executor)
   │ prompt-compiler registra o pacote (artefato versionado, referências+hashes, convenção "(fonte: ...)")
   ▼ executor (Claude Code — ADR-VOS-007) escreve product-vision.md + hypotheses.md
submit ──► PRODUCT_STRATEGY_REVIEW ──gate──► APPROVED ──► MVP_REFINEMENT_READY (+ baseline → controle_evaluation)
   │ reprovou: 1ª vez volta ao executor (attempt+1); esgotado → decisão humana → retomada
```

## Comandos

```bash
node runtime/cli/pipe-os.mjs run-phase --project <slug>
# ler o pacote em ~/.pipe/venture-os/projects/<slug>/artifacts/prompt-package-product-strategy/vN/prompt-package.md
node runtime/cli/pipe-os.mjs submit --project <slug> --files /caminho/product-vision.md,/caminho/hypotheses.md
```

## Gate `strategy-completeness-gate` (determinístico)

artefatos presentes · proposta de valor clara · público identificável (hipótese vale) · problema↔
solução conectados · ≥2 hipóteses explícitas · riscos registrados · **todo bullet com `(fonte: ...)`
reconhecida — item sem fonte é invenção e reprova** · próxima ação definida. Reviewer advisory
(`strategy-reviewer`): claims de evidência de mercado, escopo prematuro, baixa sobreposição com
fontes, ausência de lacunas marcadas.

## Fronteiras

O executor não decide público/proposta definitivos (nível 4 — entram como hipóteses); monetização/
growth/pricing são fora de escopo (gates absolutos); avanço do baseline usa supersessão por
identidade (nunca baseline paralelo); sem baseline importado o avanço é registrado como não emitido
com motivo (nunca silencioso).
