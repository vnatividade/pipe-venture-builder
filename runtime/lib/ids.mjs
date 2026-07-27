// Identidade, slug, hash e relógio injetável (determinismo em testes).
import { createHash, randomBytes } from 'node:crypto';

let _now = () => new Date();
export function setClock(fn) { _now = fn; }
export function nowIso() { return _now().toISOString(); }

export function newId(prefix) {
  const t = Date.now().toString(36);
  const r = randomBytes(5).toString('hex');
  return `${prefix}_${t}${r}`;
}

export function slugify(name) {
  const slug = String(name).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 64);
  if (!/^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$/.test(slug)) {
    throw new Error(`slug inválido derivado de "${name}": "${slug}" (mínimo 3 caracteres alfanuméricos)`);
  }
  return slug;
}

export function sha256(content) {
  return createHash('sha256').update(content).digest('hex');
}
