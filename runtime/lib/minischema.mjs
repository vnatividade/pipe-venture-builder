// Validador mínimo de JSON Schema (subconjunto): type, required, properties,
// enum, items, additionalProperties, minLength, const. Suficiente para os
// contratos da fatia; substituível por validador completo sem mudar chamadas.
export function validate(schema, value, path = '$') {
  const errors = [];
  check(schema, value, path, errors);
  return { valid: errors.length === 0, errors };
}

function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

function check(schema, value, path, errors) {
  if (!schema || typeof schema !== 'object') return;
  if (schema.const !== undefined && value !== schema.const) {
    errors.push(`${path}: esperado const ${JSON.stringify(schema.const)}`);
    return;
  }
  if (schema.type) {
    const types = Array.isArray(schema.type) ? schema.type : [schema.type];
    const t = typeOf(value);
    const ok = types.some((x) => x === t || (x === 'integer' && t === 'number' && Number.isInteger(value)));
    if (!ok) { errors.push(`${path}: tipo ${t}, esperado ${types.join('|')}`); return; }
  }
  if (schema.enum && !schema.enum.includes(value)) {
    errors.push(`${path}: valor ${JSON.stringify(value)} fora do enum [${schema.enum.join(', ')}]`);
  }
  if (schema.minLength !== undefined && typeof value === 'string' && value.length < schema.minLength) {
    errors.push(`${path}: string menor que minLength ${schema.minLength}`);
  }
  if (typeOf(value) === 'object') {
    for (const req of schema.required ?? []) {
      if (!(req in value)) errors.push(`${path}.${req}: campo obrigatório ausente`);
    }
    const props = schema.properties ?? {};
    for (const [k, v] of Object.entries(value)) {
      if (props[k]) check(props[k], v, `${path}.${k}`, errors);
      else if (schema.additionalProperties === false) errors.push(`${path}.${k}: propriedade não permitida`);
    }
  }
  if (typeOf(value) === 'array' && schema.items) {
    value.forEach((item, i) => check(schema.items, item, `${path}[${i}]`, errors));
  }
}
