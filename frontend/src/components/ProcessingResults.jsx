import { CheckCircle2, FileText, Hash } from 'lucide-react'
import StatusBadge from './StatusBadge.jsx'

function ProcessingResults({ batch, activeFileId, onSelectResult }) {
  const results = Array.isArray(batch.results) ? batch.results : []

  return (
    <div className="results-content">
      <div className="batch-summary">
        <div className="batch-id">
          <span className="summary-icon"><Hash size={17} /></span>
          <span><small>BATCH ID</small><strong>{batch.batch_id}</strong></span>
        </div>
        <StatusBadge status={batch.status} />
        <div className="summary-stat"><strong>{batch.total_files}</strong><span>Total files</span></div>
        <div className="summary-stat summary-success"><strong>{batch.successful_files}</strong><span>Successful</span></div>
        <div className={`summary-stat${batch.failed_files ? ' summary-failed' : ''}`}><strong>{batch.failed_files}</strong><span>Failed</span></div>
      </div>

      {results.length > 0 ? (
        <div className="result-list">
          {results.map((result) => {
            const isActive = activeFileId === result.file_id
            return (
              <button
                className={`result-row${isActive ? ' result-row-active' : ''}`}
                type="button"
                key={result.file_id}
                onClick={() => onSelectResult(result)}
                aria-expanded={isActive}
              >
                <span className={`result-file-icon${result.status?.toLowerCase() === 'failed' ? ' result-file-failed' : ''}`}>
                  {result.status?.toLowerCase() === 'done' ? <CheckCircle2 size={19} /> : <FileText size={19} />}
                </span>
                <span className="result-file-info">
                  <strong>{result.filename}</strong>
                  <span>{result.method ? `Method · ${result.method}` : result.error || 'No extraction method reported'}</span>
                </span>
                <StatusBadge status={result.status} />
                <span className="result-action">{isActive ? 'Close text' : 'View text'}</span>
              </button>
            )
          })}
        </div>
      ) : (
        <div className="file-empty result-empty"><FileText size={21} /><strong>No result details returned</strong><span>The batch response did not include any file results.</span></div>
      )}
    </div>
  )
}

export default ProcessingResults
