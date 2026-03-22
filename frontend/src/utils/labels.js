/** Rótulos em português para valores vindos da API (badges / tipos heurísticos). */

export const MATURIDADE_PT = {
  high: 'Alta',
  medium: 'Média',
  low: 'Baixa',
}

/** Tipos de dado sensível (heurística de nome de campo). */
export const TIPO_CAMPO_PT = {
  email: 'e-mail',
  phone: 'telefone',
  cpf: 'CPF',
  cnpj: 'CNPJ',
  address: 'endereço',
  cep: 'CEP',
  rg: 'RG',
  date_of_birth: 'data de nascimento',
  name: 'nome',
  ip_address: 'IP',
  credit_card: 'cartão',
}

export function labelTipoCampo(type) {
  return TIPO_CAMPO_PT[type] || type
}

export function labelMaturidade(maturity) {
  return MATURIDADE_PT[maturity] || maturity
}

/** Classe CSS: maturidade alta = bom = verde (risk-low), baixa = ruim = laranja (risk-high) */
export function maturityBadgeClass(maturity) {
  if (maturity === 'high') return 'risk-low'
  if (maturity === 'medium') return 'risk-medium'
  return 'risk-high'
}
