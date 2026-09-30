import type { DocumentStatus } from '../types'

const LABELS: Record<DocumentStatus, string> = {
  pending: 'Na fila',
  processing: 'Processando',
  completed: 'Pronto',
  failed: 'Falhou',
}

export function StatusBadge({ status }: { status: DocumentStatus }) {
  return <span className={`badge badge--${status}`}>{LABELS[status]}</span>
}
