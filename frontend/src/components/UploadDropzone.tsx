import { useRef, useState, type DragEvent } from 'react'
import { api } from '../api/client'

const ACCEPTED = 'video/*,audio/*,image/*,.csv,.docx,.doc,.xlsx,.pdf,.txt,.md'

type Props = {
  onUploaded: () => void
}

export function UploadDropzone({ onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function send(files: FileList | null) {
    if (!files?.length) return
    setSending(true)
    setError(null)
    try {
      for (const file of Array.from(files)) {
        await api.uploadDocument(file)
      }
      onUploaded()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSending(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault()
    setDragging(false)
    send(event.dataTransfer.files)
  }

  return (
    <div>
      <div
        className={`dropzone ${dragging ? 'dropzone--active' : ''}`}
        onDragOver={(event) => {
          event.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
      >
        <strong>{sending ? 'Enviando...' : 'Arraste arquivos aqui'}</strong>
        <small>video, audio, imagem, csv, docx, xlsx, pdf ou texto</small>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED}
          hidden
          onChange={(event) => send(event.target.files)}
        />
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
