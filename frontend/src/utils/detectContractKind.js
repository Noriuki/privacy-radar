/**
 * Detecta pelo JSON se o contrato é introspection GraphQL ou OpenAPI/Swagger.
 * @param {unknown} obj - Resultado de JSON.parse
 * @returns {'openapi' | 'graphql' | null}
 */
export function detectContractKind(obj) {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) {
    return null
  }
  const schema = obj.data?.__schema ?? obj.__schema
  if (schema && typeof schema === 'object' && Array.isArray(schema.types)) {
    return 'graphql'
  }
  if (typeof obj.openapi === 'string' || typeof obj.swagger === 'string') {
    return 'openapi'
  }
  if (obj.paths && typeof obj.paths === 'object' && !Array.isArray(obj.paths)) {
    return 'openapi'
  }
  return null
}
