import type { Doc } from '../types'
import { DocumentRow } from './DocumentRow'

type Props = {
  documents: Doc[]
  loading: boolean
  onChanged: () => void
}

export function DocumentList({ documents, loading, onChanged }: Props) {
  if (loading) return <p className="muted">Carregando...</p>
  if (documents.length === 0) return <p className="muted">Nenhum arquivo enviado ainda.</p>

  return (
    <ul className="list">
      {documents.map((doc) => (
        <DocumentRow key={doc.id} doc={doc} onChanged={onChanged} />
      ))}
    </ul>
  )
}
