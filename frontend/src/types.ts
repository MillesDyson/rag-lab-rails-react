export type DocumentStatus = 'pending' | 'processing' | 'completed' | 'failed'

export type Doc = {
  id: number
  filename: string
  contentType: string
  byteSize: number
  status: DocumentStatus
  kind: string | null
  chunksCount: number | null
  charactersCount: number | null
  extractedPreview: string | null
  error: string | null
  createdAt: string
}
