// Feature flag da fatia vertical. Default: DESABILITADO (fail-safe, coerente com
// o modo `restricted` do repositório). Habilitado: comandos mutantes funcionam.
// Desabilitado: comandos mutantes recusam com mensagem clara; leitura funciona
// com aviso. Rollback: desligar a flag e/ou remover runtime/ e docs/venture-os/.
export function ventureOsEnabled(env = process.env) {
  const v = String(env.VENTURE_OS_ENABLED ?? '').toLowerCase();
  return v === '1' || v === 'true' || v === 'yes';
}

export function assertEnabled(env = process.env) {
  if (!ventureOsEnabled(env)) {
    const err = new Error(
      'Venture OS desabilitado (fail-safe). Exporte VENTURE_OS_ENABLED=true para usar comandos mutantes. ' +
      'Comportamento atual do pipe-venture-builder não é afetado por esta flag.'
    );
    err.code = 'FLAG_DISABLED';
    throw err;
  }
}
