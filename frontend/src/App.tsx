import { useState } from 'react'
import { DocumentList } from './components/DocumentList'
import { SearchPanel } from './components/SearchPanel'
import { UploadDropzone } from './components/UploadDropzone'
import { useDocuments } from './hooks/useDocuments'

type Aba = 'ingestao' | 'consulta'

export default function App() {
  const [aba, setAba] = useState<Aba>('ingestao')
  const { documents, loading, error, refresh } = useDocuments()

  return (
    <main className="app">
      <header className="app__header">
        <h1>RAG Lab</h1>
        <nav className="tabs">
          <button
            className={`tab ${aba === 'ingestao' ? 'tab--on' : ''}`}
            onClick={() => setAba('ingestao')}
          >
            Ingestão
          </button>
          <button
            className={`tab ${aba === 'consulta' ? 'tab--on' : ''}`}
            onClick={() => setAba('consulta')}
          >
            Consulta
          </button>
        </nav>
      </header>

      {aba === 'ingestao' ? (
        <>
          <UploadDropzone onUploaded={refresh} />
          {error && <p className="error">{error}</p>}
          <section>
            <h2>Arquivos</h2>
            <DocumentList documents={documents} loading={loading} onChanged={refresh} />
          </section>
        </>
      ) : (
        <SearchPanel />
      )}
    </main>
  )
}
