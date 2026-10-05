#!/usr/bin/env python3
"""Local routing and evidence helper. Never invokes a model during inspection."""
import argparse
from datetime import datetime, timezone
try:
    import fcntl
except ImportError:  # Selection and inspection remain available on Windows.
    fcntl = None
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib

ROOT = Path(__file__).resolve().parent
BEGIN = '<!-- AGENT-MODEL-POLICY:START -->'
END = '<!-- AGENT-MODEL-POLICY:END -->'
TASKS = ('mechanical', 'search', 'feature', 'plan', 'refactor', 'bug', 'architecture', 'review')
ROLES = ('worker', 'builder', 'architect', 'reviewer')


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def matrix():
    return read_json(ROOT / 'matrix.json')


def atomic(path, data, mode=0o600):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()


def valid_model(runtime, value):
    if not re.fullmatch(r'[a-zA-Z0-9._-]+', value):
        return False
    return value.startswith('gpt-') if runtime == 'codex' else bool(
        value in ('haiku', 'sonnet', 'opus') or value.startswith('claude-'))


def family(runtime, value):
    if runtime == 'claude' and value:
        for alias in ('haiku', 'sonnet', 'opus'):
            if value == alias or re.match(r'^claude-' + alias + r'(?:-|$)', value):
                return alias
    return value


def select(runtime, task='feature', role=None, critical=False, ambiguous=False,
           failed_hypotheses=0, architect_failures=0, resolved=False,
           explicit_model=None, explicit_effort=None, authorization=None):
    if min(failed_hypotheses, architect_failures) < 0:
        raise ValueError('Contadores de hipóteses não podem ser negativos')
    reason = 'requisitos claros ou planejamento normal'
    if role is None:
        if task == 'review':
            role, reason = 'reviewer', 'revisão solicitada'
        elif resolved:
            role, reason = 'builder', 'decisão resolvida; retornar à implementação'
        elif ambiguous or task == 'architecture' or failed_hypotheses >= 2:
            role, reason = 'architect', 'arquitetura, ambiguidade ou duas hipóteses distintas fracassadas'
        elif task in ('mechanical', 'search') and not critical:
            role, reason = 'worker', 'regra mecânica clara e baixo risco'
        else:
            role = 'builder'
    else:
        reason = 'papel solicitado explicitamente'
    if role == 'worker' and (critical or ambiguous or failed_hypotheses >= 2):
        role = 'architect' if ambiguous or failed_hypotheses >= 2 else 'builder'
        reason = 'Worker incompatível com risco/ambiguidade; promover papel'
    chosen = matrix()['roles'][role][runtime].copy()
    if role == 'reviewer' and critical and runtime == 'codex':
        chosen['effort'] = 'medium'
    if role == 'architect' and architect_failures >= 2:
        chosen['effort'] = 'high'
        reason += '; duas abordagens de Architect insuficientes documentadas'
    if explicit_effort and not explicit_model:
        raise ValueError('Esforço explícito exige modelo e autorização da tarefa')
    if explicit_model:
        if not authorization or not authorization.strip():
            raise ValueError('Escolha explícita exige referência à autorização humana')
        if not valid_model(runtime, explicit_model):
            raise ValueError('Modelo inválido ou de outro provedor; sem fallback')
        chosen = {'model': explicit_model, 'effort': explicit_effort}
        reason = 'escolha explícita do usuário para a tarefa'
    return {'version': matrix()['version'], 'runtime': runtime, 'role': role,
            'reason': reason, 'recommended': chosen,
            'authorization': authorization if explicit_model else None,
            'deliverable': matrix()['roles'][role]['deliverable'],
            'review_required': bool(critical),
            'transition_status': 'recommended_not_observed'}


