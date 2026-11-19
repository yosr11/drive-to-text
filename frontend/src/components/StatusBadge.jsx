function StatusBadge({ status }) {
  const normalized = status?.toLowerCase()
  const label = normalized === 'done' ? 'Done' : normalized === 'failed' ? 'Failed' : status || 'Unknown'
  const className = normalized === 'done' ? 'status-done' : normalized === 'failed' ? 'status-failed' : 'status-pending'

  return <span className={`status-badge ${className}`}><span className="status-dot" />{label}</span>
}

export default StatusBadge
