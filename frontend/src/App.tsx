import { DocumentList } from './components/DocumentList'
import { UploadDropzone } from './components/UploadDropzone'
import { useDocuments } from './hooks/useDocuments'

export default function App() {
  const { documents, loading, error, refresh } = useDocuments()

  return (
    <main className="app">
      <header className="app__header">
        <h1>RAG Lab</h1>
        <p className="muted">Ingestao de midia: extrai texto, divide em chunks e vetoriza.</p>
      </header>

      <UploadDropzone onUploaded={refresh} />

      {error && <p className="error">{error}</p>}

      <section>
        <h2>Arquivos</h2>
        <DocumentList documents={documents} loading={loading} onChanged={refresh} />
      </section>
    </main>
  )
}
