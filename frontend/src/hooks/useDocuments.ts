import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import type { Doc } from '../types'

const POLL_INTERVAL = 2000

/**
 * Mantem a lista de documentos em sincronia com o back.
 * Enquanto houver algum documento em andamento, faz polling a cada 2s.
 */
export function useDocuments() {
  const [documents, setDocuments] = useState<Doc[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      setDocuments(await api.listDocuments())
      setError(null)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  const pending = documents.some((doc) => doc.status === 'pending' || doc.status === 'processing')
  const refreshRef = useRef(refresh)
  refreshRef.current = refresh

  useEffect(() => {
    refreshRef.current()
  }, [])

  useEffect(() => {
    if (!pending) return
    const timer = setInterval(() => refreshRef.current(), POLL_INTERVAL)
    return () => clearInterval(timer)
  }, [pending])

  return { documents, error, loading, refresh }
}
