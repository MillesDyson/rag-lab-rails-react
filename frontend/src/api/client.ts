import type { Doc, SearchResult } from '../types'

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

  search: (question: string, kinds: string[]) =>
    fetch('/api/v1/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, k: 5, kinds }),
    }).then(parse<SearchResult>),

  fetchText: (id: number) =>
    fetch(`/api/v1/documents/${id}/text`).then(parse<{ text: string | null }>),

  deleteDocument: (id: number) =>
    fetch(`/api/v1/documents/${id}`, { method: 'DELETE' }).then((response) => {
      if (!response.ok) throw new Error('Nao foi possivel remover o documento')
    }),
}
