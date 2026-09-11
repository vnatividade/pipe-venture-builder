"""Deterministic guard for the delegated responder (PIP-906).

Whatever the responder model says, a worker blocker or a responder instruction
that touches something only the founder decides is never answered on the
founder's behalf: credentials and secrets, merge/push to the main line,
production/deploy/release, billing and payment, communication with customers,
and the repository's own governance surface (AGENTS.md, CLAUDE.md, the
operating mode, approval gates, the mission's write set or scope).

This is defence in depth, not the only barrier: the worker that would act on an
answer has no tool for merge, deploy, billing or messaging, and its diff is
checked against the write set before anything is committed. The guard exists so
that such a *question* still reaches the founder.

How it matches (two adversarial reviews of the first versions showed a
substring check on ``lower()`` lets inflections through and also blocks most
ordinary technical questions):

- Normalize: NFKD, drop combining marks (accents) and zero-width characters,
  map common Cyrillic look-alikes to Latin, casefold.
- Tokenize on anything that is not a letter or digit, so ``STRIPE_API_KEY`` is
  ``stripe api key`` and ``e-mail`` is ``e mail``. Tokens that mix letters and
  digits also get a leet-speak reading (``t0ken`` -> ``token``), and runs of
  three or more single-letter tokens are joined (``t o k e n`` -> ``token``).
- Match whole tokens, prefixes anchored at the start of a token (``merg``
  matches ``mergear`` but ``cobr`` never matches ``descobrir``), token pairs
  within a short window (``chave ... api``, ``e-mail ... cliente``), and a few
  path/command patterns on the normalized text (``.env``, ``~/.ssh``,
  ``id_rsa``, ``push -f``).

Known, accepted gaps: base64 or otherwise encoded text, and deliberately
misspelled words outside the look-alike and leet mappings. Known, accepted false
positives (it fails closed): "produção"/"prod"/"deploy" used for something other
than the production environment, and any mention of payment ("módulo de
pagamento") — in a Pipe mission a payment question is plausibly the founder's.
"""

from __future__ import annotations

import re
import unicodedata

# Every invisible/format character, not a fixed list: zero-width spaces and
# joiners, invisible operators (U+2061..U+2064), the Mongolian vowel separator,
# bidi overrides, soft hyphen, and C0/C1 controls (PIP-906 review 4, achado 10).
_ZERO_WIDTH = {
    code: None
    for code in range(0x110000)
    if unicodedata.category(chr(code)) in {"Cf", "Cc"} or chr(code) in "\u180e\u00ad"
}
# Lower-case Cyrillic letters that render like Latin ones (after casefold).
_LOOKALIKES = str.maketrans({
    "а": "a", "в": "b", "е": "e", "к": "k", "м": "m", "н": "h", "о": "o", "р": "p",
    "с": "c", "т": "t", "у": "y", "х": "x", "і": "i", "ј": "j", "ѕ": "s", "һ": "h",
    "ԁ": "d", "ԛ": "q", "ԝ": "w",
})
_LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
_TOKEN_RE = re.compile(r"[a-z0-9@$]+")

