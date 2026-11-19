import { FileStack } from 'lucide-react'

const statusLabels = {
  unchecked: 'API not checked',
  connected: 'API reachable',
  disconnected: 'API unavailable',
}

function Header({ apiStatus }) {
  return (
    <header className="topbar">
      <a className="brand" href="/" aria-label="Drive to Text home">
        <span className="brand-icon"><FileStack size={20} strokeWidth={1.9} /></span>
        <span className="brand-name">drive<span>to</span>text</span>
      </a>
      <p className="brand-description">Extract text from your Google Drive documents with AI-powered OCR.</p>
      <div className={`api-indicator api-${apiStatus}`}>
        <span className="api-dot" />
        {statusLabels[apiStatus]}
      </div>
    </header>
  )
}

export default Header
