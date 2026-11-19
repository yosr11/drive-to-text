import { useState } from 'react'
import { Check, Clipboard, FileText } from 'lucide-react'

function ExtractedTextViewer({ result }) {
  const [copied, setCopied] = useState(false)
  const [copyError, setCopyError] = useState(false)
  const text = result.text || ''

  async function handleCopy() {
    if (!text) return
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setCopyError(false)
      window.setTimeout(() => setCopied(false), 1800)
    } catch {
      setCopied(false)
      setCopyError(true)
    }
  }

  return (
    <section className="text-viewer" aria-label={`Extracted text from ${result.filename}`}>
      <div className="viewer-heading">
        <div className="viewer-file">
          <span className="viewer-icon"><FileText size={17} /></span>
          <span><strong>{result.filename}</strong><small>EXTRACTED TEXT</small></span>
        </div>
        <div className="viewer-actions">
          <span>{text.length.toLocaleString()} characters</span>
          <button type="button" className="copy-button" onClick={handleCopy} disabled={!text}>
            {copied ? <Check size={15} /> : <Clipboard size={15} />}
            {copied ? 'Copied' : 'Copy text'}
          </button>
        </div>
      </div>
      {copyError && <div className="copy-error" role="alert">Clipboard access failed. Select the text below and copy it manually.</div>}
      {result.status?.toLowerCase() === 'failed' && result.error && (
        <div className="result-error-message"><span>Error</span>{result.error}</div>
      )}
      <pre className={`extracted-text${!text ? ' extracted-text-empty' : ''}`}>
        {text || (result.error ? 'No text could be extracted from this file.' : 'No text was returned for this file.')}
      </pre>
    </section>
  )
}

export default ExtractedTextViewer