def inspect(runtime, project, home):
    project, home = Path(project).resolve(), Path(home).resolve()
    layers, uncertainties, warnings = [], [], []
    effective = {'model': None, 'effort': None, 'plan_effort': None}
    if runtime == 'codex':
        paths = [home / '.codex/config.toml']
        for parent in [*reversed(project.parents), project]:
            p = parent / '.codex/config.toml'
            if p not in paths:
                paths.append(p)
        for path in paths:
            if path.is_file():
                data = tomllib.loads(path.read_text(encoding='utf-8'))
                values = {out: data[key] for key, out in (
                    ('model', 'model'), ('model_reasoning_effort', 'effort'),
                    ('plan_mode_reasoning_effort', 'plan_effort')) if key in data}
                effective.update(values)
                layers.append({'path': str(path), 'selection': values})
        for script in ('scripts/codex-gpt6', 'scripts/codex'):
            path = project / script
            if path.is_file():
                # Signals only; never execute project code or print its contents.
                content = path.read_text(encoding='utf-8')
                if 'effort=high' in content or 'model_reasoning_effort=high' in content:
                    warnings.append({'path': str(path), 'reason': 'launcher contém esforço high; inspecionar por papel'})
        uncertainties.append('confiança do projeto, perfis, flags, política gerenciada e sessão do aplicativo')
        env_names = ('OPENAI_MODEL',)  # no generic environment or credential enumeration
    else:
        paths = [home / '.claude/settings.json']
        for parent in [*reversed(project.parents), project]:
            for filename in ('settings.json', 'settings.local.json'):
                p = parent / '.claude' / filename
                if p not in paths:
                    paths.append(p)
        for path in paths:
            if path.is_file():
                data = read_json(path)
                values = {out: data[key] for key, out in (
                    ('model', 'model'), ('effortLevel', 'effort')) if key in data}
                effective.update(values)
                layers.append({'path': str(path), 'selection': values})
        uncertainties.append('flags, settings sources, política gerenciada, host e escolha conservada na sessão')
        env_names = ('ANTHROPIC_MODEL', 'ANTHROPIC_DEFAULT_MODEL', 'CLAUDE_CODE_EFFORT_LEVEL')
    # Report presence, not environment values.
    for key in env_names:
        if key in os.environ:
            uncertainties.append(key + ' presente: override não resolvido pelo helper')
    instructions = home / ('.codex/AGENTS.md' if runtime == 'codex' else '.claude/CLAUDE.md')
    referenced = instructions.is_file() and BEGIN in instructions.read_text(encoding='utf-8')
    return {'runtime': runtime, 'project': str(project), 'configured': effective,
            'layers': layers, 'global_policy_reference': referenced,
            'warnings': warnings, 'unresolved_layers': uncertainties,
            'effective_runtime_status': 'not_verified'}


