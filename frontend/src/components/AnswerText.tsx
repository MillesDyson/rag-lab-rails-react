type Props = {
  text: string
  highlighted: number | null
  onHighlight: (index: number | null) => void
}

// Quebra a resposta em texto e citações [1], [2], transformando cada citação
// num botão que destaca a fonte correspondente.
export function AnswerText({ text, highlighted, onHighlight }: Props) {
  const parts = text.split(/(\[\d+\])/g)

  return (
    <p className="answer">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/)
        if (!match) return <span key={i}>{part}</span>

        const number = Number(match[1])
        return (
          <button
            key={i}
            className={`cite ${highlighted === number ? 'cite--on' : ''}`}
            onMouseEnter={() => onHighlight(number)}
            onMouseLeave={() => onHighlight(null)}
            onClick={() => onHighlight(highlighted === number ? null : number)}
          >
            {number}
          </button>
        )
      })}
    </p>
  )
}