# Whole tokens that are sensitive on their own.
_WORDS = frozenset({
    # credentials and secrets
    "token", "tokens", "secret", "secrets", "segredo", "segredos", "senha", "senhas",
    "passwd", "apikey", "apikeys", "creds", "cred", "vaultwarden", "bitwarden", "1password",
    "lastpass", "keychain", "vault",
    # production and release
    "producao", "production", "prod", "prd", "produtivo", "produtiva", "staging",
    # billing and pricing
    "billing", "invoice", "invoices", "fatura", "faturas", "cartao", "cartoes",
    "cobrar", "cobrando", "cobrado", "cobrada", "cobra", "cobro", "boleto", "boletos", "pix",
    "pago", "paga", "pagos", "pagas", "preco", "precos", "price", "prices", "pricing",
    # customers' data and communication
    "cpf", "cpfs", "cnpj", "pii", "lgpd", "gdpr", "newsletter", "newsletters", "intercom",
    "zendesk", "hubspot", "mailchimp", "sendgrid", "twilio",
    # release and operations
    "hotfix", "canary", "rollout", "dns", "cloudflare", "testflight",
    # credentials (other shapes)
    "passphrase", "bearer", "keystore", "truststore", "p12", "pem", "jks", "netrc",
    # billing (other shapes)
    "reembolso", "reembolsos", "cupom", "cupons", "fiscal",
    # governance
    "sudo", "writeset", "pypi", "exploration",
})
# Tokens that a prefix below would otherwise catch but that are ordinary.
_ORDINARY = frozenset({"mergesort", "mergeable", "merger"})
# Prefixes, anchored at the start of a token.
_PREFIXES = (
    "credenc", "credential", "password", "merg", "deploy", "cobranc", "pagar", "pague",
    "pagament", "payment", "refund", "estorn", "rotacion", "rotate",
)
# Pairs of token stems that must both appear within ``_WINDOW`` tokens of each
# other. A stem ending in ``*`` matches by prefix; any other stem matches the
# whole token only (so ``pat`` never matches ``path`` and ``mode`` never
# matches ``model``).
_WINDOW = 4
_CUSTOMER = ("client*", "customer*", "usuario*", "user", "users", "contato*", "lead", "leads")
_MESSAGE = ("email*", "mail", "mails", "mensag*", "message*", "slack", "whatsapp", "sms", "telegram", "dm", "dms")
_PAIRS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("api",), ("key", "keys", "chave*")),
    (("chave*",), ("api", "ssh", "privada*", "acesso", "secreta*")),
    (("private", "access", "ssh", "secret"), ("key", "keys")),
    (("pat", "pats"), ("github", "gh")),
    (("agents", "claude"), ("md",)),
    (("pipe",), ("mode",)),
    (("operating",), ("modes", "mode")),
    (("approval",), ("gates", "gate")),
    (("settings",), ("json",)),
    (("write",), ("set",)),
    (("go",), ("live",)),
    (("railway",), ("up",)),
    (("release*", "lancar", "lancamento*", "publicar"), _CUSTOMER + ("pypi", "npm", "producao", "production")),
    (("charge*",), ("card", "cards", "customer*", "client*")),
    (("push",), ("main", "master", "force")),
    (("mesclar", "aprovar", "aprove", "approve"), ("pr", "prs", "pull", "request")),
    (("reservado*",), ("fundador", "founder", "humano")),
    (("escopo", "scope"), ("fora", "sair", "mudar", "ampliar", "alterar", "expand*", "change*", "outside")),
    (_MESSAGE, _CUSTOMER),
    (("cobre",), _CUSTOMER),
    (("stripe", "openai", "anthropic", "aws", "github", "railway", "supabase", "gcp", "azure", "vercel"),
     ("key", "keys", "chave*", "token*", "secret*", "cred*", "credenc*", "senha*", "password*", "conta", "account")),
    (("vw",), ("get", "list", "item", "unlock")),
    (("live",), ("db", "database", "banco", "ship*", "go", "ambiente", "environment", "env", "site", "server",
                  "servidor", "users", "usuarios", "migration*", "migrac*")),
    (("lanc*",), ("versao", "release", "app", "usuario*", "user", "users", "client*", "producao", "loja",
                            "store", "beta")),
    (("publish*", "publica*", "publicar"), ("npm", "pypi", "store", "play", "app", "loja", "pacote", "package",
                                             "versao", "release", "twitter", "linkedin", "instagram", "blog")),
    (("posta*", "post", "tweet*", "anuncia*", "announce*"), ("twitter", "linkedin", "instagram", "facebook",
                                                             "tiktok", "blog", "anuncio", "announcement")),
    (("dump*", "export*", "exporta*", "copia*", "copy", "baixa*", "download*"),
     ("client*", "customer*", "usuario*", "user", "users", "producao", "production", "prod")),
    (("recarreg*", "recharge", "top"), ("credito*", "credit*", "saldo", "balance")),
    (("modo", "mode"), ("repositorio", "repo", "repository", "exploration", "restricted", "pipe")),
    (("mudar", "muda", "trocar", "troca", "change", "bump", "aumenta*", "reduz*"), ("preco*", "price*", "plano", "plan")),
    (("rebase", "reset", "force", "mescla*", "merge*", "pr", "integra*"), ("main", "master")),
    (("pat", "pats"), ("gera*", "novo", "nova", "escopo", "scope", "generate*", "create*")),
    (("dump*",), ("postgres*", "mysql", "banco", "database", "db", "rds", "supabase", "railway")),
    (("push",), ("notification*", "notificac*")),
    (("dados", "tabela", "registros", "linhas", "rows"), ("cliente*", "customer*", "usuario*", "producao",
                                                          "production", "prod", "reais", "real")),
    (("apaga*", "deleta*", "delete*", "remove*", "drop*", "truncate*"), ("banco", "database", "db", "tabela",
                                                                          "producao", "production", "prod", "rds")),
    (("reembols*", "estorna*"), ("cliente*", "customer*", "valor", "pagamento*", "cobranc*")),
    (("feature",), ("flag", "flags")),
    (("claim*", "afirma*", "promete*"), ("cliente*", "customer*", "juridic*", "legal", "compliance")),
    (("reais", "real", "verdadeiros"), ("cpf*", "cliente*", "customer*", "dados", "data")),
)
# A message word and a customer word anywhere in the same text (no window):
# "envie o e-mail de desculpas para todos os clientes afetados".
_MESSAGE_VERBS = (
    "avis*", "notif*", "comunica*", "responde*", "respond*", "reply*", "contact*", "contat*",
    "envia*", "envie", "send*", "manda*", "mande", "liga*", "telefon*",
)
# Customers for the whole-text rule: business words only ("client"/"user" are
# ordinary in code — an HTTP client, a user model — so they need the window).
_BUSINESS_CUSTOMER = ("cliente*", "customer*", "usuario*", "contato*", "lead", "leads", "assinante*", "subscriber*")
# Token pairs that make an otherwise sensitive token ordinary.
_EXCEPTIONS = ((("merg*",), ("sort", "base", "conflict*")),)
# Environment-variable-looking credential names, matched on the original case
# so ``cache_key``/``primary_key`` stay ordinary: ANTHROPIC_KEY, GH_TOKEN.
_ENV_NAME_RE = re.compile(r"\b[A-Z][A-Z0-9]*_(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|PAT)S?\b")
# Patterns on the normalized, lower-cased text (separators kept).
_TEXT_PATTERNS = tuple(re.compile(pattern) for pattern in (
    r"(?:^|[\s/~'\"`(])\.env(?:\b|\.)",  # .env, .env.local — not .venv
    r"\.ssh\b",
    r"\bid_(?:rsa|ed25519|ecdsa|dsa)\b",
    r"\bsecrets?/",
    r"\.(?:netrc|npmrc|pypirc)\b",
    r"\.aws\b",
    r"\.config/gh\b",
    r"~/\.claude\b",
    r"\.claude/settings",
    r"\.pipe/mode\.json",
    r"(?<![\w-])mode\.json\b",
    r"\bdatabase_url\b",
    r"\bconnection string\b",
    r"(?:^|[\s/~'\"`(])\.pipe\b",
    r"\bsk_(?:live|test)",
    r"\b(?:no|pro|para o|ao) ar\b",
    r"\bnpm\s+publish\b",
    r"\bgit\s+reset\s+--hard\s+origin",
    r"\bpush\s+(?:-f\b|--force)",
    r"\bforce[\s-]?push",
    r"\brm\s+-rf\b",
    r"[\w.+-]+@[\w-]+\.[\w.]+",  # an e-mail address
))


