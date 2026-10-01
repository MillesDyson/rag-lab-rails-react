import { useState, type FormEvent } from 'react'
import { useSearch } from '../hooks/useSearch'
import { AnswerText } from './AnswerText'
import { SourceCard } from './SourceCard'

const KINDS = [
  { value: 'video', label: '🎬 vídeo' },
  { value: 'audio', label: '🎧 áudio' },
  { value: 'image', label: '🖼️ imagem' },
  { value: 'document', label: '📄 documento' },
  { value: 'text', label: '📝 texto' },
]

export function SearchPanel() {
  const { result, asking, error, ask } = useSearch()
  const [question, setQuestion] = useState('')
  const [kinds, setKinds] = useState<string[]>([])
  const [highlighted, setHighlighted] = useState<number | null>(null)

  function toggleKind(value: string) {
    setKinds((atual) =>
      atual.includes(value) ? atual.filter((k) => k !== value) : [...atual, value]
    )
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    setHighlighted(null)
    ask(question, kinds)
  }

  return (
    <section className="search">
      <form onSubmit={submit}>
        <div className="search__row">
          <input
            className="search__input"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Pergunte alguma coisa sobre os arquivos enviados"
          />
          <button className="search__button" disabled={asking || !question.trim()}>
            {asking ? 'Buscando...' : 'Perguntar'}
          </button>
        </div>

        <div className="search__filters">
          <span className="muted">filtrar por tipo:</span>
          {KINDS.map((kind) => (
            <button
              key={kind.value}
              type="button"
              className={`chip ${kinds.includes(kind.value) ? 'chip--on' : ''}`}
              onClick={() => toggleKind(kind.value)}
            >
              {kind.label}
            </button>
          ))}
          {kinds.length > 0 && (
            <button type="button" className="link" onClick={() => setKinds([])}>
              limpar
            </button>
          )}
        </div>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <>
          <AnswerText
            text={result.answer}
            highlighted={highlighted}
            onHighlight={setHighlighted}
          />

          <h2>Fontes</h2>
          {result.sources.length === 0 ? (
            <p className="muted">Nenhum trecho correspondeu.</p>
          ) : (
            <ul className="list">
              {result.sources.map((source, index) => (
                <SourceCard
                  key={`${source.documentId}-${source.chunkIndex}`}
                  source={source}
                  number={index + 1}
                  highlighted={highlighted === index + 1}
                />
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  )
}
