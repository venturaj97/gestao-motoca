import axios from 'axios'

export const getApiErrorMessage = (error: unknown, fallback = 'Falha ao comunicar com o servidor.') => {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail

    if (typeof detail === 'string' && detail.trim()) {
      return detail
    }

    if (Array.isArray(detail)) {
      return detail
        .map((item) => item?.msg)
        .filter(Boolean)
        .join(', ')
    }
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return fallback
}
