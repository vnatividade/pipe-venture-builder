#!/bin/bash
# Reconciliação agendada do Linear (PIP-835, item 4).
#
# Ação de risco em AGENTS.md ("scheduling or enabling production jobs"), liberada
# nomeadamente pelo fundador em 2026-08-05. Este script:
#   - lê o token do Vaultwarden em tempo de execução (fluxo aprovado);
#   - NUNCA imprime, grava nem exporta o token para além do processo do pipe;
#   - falha ALTO e registra no log quando não consegue rodar.
#
# O modo de falha que mais importa é o silencioso: se a sessão do cofre expirar,
# um job que apenas "não faz nada" parece um job saudável que não achou deriva.
# Por isso toda saída anômala vira linha de log com motivo explícito.
set -uo pipefail

REPO="${PIPE_REPO_ROOT:-$HOME/Developer/pipe-venture-builder}"
LOG_DIR="${PIPE_LINEAR_REPORT_ROOT:-$HOME/.pipe/linear}"
LOG="$LOG_DIR/reconcile.log"
VAULT_ITEM="Linear — API key pessoal (workspace Natiivis)"
VW="${VW_BIN:-$HOME/.local/bin/vw}"

mkdir -p "$LOG_DIR"
registrar() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" >> "$LOG"; }

# Resolve o binário do pipe. Um LaunchAgent apontando para um venv efêmero quebra
# em silêncio semanas depois — por isso a ordem começa por caminhos duráveis.
PIPE=""
for candidato in "${PIPE_BIN:-}" "$HOME/.pipe/venv/bin/pipe" "$(command -v pipe 2>/dev/null)"; do
  if [ -n "$candidato" ] && [ -x "$candidato" ]; then PIPE="$candidato"; break; fi
done
if [ -z "$PIPE" ]; then
  registrar "ERRO pipe não encontrado (procurei em PIPE_BIN, ~/.pipe/venv/bin/pipe e PATH)"
  exit 1
fi

if [ ! -d "$REPO" ]; then
  registrar "ERRO repositório ausente em $REPO"
  exit 1
fi

if [ ! -x "$VW" ]; then
  registrar "ERRO wrapper do Vaultwarden ausente em $VW"
  exit 1
fi

TOKEN="$("$VW" get item "$VAULT_ITEM" 2>/dev/null | jq -r '.notes // empty')"
if [ -z "$TOKEN" ]; then
  # Causa mais provável: sessão do cofre expirou. NÃO tentar contornar.
  registrar "ERRO token indisponível no cofre — sessão provavelmente expirada; rode ~/Desktop/command/vaultwarden-agent-setup.command"
  exit 1
fi

cd "$REPO" || { registrar "ERRO não consegui entrar em $REPO"; exit 1; }

SAIDA="$(LINEAR_API_KEY="$TOKEN" "$PIPE" reconcile plan --json 2>&1)"
CODIGO=$?
unset TOKEN

if [ "$CODIGO" -ne 0 ]; then
  registrar "ERRO reconcile falhou (exit $CODIGO): $(printf '%s' "$SAIDA" | head -c 300)"
  exit "$CODIGO"
fi

RESUMO="$(printf '%s' "$SAIDA" | jq -c '{clean, summary}' 2>/dev/null || echo 'saída ilegível')"
registrar "OK $RESUMO"
exit 0