# camelCase starting in lower case is split (``stripeSecretKey``); PascalCase
# proper nouns (``GitHub``, ``PyPI``, ``WhatsApp``) are left whole.
_CAMEL_WORD_RE = re.compile(r"\b[a-z][a-z0-9]*[A-Z][A-Za-z0-9]*\b")
_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
# Code identifiers (snake_case, camelCase, PascalCase). One that carries a
# technical affix is code, not a request — ``token_count``, ``merge_dicts``,
# ``hash_password``, ``user_message``, ``DeployPlan`` — so its words are left
# out of the token rules; one without an affix still counts
# (``stripeSecretKey``, ``dbPassword``, ``stripe_key``). Dotted file names are
# not identifiers here, so ``AGENTS.md``/``mode.json`` keep matching.
_IDENT_RE = re.compile(
    r"\b_*[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b"
    r"|\b[a-z]+(?:[A-Z][a-z0-9]*)+\b"
    r"|\b[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+\b"
)
_TECH_AFFIXES = frozenset({
    "count", "counts", "dict", "dicts", "util", "utils", "config", "cfg", "helper", "helpers",
    "plan", "plans", "message", "messages", "msg", "hash", "hashed", "hasher", "test", "tests",
    "mask", "masked", "field", "fields", "fixture", "fixtures", "schema", "model", "models",
    "parser", "lexer", "id", "ids", "type", "types", "validator", "validate", "stub", "mock",
    "fake", "len", "length", "size", "limit", "regex", "pattern", "format", "fmt", "sort",
    "strategy", "decision", "lowercased", "normalize", "normalized",
})


