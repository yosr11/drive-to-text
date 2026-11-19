import { Check, FolderOpen, LoaderCircle, Link2 } from 'lucide-react'

function DriveFolderInput({ folderUrl, onChange, onSubmit, isLoading, isConnected }) {
  return (
    <form className="folder-form" onSubmit={onSubmit}>
      <label className="input-label" htmlFor="folder-url">GOOGLE DRIVE FOLDER URL</label>
      <div className="url-input-wrap">
        <Link2 className="url-input-icon" size={18} />
        <input
          id="folder-url"
          type="text"
          inputMode="url"
          value={folderUrl}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Paste your Google Drive folder link here..."
          autoComplete="url"
          disabled={isLoading}
        />
        <button className="button button-primary validate-button" type="submit" disabled={isLoading}>
          {isLoading ? <LoaderCircle size={16} className="spin" /> : isConnected ? <Check size={16} /> : <FolderOpen size={16} />}
          {isLoading ? 'Checking…' : isConnected ? 'Connected' : 'Validate folder'}
        </button>
      </div>
      <div className="input-hint"><span className="hint-lock">↗</span> Make sure link access is set to “Anyone with the link”.</div>
    </form>
  )
}

export default DriveFolderInput
