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

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff\u00ad"), None)
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
    "token", "tokens", "secret", "secrets", "segredo", "segredos", "senha", "senhas",
    "passwd", "apikey", "apikeys", "producao", "production", "prod", "prd",
    "billing", "invoice", "invoices", "fatura", "faturas", "cartao", "cartoes",
    "cobrar", "cobrando", "cobrado", "cobrada", "sudo", "writeset", "pypi",
})
# Tokens that a prefix below would otherwise catch but that are ordinary.
_ORDINARY = frozenset({"mergesort", "mergeable", "merger"})
# Prefixes, anchored at the start of a token.
_PREFIXES = ("credenc", "credential", "password", "merg", "deploy", "cobranc", "pagar", "pague", "pagament", "payment")
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
)
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
    r"\bpush\s+(?:-f\b|--force)",
    r"\bforce[\s-]?push",
    r"\brm\s+-rf\b",
    r"[\w.+-]+@[\w-]+\.[\w.]+",  # an e-mail address
))


def normalize(text: str) -> str:
    """NFKD without accents or zero-width characters, look-alikes mapped, casefolded."""

    decomposed = unicodedata.normalize("NFKD", text).translate(_ZERO_WIDTH)
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
    tokens = _tokens(normalized)
    for index, token in enumerate(tokens):
        if token in _WORDS:
            return True
        if token in _ORDINARY:
            continue
        if any(token.startswith(prefix) for prefix in _PREFIXES) and not _excepted(tokens, index):
            return True
    for left, right in _PAIRS:
        for index, token in enumerate(tokens):
            if not _matches(token, left):
                continue
            window = tokens[max(0, index - _WINDOW):index] + tokens[index + 1:index + 1 + _WINDOW]
            if any(_matches(item, right) for item in window):
                return True
    return False