def check(selection, configuration, observation=None):
    runtime = selection['runtime']
    expected = selection['recommended']
    configured = configuration['configured']
    issues = []
    for field in ('model', 'effort'):
        if expected[field] is not None and family(runtime, configured.get(field)) != family(runtime, expected[field]):
            issues.append('configured_' + field + '_mismatch_or_unknown')
    if not configuration['global_policy_reference']:
        issues.append('global_policy_reference_missing')
    status = 'not_verified'
    observed = None
    if observation is not None:
        required = ('runtime', 'model', 'effort', 'source', 'observed_at', 'session_id', 'project')
        if any(key not in observation for key in required):
            raise ValueError('Observação incompleta; requer runtime/model/effort/source/observed_at/session_id/project')
        if observation['runtime'] != runtime:
            raise ValueError('Observação pertence a outro runtime')
        for key in ('model', 'source', 'session_id', 'project'):
            if not isinstance(observation[key], str) or not observation[key].strip():
                raise ValueError('Observação inválida: ' + key)
        stamp = datetime.fromisoformat(observation['observed_at'].replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('Observação exige horário com fuso')
        age = (datetime.now(timezone.utc) - stamp).total_seconds()
        if not 0 <= age <= 86400:
            raise ValueError('Observação futura ou com mais de 24 horas')
        if not Path(observation['project']).is_absolute() or Path(observation['project']).resolve() != Path(configuration['project']):
            raise ValueError('Observação pertence a outro projeto')
        observed = {key: observation[key] for key in required}
        status = 'matches' if all(expected[k] is None or family(runtime, observed[k]) == family(runtime, expected[k])
                                  for k in ('model', 'effort')) else 'mismatch'
        if status == 'mismatch':
            issues.append('observed_selection_mismatch')
    return {'selection': selection, 'configuration': configuration,
            'observed': observed, 'observation_status': status,
            'configuration_status': 'divergent' if any(i.startswith('configured_') for i in issues) else 'matches_files',
            'issues': issues,
            'limits': 'Observação fornecida pelo operador; arquivos não comprovam sessão, acesso ou inferência.'}


def block(existing, body):
    if existing.count(BEGIN) != existing.count(END) or existing.count(BEGIN) > 1:
        raise ValueError('Bloco de política duplicado ou incompleto')
    new = BEGIN + '\n' + body.rstrip() + '\n' + END
    if BEGIN in existing:
        pattern = re.escape(BEGIN) + r'.*?' + re.escape(END)
        return re.sub(pattern, lambda _: new, existing, flags=re.S)
    return existing.rstrip() + '\n\n' + new + '\n'


def edit_toml(text, values):
    # Only root keys before the first table; never overwrite MCP/project sections.
    cut = re.search(r'^\s*\[', text, re.M)
    head, rest = (text[:cut.start()], text[cut.start():]) if cut else (text, '')
    for key, value in values.items():
        line = key + ' = ' + json.dumps(value)
        pattern = r'^' + re.escape(key) + r'\s*=.*$'
        if re.search(pattern, head, re.M):
            head = re.sub(pattern, line, head, flags=re.M)
        else:
            head = line + '\n' + head
    result = head + rest
    tomllib.loads(result)
    return result


def install(home, dry_run=False, replace_version=False, approval_reference=None):
    if os.name != 'posix':
        raise ValueError('Instalação global suporta macOS/Linux; no Windows use select/inspect/check e configure o runtime manualmente')
    home = Path(home).resolve()
    # Never write a standard home when a runtime uses a custom config root.
    for name, standard in (('CODEX_HOME', home / '.codex'), ('CLAUDE_CONFIG_DIR', home / '.claude')):
        configured = os.environ.get(name)
        if configured and Path(configured).expanduser().resolve() != standard:
            raise ValueError(name + ' personalizado: instalação global bloqueada; reconciliar destino sem copiar configuração')
    # Check all known ancestors before reading any destination file.
    for relative in ('.agents/model-policy/INSTALLATION.json', '.codex/config.toml',
                     '.codex/AGENTS.md', '.claude/settings.json', '.claude/CLAUDE.md',
                     'AGENTS.md', '.local/bin/agent-model',
                     '.agents/skills/repo-padrao/SKILL.md', '.local/state/agent-model/backups'):
        for path in (home / relative, *(home / relative).parents):
            if path == home:
                break
            if path.is_symlink():
                raise ValueError('Destino ou diretório gerenciado é symlink; preservar')
    central = home / '.agents/model-policy'
    payload = {
        'matrix.json': (ROOT / 'matrix.json').read_bytes(),
        'model_policy.py': Path(__file__).read_bytes(),
        'POLICY.md': (ROOT / 'POLICY.md').read_bytes(),
        'ONBOARDING.md': (ROOT / 'ONBOARDING.md').read_bytes(),
    }
    # Installed docs use local central links instead of repository-relative links.
    payload['POLICY.md'] = payload['POLICY.md'].replace(b'../tools/model-policy/matrix.json', b'matrix.json').replace(b'model-policy-onboarding.md', b'ONBOARDING.md')
    receipt_path = central / 'INSTALLATION.json'
    if receipt_path.is_symlink():
        raise ValueError('Receipt é symlink; preservar')
    if central.is_symlink():
        raise ValueError('Destino central é symlink; preservar e reconciliar')
    receipt_before = receipt_path.read_bytes() if receipt_path.exists() else None
    old_receipt = json.loads(receipt_before) if receipt_before is not None else None
    if central.exists() and not old_receipt:
        raise ValueError('Diretório central preexistente sem receipt; preservar')
    if old_receipt:
        for name, checksum in old_receipt['payload_sha256'].items():
            p = central / name
            if not p.is_file() or p.is_symlink() or digest(p.read_bytes()) != checksum:
                raise ValueError('Drift no arquivo instalado: ' + name)
        different = any(old_receipt['payload_sha256'].get(n) != digest(v) for n, v in payload.items())
        if different and not (replace_version and approval_reference and approval_reference.strip()):
            raise ValueError('Atualização exige --replace-version e referência à aprovação humana')
    paths = {}
    defaults = matrix()['roles']['builder']
    for runtime in ('codex', 'claude'):
        if not valid_model(runtime, defaults[runtime]['model']):
            raise ValueError('Padrão inválido na matriz')
    common = ('## Modelos e entregáveis\n\n'
              'Leia `~/.agents/model-policy/POLICY.md` ao começar trabalho ou reavaliar modelos.\n'
              f'Use `agent-model select/check`; padrão Codex {defaults["codex"]["model"]}/{defaults["codex"]["effort"]}, '
              f'Claude {defaults["claude"]["model"]}/{defaults["claude"]["effort"]}.\n'
              'Escolha explícita por tarefa prevalece; preserve sessões/contratos em andamento.\n'
              'Trocas dentro do runtime são autorizadas e anunciadas, com confirmação do modelo efetivo.\n'
              'Sem acesso à troca, prepare passagem e peça alteração no seletor. Sem fallback de provedor.\n'
              'Não criar agentes/tarefas adicionais por escolha de modelo.\n'
              'Novo lançamento: somente por aviso humano, reavaliar arquitetura operacional, regras e políticas;\n'
              'entregar proposta/diff e aguardar aprovação antes de adotar. Sem monitoramento agendado.\n'
              'Modelo indisponível ou configuração divergente deve ser registrado, sem alegar conformidade.\n')
    for rel in ('AGENTS.md', '.codex/AGENTS.md', '.claude/CLAUDE.md'):
        p = home / rel
        existing = p.read_text(encoding='utf-8') if p.exists() else ''
        body = common + ('\n@~/.agents/model-policy/POLICY.md\n' if rel == '.claude/CLAUDE.md' else '')
        paths[p] = block(existing, body).encode()
    # Extend the installed shared onboarding without replacing the skill bundle.
    skill = home / '.agents/skills/repo-padrao/SKILL.md'
    if skill.is_file():
        paths[skill] = block(skill.read_text(encoding='utf-8'),
            '## Roteamento de modelos no onboarding\n\n'
            'Leia `~/.agents/model-policy/ONBOARDING.md`; inventarie configurações com\n'
            '`agent-model inspect/check` nas duas ferramentas. Reconcile overrides sob\n'
            'ticket/worktree próprios; preserve contratos ativos e registre impedimentos.\n').encode()
    codex = home / '.codex/config.toml'
    old = codex.read_text(encoding='utf-8') if codex.exists() else ''
    codex_values = {'model': defaults['codex']['model'], 'model_reasoning_effort': defaults['codex']['effort']}
    if 'plan_mode_reasoning_effort' in tomllib.loads(old):
        codex_values['plan_mode_reasoning_effort'] = defaults['codex']['effort']
    paths[codex] = edit_toml(old, codex_values).encode()
    claude = home / '.claude/settings.json'
    settings = read_json(claude) if claude.exists() else {}
    settings.update(model=defaults['claude']['model'], effortLevel=defaults['claude']['effort'])
    paths[claude] = json_bytes(settings)
    wrapper = home / '.local/bin/agent-model'
    script = '#!/bin/sh\nset -eu\nexec ' + shlex.quote(sys.executable) + ' ' + shlex.quote(str(central / 'model_policy.py')) + ' "$@"\n'
    if wrapper.exists() and (not old_receipt or str(wrapper) not in old_receipt.get('managed_paths', [])):
        raise ValueError('Wrapper preexistente não gerenciado; preservar')
    paths[wrapper] = script.encode()
    for name, data in payload.items():
        paths[central / name] = data
    changes = {}
    for path, data in paths.items():
        for ancestor in (path, *path.parents):
            if ancestor == home:
                break
            if ancestor.is_symlink():
                raise ValueError('Destino ou diretório gerenciado é symlink; preservar')
        if path.is_symlink():
            raise ValueError('Arquivo gerenciado é symlink; preservar: ' + str(path))
        before = path.read_bytes() if path.exists() else None
        if before != data:
            changes[path] = (before, data)
    result = {'version': matrix()['version'], 'dry_run': dry_run,
              'changed_paths': [str(p) for p in changes],
              'sessions_modified': False, 'global_defaults': matrix()['roles']['builder'],
              'limits': 'Novas sessões; overrides locais e inferência exigem verificação.'}
    if dry_run or not changes:
        return result
    backup = home / '.local/state/agent-model/backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup.mkdir(parents=True, mode=0o700)
    os.chmod(backup, 0o700)
    backups = []
    for idx, (path, (before, after)) in enumerate(changes.items()):
        previous_mode = path.stat().st_mode & 0o777 if path.exists() else None
        backup_path = backup / str(idx)
        if before is not None:
            atomic(backup_path, before)
        backups.append({'path': str(path), 'before_sha256': digest(before) if before is not None else None,
                        'after_sha256': digest(after), 'backup': str(backup_path) if before is not None else None,
                        'before_mode': previous_mode})
    # Compare again before mutations; avoid clobbering concurrent edits.
    for path, (before, _) in changes.items():
        if (path.read_bytes() if path.exists() else None) != before:
            raise ValueError('Alteração concorrente: ' + str(path))
    written = []
    try:
        for path, (_, data) in changes.items():
            old_mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
            atomic(path, data, 0o755 if path == wrapper else old_mode)
            written.append(path)
        receipt = {'version': matrix()['version'], 'installed_at': now(), 'source': str(ROOT),
                   'approval_reference': approval_reference,
                   'payload_sha256': {n: digest(v) for n, v in payload.items()},
                   'managed_paths': [str(p) for p in paths], 'backups': backups,
                   'previous_receipt': str(backup / 'previous-receipt.json') if old_receipt else None,
                   'limits': result['limits']}
        if old_receipt:
            atomic(backup / 'previous-receipt.json', json_bytes(old_receipt))
        atomic(receipt_path, json_bytes(receipt))
        atomic(backup / 'changes.json', json_bytes(backups))
    except Exception:
        for path in reversed(written):
            before = changes[path][0]
            if before is None:
                path.unlink()
            else:
                mode = next(b['before_mode'] for b in backups if b['path'] == str(path))
                atomic(path, before, mode)
        if receipt_before is None:
            if receipt_path.exists():
                receipt_path.unlink()
        else:
            atomic(receipt_path, receipt_before)
        raise
    result['receipt'] = str(receipt_path)
    result['backup_manifest'] = str(backup / 'changes.json')
    return result


def release(home, runtime, model, notice, reopen=None):
    if fcntl is None:
        raise ValueError('Registro de lançamentos requer macOS/Linux; nenhuma avaliação criada')
    if not notice.strip():
        raise ValueError('Gatilho exige referência ao aviso humano')
    if not valid_model(runtime, model):
        raise ValueError('Identificador de modelo inválido ou provedor incorreto')
    state = Path(home).resolve() / '.local/state/agent-model'
    state.mkdir(parents=True, exist_ok=True)
    key = digest((runtime + ':' + model).encode())[:24]
    with (state / 'releases.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        registry_path = state / 'releases.json'
        registry = read_json(registry_path) if registry_path.exists() else {'releases': {}}
        evaluations = registry['releases'].get(key, [])
        if evaluations and not reopen:
            return {'deduplicated': True, 'evaluation': evaluations[-1], 'policy_changed': False}
        if reopen is not None and not reopen.strip():
            raise ValueError('Reabertura exige motivo')
        folder = state / 'evaluations' / (key + '-' + str(len(evaluations) + 1))
        folder.mkdir(parents=True)
        report = ('# Reavaliação de modelo\n\n'
                  f'Runtime: {runtime}\nModelo/versão: {model}\nPolítica vigente: {matrix()["version"]}\n'
                  f'Aviso humano: {notice}\nReabertura: {reopen or "não"}\n\n'
                  'Estado: aguardando avaliação; não aprovado nem adotado.\n\n'
                  '## Fontes oficiais e disponibilidade\n\nPreencher: versão, fontes, capacidades, esforço e acesso real.\n\n'
                  '## Operação dos agentes\n\nAvaliar papéis, roteamento, arquitetura do fluxo, contexto, entregáveis, regras e políticas.\n\n'
                  '## Evidências\n\nTarefas representativas, modelo/esforço observados, resultados, custo observado ou não medido e limitações.\n\n'
                  '## Proposta e alternativa\n\nComparar adotar com manter o estado atual. Preencher benefícios e riscos.\n\n'
                  '## Critérios e reversão\n\nPreencher critérios de adoção, migração de novos trabalhos e reversão.\n\n'
                  '## Impactos nos produtos\n\nSomente propostas por projeto; não iniciar implementação.\n\n'
                  '## Decisão humana\n\nPendente. Registrar referência à aprovação/rejeição antes de alterar a política.\n')
        atomic(folder / 'REVIEW.md', report.encode())
        atomic(folder / 'PROPOSAL.diff', b'# Preencher o diff proposto. Nenhuma alteracao aplicada.\n')
        entry = {'runtime': runtime, 'model': model, 'notice': notice,
                 'created_at': now(), 'reopen_reason': reopen,
                 'policy_version': matrix()['version'], 'status': 'awaiting_evaluation',
                 'report': str(folder / 'REVIEW.md'), 'proposal': str(folder / 'PROPOSAL.diff')}
        evaluations.append(entry)
        registry['releases'][key] = evaluations
        atomic(registry_path, json_bytes(registry))
        return {'deduplicated': False, 'evaluation': entry, 'policy_changed': False}


def launch(selection, project, extra):
    runtime = selection['runtime']
    executable = shutil.which(runtime)
    if not executable:
        raise ValueError('Runtime indisponível: ' + runtime)
    chosen = selection['recommended']
    # Prevent forwarded flags from silently overriding selection or permissions.
    if extra:
        raise ValueError('Launch não encaminha argumentos; use o CLI diretamente para exceções autorizadas')
    argv = [executable, '--model', chosen['model']]
    if runtime == 'codex':
        argv += ['-C', str(Path(project).resolve())]
        if chosen['effort']:
            argv += ['-c', 'model_reasoning_effort=' + json.dumps(chosen['effort'])]
    elif chosen['effort']:
        argv += ['--effort', chosen['effort']]
    print(json.dumps({'launch': argv, 'role': selection['role'], 'reason': selection['reason'],
                      'status': 'launch_requested_not_observed'}, ensure_ascii=False), flush=True)
    os.chdir(Path(project).resolve())
    os.execv(executable, argv)


def add_arguments(parser):
    parser.add_argument('--home', type=Path, default=Path.home())
    parser.add_argument('--json', action='store_true')
    subs = parser.add_subparsers(dest='command', required=True)
    for command in ('select', 'inspect', 'check', 'launch'):
        p = subs.add_parser(command)
        p.add_argument('--runtime', choices=('codex', 'claude'), required=True)
        p.add_argument('--project', type=Path, default=Path.cwd())
        if command != 'inspect':
            p.add_argument('--task', choices=TASKS, default='feature')
            p.add_argument('--role', choices=ROLES)
            p.add_argument('--critical', action='store_true')
            p.add_argument('--ambiguous', action='store_true')
            p.add_argument('--resolved', action='store_true')
            p.add_argument('--failed-hypotheses', type=int, default=0)
            p.add_argument('--architect-failures', type=int, default=0)
            p.add_argument('--explicit-model')
            p.add_argument('--explicit-effort', choices=('low', 'medium', 'high', 'xhigh', 'max'))
            p.add_argument('--authorization')
        if command == 'check':
            p.add_argument('--observed', type=Path)
    p = subs.add_parser('install')
    action = p.add_mutually_exclusive_group()
    action.add_argument('--plan', '--dry-run', action='store_true', dest='dry_run')
    action.add_argument('--apply', action='store_false', dest='dry_run')
    p.set_defaults(dry_run=True)
    p.add_argument('--replace-version', action='store_true')
    p.add_argument('--approval-reference')
    p = subs.add_parser('release')
    p.add_argument('--runtime', choices=('codex', 'claude'), required=True)
    p.add_argument('--model', required=True)
    p.add_argument('--notice', required=True)
    p.add_argument('--reopen')
    for command_parser in subs.choices.values():
        command_parser.add_argument('--json', action='store_true', default=argparse.SUPPRESS)
        command_parser.add_argument('--home', type=Path, default=argparse.SUPPRESS)
    return parser


def execute(args):
    if args.command == 'install':
        result = install(args.home, args.dry_run, args.replace_version, args.approval_reference)
    elif args.command == 'release':
        result = release(args.home, args.runtime, args.model, args.notice, args.reopen)
    else:
        if args.command != 'inspect':
            selected = select(**{k: getattr(args, k) for k in (
                'runtime', 'task', 'role', 'critical', 'ambiguous', 'failed_hypotheses',
                'architect_failures', 'resolved', 'explicit_model', 'explicit_effort', 'authorization')})
        if args.command == 'select':
            result = selected
        elif args.command == 'launch':
            launch(selected, args.project, [])
            return {}, 0
        else:
            configuration = inspect(args.runtime, args.project, args.home)
            result = configuration if args.command == 'inspect' else check(
                selected, configuration, read_json(args.observed) if args.observed else None)
    code = 0
    if args.command == 'check':
        code = 1 if result['issues'] else (0 if result['observation_status'] == 'matches' else 2)
    return result, code


def main(argv=None):
    parser = add_arguments(argparse.ArgumentParser(description=__doc__))
    args = parser.parse_args(argv)
    try:
        result, code = execute(args)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if args.command == 'select':
                choice = result['recommended']
                print(f'{result["role"]}: {choice["model"]} / {choice["effort"] or "nativo"}\n'
                      f'Gatilho: {result["reason"]}\nEntregável: {result["deliverable"]}\nTroca: ainda não observada')
            else:
                print(json.dumps(result, ensure_ascii=False, indent=2))
        return code
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Avoid echoing parser errors containing file contents or secret-like values.
        message = str(exc) if isinstance(exc, ValueError) and not isinstance(exc, json.JSONDecodeError) else type(exc).__name__
        print(json.dumps({'status': 'error', 'reason': message}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
