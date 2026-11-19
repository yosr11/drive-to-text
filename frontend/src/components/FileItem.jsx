import { FileImage, FileText } from 'lucide-react'

const supportedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg']

function formatFileSize(size) {
  if (size === null || size === undefined || size === '') return 'Size unavailable'
  const bytes = Number(size)
  if (!Number.isFinite(bytes) || bytes < 0) return 'Size unavailable'
  if (bytes < 1024) return `${bytes} B`
  const units = ['KB', 'MB', 'GB', 'TB']
  let value = bytes / 1024
  let unitIndex = 0
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unitIndex]}`
}

function getFileType(file) {
  if (file.mimeType === 'application/pdf') return 'PDF'
  if (file.mimeType === 'image/png') return 'PNG image'
  if (['image/jpeg', 'image/jpg'].includes(file.mimeType)) return 'JPEG image'
  return 'Unsupported file'
}

function FileItem({ file, selected, onToggle }) {
  const isImage = file.mimeType?.startsWith('image/')
  const Icon = isImage ? FileImage : FileText
  const supported = supportedTypes.includes(file.mimeType)

  return (
    <label className={`file-item${selected ? ' file-item-selected' : ''}${!supported ? ' file-item-unsupported' : ''}`}>
      <input type="checkbox" checked={selected} onChange={onToggle} disabled={!supported} />
      <span className={`file-type-icon${isImage ? ' image-icon' : ''}`}><Icon size={19} /></span>
      <span className="file-name">{file.name}</span>
      <span className={`file-type-pill${!supported ? ' unsupported-pill' : ''}`}>{getFileType(file)}</span>
      <span className="file-size">{formatFileSize(file.size)}</span>
    </label>
  )
}

export default FileItem
