import { FileSearch } from 'lucide-react'
import FileItem from './FileItem.jsx'

function FileList({ files, selectedIds, onToggleFile, onToggleAll }) {
  if (!files.length) {
    return (
      <div className="file-empty">
        <FileSearch size={22} />
        <strong>No supported files found</strong>
        <span>This folder is accessible, but it does not contain any supported PDFs or images.</span>
      </div>
    )
  }

  const supported = files.filter((file) => ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'].includes(file.mimeType))
  const allSelected = supported.length > 0 && selectedIds.length === supported.length
  const someSelected = selectedIds.length > 0 && !allSelected

  return (
    <div className="file-list">
      <div className="file-list-head">
        <label className="select-all-control">
          <input
            type="checkbox"
            checked={allSelected}
            ref={(element) => {
              if (element) element.indeterminate = someSelected
            }}
            onChange={onToggleAll}
            aria-label="Select all supported files"
            disabled={!supported.length}
          />
          <span>Select all</span>
        </label>
        <span className="file-list-caption">{selectedIds.length} of {supported.length} selected</span>
      </div>
      <div className="file-list-items">
        {files.map((file) => (
          <FileItem
            key={file.id}
            file={file}
            selected={selectedIds.includes(file.id)}
            onToggle={() => onToggleFile(file.id)}
          />
        ))}
      </div>
    </div>
  )
}

export default FileList
