import api from './client'

export async function solicitarRecuperacao(email: string): Promise<{ mensagem: string }> {
  const res = await api.post<{ mensagem: string }>('/auth/solicitar-recuperacao', { email })
  return res.data
}

export async function redefinirSenha(dados: {
  email: string
  codigo_pin: string
  nova_senha: string
}): Promise<{ mensagem: string }> {
  const res = await api.post<{ mensagem: string }>('/auth/redefinir-senha', dados)
  return res.data
}

export async function alterarSenhaLogado(dados: {
  senha_atual: string
  nova_senha: string
}): Promise<{ mensagem: string }> {
  const res = await api.put<{ mensagem: string }>('/auth/alterar-senha', dados)
  return res.data
}

export async function solicitarConfirmacaoEmail(): Promise<{ mensagem: string }> {
  const res = await api.post<{ mensagem: string }>('/auth/enviar-confirmacao-email')
  return res.data
}

export async function confirmarEmail(codigo_pin: string): Promise<{ mensagem: string }> {
  const res = await api.post<{ mensagem: string }>('/auth/confirmar-email', { codigo_pin })
  return res.data
}
