import { useState } from 'react'
import { api } from '../api/client'
import type { Doc } from '../types'
import { StatusBadge } from './StatusBadge'

const KIND_ICONS: Record<string, string> = {
  video: '🎬',
  audio: '🎧',
  image: '🖼️',
  document: '📄',
  text: '📝',
}

function humanSize(bytes: number) {
  const units = ['B', 'KB', 'MB', 'GB']
  let value = bytes
  let unit = 0
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024
    unit += 1
  }
  return `${value.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`
}

type Props = {
  doc: Doc
  onChanged: () => void
}

export function DocumentRow({ doc, onChanged }: Props) {
  const [open, setOpen] = useState(false)

  async function remove() {
    await api.deleteDocument(doc.id)
    onChanged()
  }

  return (
    <li className="row">
      <div className="row__main">
        <span className="row__icon">{KIND_ICONS[doc.kind ?? ''] ?? '📦'}</span>
        <div className="row__info">
          <span className="row__name">{doc.filename}</span>
          <span className="row__meta">
            {humanSize(doc.byteSize)}
            {doc.chunksCount !== null && ` · ${doc.chunksCount} chunks`}
            {doc.charactersCount !== null && ` · ${doc.charactersCount} caracteres`}
          </span>
        </div>
        <StatusBadge status={doc.status} />
        {doc.extractedPreview && (
          <button className="link" onClick={() => setOpen(!open)}>
            {open ? 'ocultar' : 'ver texto'}
          </button>
        )}
        <button className="link link--danger" onClick={remove}>
          remover
        </button>
      </div>

      {doc.error && <p className="error">{doc.error}</p>}
      {open && doc.extractedPreview && <pre className="preview">{doc.extractedPreview}</pre>}
    </li>
  )
}
