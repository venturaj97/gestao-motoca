export type LoginPayload = {
  email: string
  senha: string
}

export type RegisterPayload = {
  nome: string
  email: string
  senha: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export type CurrentUser = {
  id: number
  nome: string
  email: string
}
