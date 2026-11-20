function StatusBadge({ status }) {
  const normalized = status?.toLowerCase()
  const labels = {
    pending: 'Pending',
    processing: 'Processing',
    done: 'Done',
    failed: 'Failed',
  }
  const label = labels[normalized] || status || 'Unknown'
  const className = normalized === 'done'
    ? 'status-done'
    : normalized === 'failed'
      ? 'status-failed'
      : normalized === 'processing'
        ? 'status-processing'
        : 'status-pending'

  return <span className={`status-badge ${className}`}><span className="status-dot" />{label}</span>
}

export default StatusBadge
