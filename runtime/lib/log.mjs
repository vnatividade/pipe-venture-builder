// Logs estruturados (JSON lines em stderr). Nunca logar segredos nem conteúdo
// integral de prompts/ideias — apenas hashes, tamanhos e identificadores.
import { nowIso } from './ids.mjs';

const REDACT_KEYS = new Set(['secret', 'token', 'password', 'apiKey', 'api_key', 'authorization']);

function redact(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  const out = Array.isArray(obj) ? [] : {};
  for (const [k, v] of Object.entries(obj)) {
    out[k] = REDACT_KEYS.has(k) ? '[REDACTED]' : redact(v);
  }
  return out;
}

export function log(level, msg, fields = {}) {
  if (process.env.VENTURE_OS_LOG_SILENT === '1') return;
  const line = { ts: nowIso(), level, msg, ...redact(fields) };
  process.stderr.write(JSON.stringify(line) + '\n');
}

export const info = (msg, f) => log('info', msg, f);
export const warn = (msg, f) => log('warn', msg, f);
export const error = (msg, f) => log('error', msg, f);