# A credential word inside an identifier is never exempt: ``STRIPE_SECRET_KEY_TEST``
# and ``github_token_config`` are requests, not code (PIP-906 review 4, achado 3).
_NEVER_EXEMPT = frozenset({
    "key", "keys", "token", "tokens", "secret", "secrets", "password", "passwords", "passwd",
    "senha", "senhas", "creds", "cred", "pat", "credential", "credentials", "apikey", "sk",
})


def _technical_identifier(identifier: str) -> bool:
    parts = [part.casefold() for part in re.split(r"_+|(?<=[a-z0-9])(?=[A-Z])", identifier) if part]
    if any(part in _NEVER_EXEMPT for part in parts):
        return False
    return "".join(parts) == "writeset" or any(part in _TECH_AFFIXES for part in parts)


def normalize(text: str) -> str:
    """NFKD without accents or zero-width characters, camelCase split
    (``stripeSecretKey`` -> ``stripe Secret Key``), look-alikes mapped, casefolded."""

    decomposed = _CAMEL_WORD_RE.sub(
        lambda match: _CAMEL_RE.sub(" ", match.group()),
        unicodedata.normalize("NFKD", text).translate(_ZERO_WIDTH),
    )
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.casefold().translate(_LOOKALIKES)


def _tokens(normalized: str) -> list[str]:
    raw = _TOKEN_RE.findall(normalized)
    tokens: list[str] = []
    run: list[str] = []
    for token in raw + [""]:
        if len(token) == 1 and token.isalpha():
            run.append(token)
            continue
        if len(run) >= 3:
            tokens.append("".join(run))
        tokens.extend(run)
        run = []
        if token:
            tokens.append(token)
            if any(ch.isdigit() or ch in "@$" for ch in token) and any(ch.isalpha() for ch in token):
                tokens.append(token.translate(_LEET))
    return tokens


def _matches(token: str, stems: tuple[str, ...]) -> bool:
    return any(token.startswith(stem[:-1]) if stem.endswith("*") else token == stem for stem in stems)


def _excepted(tokens: list[str], index: int) -> bool:
    following = tokens[index + 1:index + 3]
    return any(
        _matches(tokens[index], heads) and any(_matches(item, tails) for item in following)
        for heads, tails in _EXCEPTIONS
    )


def contains_sensitive_terms(text: str) -> bool:
    """True when ``text`` touches something only the founder decides (see module docstring)."""

    if _ENV_NAME_RE.search(unicodedata.normalize("NFKD", text).translate(_ZERO_WIDTH)):
        return True
    normalized = normalize(text)
    if any(pattern.search(normalized) for pattern in _TEXT_PATTERNS):
        return True
    words = _IDENT_RE.sub(
        lambda match: " " if _technical_identifier(match.group()) else match.group(),
        unicodedata.normalize("NFKD", text).translate(_ZERO_WIDTH),
    )
    tokens = _tokens(normalize(words))
    for index, token in enumerate(tokens):
        if token in _WORDS:
            return True
        if token in _ORDINARY:
            continue
        if any(token.startswith(prefix) for prefix in _PREFIXES) and not _excepted(tokens, index):
            return True
    if any(_matches(token, _MESSAGE + _MESSAGE_VERBS) for token in tokens) and any(
        _matches(token, _BUSINESS_CUSTOMER) for token in tokens
    ):
        return True
    for left, right in _PAIRS:
        for index, token in enumerate(tokens):
            if not _matches(token, left):
                continue
            window = tokens[max(0, index - _WINDOW):index] + tokens[index + 1:index + 1 + _WINDOW]
            if any(_matches(item, right) for item in window):
                return True
    return False
