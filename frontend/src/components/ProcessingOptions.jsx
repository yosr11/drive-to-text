import { AlertTriangle, FileCheck2, LoaderCircle, Play } from 'lucide-react'

const languages = [
  ['eng', 'English'],
  ['fra', 'French'],
  ['ara', 'Arabic'],
  ['eng+fra', 'English + French'],
  ['eng+ara', 'English + Arabic'],
  ['fra+ara', 'French + Arabic'],
  ['eng+fra+ara', 'English + French + Arabic'],
]

function ProcessingOptions({
  language,
  onLanguageChange,
  selectedCount,
  fileCount,
  hasUnsupportedFiles,
  isProcessing,
  canProcess,
  onProcess,
}) {
  return (
    <section className="panel options-panel" aria-labelledby="options-title">
      <div className="panel-heading panel-heading-between">
        <div className="heading-with-step">
          <div className="step-mark">03</div>
          <div>
            <h2 id="options-title">Processing options</h2>
            <p>Choose OCR languages and start text extraction.</p>
          </div>
        </div>
        <div className="selected-count"><FileCheck2 size={15} /> {selectedCount} of {fileCount} selected</div>
      </div>

      <div className="options-controls">
        <label className="language-control">
          <span className="input-label">DOCUMENT LANGUAGE</span>
          <select value={language} onChange={(event) => onLanguageChange(event.target.value)} disabled={isProcessing}>
            {languages.map(([value, label]) => <option value={value} key={value}>{label}</option>)}
          </select>
        </label>
        <button className="button button-primary process-button" type="button" onClick={onProcess} disabled={!canProcess}>
          {isProcessing ? <LoaderCircle size={16} className="spin" /> : <Play size={16} fill="currentColor" />}
          {isProcessing ? 'Processing folder…' : 'Process selected files'}
        </button>
      </div>

      <div className={`backend-limitation${hasUnsupportedFiles ? ' limitation-warning' : ''}`}>
        <AlertTriangle size={16} />
        <span>
          <strong>Selection:</strong> Only the {selectedCount === 1 ? 'selected file' : 'selected files'} will be processed.
          {hasUnsupportedFiles && ' Unsupported files cannot be processed by this workflow.'}
        </span>
      </div>
    </section>
  )
}

export default ProcessingOptions
