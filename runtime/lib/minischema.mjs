// Validador de JSON Schema (subconjunto ampliado na fatia 2): type, required,
// properties, enum, items, additionalProperties, minLength, const, e agora
// $ref local (#/...), allOf, oneOf, anyOf, pattern, minItems, uniqueItems e
// format (date/date-time). Cobre integralmente os schemas da fatia E o
// ProductBaseline.schema.json canônico (paridade com o validador Python
// jsonschema verificada em teste). Não é um validador JSON Schema completo.
export function validate(schema, value, path = '$', root = schema) {
  const errors = [];
  check(schema, value, path, errors, root);
  return { valid: errors.length === 0, errors };
}

function typeOf(v) {
  if (v === null) return 'null';
  if (Array.isArray(v)) return 'array';
  return typeof v;
}

function resolveRef(ref, root) {
  if (!ref.startsWith('#')) throw new Error(`apenas $ref locais são suportados: ${ref}`);
  let node = root;
  for (const part of ref.slice(1).split('/').filter(Boolean)) {
    node = node?.[part.replace(/~1/g, '/').replace(/~0/g, '~')];
    if (node === undefined) throw new Error(`$ref não resolvido: ${ref}`);
  }
  return node;
}

const DATE_RE = /^\d{4}-\d{2}-\d{2}$/;
const DATETIME_RE = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$/;

function check(schema, value, path, errors, root) {
  if (schema === true) return;
  if (schema === false) { errors.push(`${path}: schema false`); return; }
  if (!schema || typeof schema !== 'object') return;

  if (schema.$ref) {
    check(resolveRef(schema.$ref, root), value, path, errors, root);
    const { $ref, ...rest } = schema;
    if (Object.keys(rest).length > 0) check(rest, value, path, errors, root);
    return;
  }
  if (schema.allOf) for (const sub of schema.allOf) check(sub, value, path, errors, root);
  if (schema.oneOf) {
    const passing = schema.oneOf.filter((sub) => validate(sub, value, path, root).valid).length;
    if (passing !== 1) errors.push(`${path}: oneOf esperava exatamente 1 schema válido, obteve ${passing}`);
  }
  if (schema.anyOf) {
    const ok = schema.anyOf.some((sub) => validate(sub, value, path, root).valid);
    if (!ok) errors.push(`${path}: nenhum schema de anyOf válido`);
  }
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
  if (typeof value === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength) {
      errors.push(`${path}: string menor que minLength ${schema.minLength}`);
    }
    if (schema.pattern !== undefined && !new RegExp(schema.pattern).test(value)) {
      errors.push(`${path}: não casa com pattern ${schema.pattern}`);
    }
    if (schema.format === 'date' && !DATE_RE.test(value)) errors.push(`${path}: formato date inválido`);
    if (schema.format === 'date-time' && !DATETIME_RE.test(value)) errors.push(`${path}: formato date-time inválido`);
  }
  if (typeOf(value) === 'object') {
    for (const req of schema.required ?? []) {
      if (!(req in value)) errors.push(`${path}.${req}: campo obrigatório ausente`);
    }
    const props = schema.properties ?? {};
    for (const [k, v] of Object.entries(value)) {
      if (props[k]) check(props[k], v, `${path}.${k}`, errors, root);
      else if (schema.additionalProperties === false) errors.push(`${path}.${k}: propriedade não permitida`);
      else if (schema.additionalProperties && typeof schema.additionalProperties === 'object') {
        check(schema.additionalProperties, v, `${path}.${k}`, errors, root);
      }
    }
  }
  if (typeOf(value) === 'array') {
    if (schema.minItems !== undefined && value.length < schema.minItems) {
      errors.push(`${path}: menos itens que minItems ${schema.minItems}`);
    }
    if (schema.uniqueItems) {
      const seen = new Set(value.map((x) => JSON.stringify(x)));
      if (seen.size !== value.length) errors.push(`${path}: itens duplicados (uniqueItems)`);
    }
    if (schema.items) value.forEach((item, i) => check(schema.items, item, `${path}[${i}]`, errors, root));
  }
}
