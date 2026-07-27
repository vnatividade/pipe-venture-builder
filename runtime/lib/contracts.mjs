// Contratos versionados: carrega os schemas de runtime/schemas/ e valida objetos
// nos pontos de criação/persistência. Falha de contrato é erro de programação —
// interrompe com mensagem clara em vez de persistir estado inválido.
import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validate } from './minischema.mjs';

const SCHEMAS_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', 'schemas');

const SCHEMAS = Object.fromEntries(
  readdirSync(SCHEMAS_DIR).filter((f) => f.endsWith('.schema.json')).map((f) => [
    f.replace('.schema.json', ''),
    JSON.parse(readFileSync(join(SCHEMAS_DIR, f), 'utf8')),
  ])
);

export function schemaNames() { return Object.keys(SCHEMAS); }

export function validateContract(name, obj) {
  const schema = SCHEMAS[name];
  if (!schema) throw new Error(`contrato desconhecido: ${name}`);
  return validate(schema, obj);
}

export function assertContract(name, obj) {
  const { valid, errors } = validateContract(name, obj);
  if (!valid) {
    const err = new Error(`violação do contrato ${name}: ${errors.slice(0, 5).join('; ')}`);
    err.code = 'CONTRACT_VIOLATION';
    err.errors = errors;
    throw err;
  }
  return obj;
}
