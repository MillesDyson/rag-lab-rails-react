import { useState } from 'react'
import { api } from '../api/client'
import type { SearchResult } from '../types'

export function useSearch() {
  const [result, setResult] = useState<SearchResult | null>(null)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function ask(question: string, kinds: string[]) {
    if (!question.trim()) return
    setAsking(true)
    setError(null)
    try {
      setResult(await api.search(question, kinds))
    } catch (err) {
      setError((err as Error).message)
      setResult(null)
    } finally {
      setAsking(false)
    }
  }

  return { result, asking, error, ask }
}
