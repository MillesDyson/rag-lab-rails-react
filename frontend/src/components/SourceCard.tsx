import { useState } from 'react'
import type { Source } from '../types'

const KIND_ICONS: Record<string, string> = {
  video: '🎬',
  audio: '🎧',
  image: '🖼️',
  document: '📄',
  text: '📝',
}

type Props = {
  source: Source
  number: number
  highlighted: boolean
}

export function SourceCard({ source, number, highlighted }: Props) {
  const [expanded, setExpanded] = useState(false)
  const longo = source.excerpt.length > 300

  return (
    <li className={`source ${highlighted ? 'source--on' : ''}`}>
      <div className="source__head">
        <span className="source__number">{number}</span>
        <span>{KIND_ICONS[source.kind] ?? '📦'}</span>
        <span className="source__name">{source.filename}</span>
        {source.missing && <span className="source__gone">documento removido</span>}
        <span className="source__meta">
          trecho {source.chunkIndex} · {source.score.toFixed(3)}
        </span>
      </div>

      <pre className="source__excerpt">
        {expanded || !longo ? source.excerpt : `${source.excerpt.slice(0, 300)}…`}
      </pre>

      {longo && (
        <button className="link" onClick={() => setExpanded(!expanded)}>
          {expanded ? 'ver menos' : 'ver trecho inteiro'}
        </button>
      )}
    </li>
  )
}
