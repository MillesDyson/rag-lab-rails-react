import type { Doc } from '../types'

async function parse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.error ?? `Falha na requisicao (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const api = {
  listDocuments: () => fetch('/api/v1/documents').then(parse<Doc[]>),

  uploadDocument: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return fetch('/api/v1/documents', { method: 'POST', body: form }).then(parse<Doc>)
  },

  deleteDocument: (id: number) =>
    fetch(`/api/v1/documents/${id}`, { method: 'DELETE' }).then((response) => {
      if (!response.ok) throw new Error('Nao foi possivel remover o documento')
    }),
}
