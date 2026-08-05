# Reconciliação agendada do Linear

Operação do item 4 de PIP-835. **Ação de risco** em `AGENTS.md` ("scheduling or
enabling production jobs"), liberada nomeadamente pelo fundador em 2026-08-05.

## O que roda

Diariamente às 08:20, `scripts/linear-reconcile.sh` executa `pipe reconcile plan`
sobre o projeto declarado em `.pipe/linear.json` e grava:

| Arquivo | Conteúdo |
|---|---|
| `~/.pipe/linear/reconcile.log` | uma linha por execução: `OK <resumo>` ou `ERRO <motivo>` |
| `~/.pipe/linear/<projeto>-<timestamp>.json` | o relatório completo daquela execução |
| `~/.pipe/linear/launchagent.err.log` | stderr do launchd, se houver |

Tudo fora do git: relatório é observação datada, não fonte de verdade. Versionar
transformaria cada execução em ruído de diff.

## Instalação

```sh
python3 -m venv ~/.pipe/venv && ~/.pipe/venv/bin/pip install -e .
cp scripts/launchagent/ai.pipe.linear-reconcile.plist ~/Library/LaunchAgents/
launchctl unload ~/Library/LaunchAgents/ai.pipe.linear-reconcile.plist 2>/dev/null
launchctl load  ~/Library/LaunchAgents/ai.pipe.linear-reconcile.plist
launchctl start ai.pipe.linear-reconcile   # disparo manual para conferir
```

O venv em `~/.pipe/venv` é deliberado: um LaunchAgent apontando para um venv
efêmero quebra em silêncio semanas depois de funcionar.

## Segredo

O script lê o token do Vaultwarden **em tempo de execução** e nunca o imprime,
grava ou exporta além do processo do `pipe`. O plist não contém segredo nenhum.

Se a sessão do cofre expirar, o script **falha alto** e registra o motivo. Esse é
o ponto: um job que apenas "não faz nada" parece um job saudável que não achou
deriva. Silêncio não é sinal de saúde.

## Limitações conhecidas

1. **O agendador não é versionado.** A cópia efetiva do plist vive em
   `~/Library/LaunchAgents/`; o repositório guarda só o template. O check
   agendado depende de estado machine-local, e o repositório não consegue provar
   que ele está instalado.
2. **Sem baseline, a cobertura não é calculada.** O relatório reporta
   `coverageStatus: unavailable` e `clean: false` — nunca zero. Para que a deriva
   de cobertura apareça, passe um ProductBaseline aprovado ao comando.
3. **A conformidade de corpo continua `unavailable`** enquanto a decisão D5 não
   for tomada: o snapshot descarta descrição por decisão registrada em
   `docs/connectors/README.md`.
4. **A máquina precisa estar ligada.** É LaunchAgent, não cron de servidor.

## Desativar

```sh
launchctl unload ~/Library/LaunchAgents/ai.pipe.linear-reconcile.plist
rm ~/Library/LaunchAgents/ai.pipe.linear-reconcile.plist
```
