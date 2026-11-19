import { useMemo, useState } from 'react'
import { AlertCircle, Check, Download, FileSearch, LoaderCircle } from 'lucide-react'
import {
  createBatch,
  exportBatch,
  isApiConnectionError,
  getApiErrorMessage,
  getBatch,
  getDriveFiles,
  validateFolder,
} from './services/api.js'
import Header from './components/Header.jsx'
import DriveFolderInput from './components/DriveFolderInput.jsx'
import FileList from './components/FileList.jsx'
import ProcessingOptions from './components/ProcessingOptions.jsx'
import ProcessingResults from './components/ProcessingResults.jsx'
import ExtractedTextViewer from './components/ExtractedTextViewer.jsx'

const INITIAL_LANGUAGE = 'eng'

function isGoogleDriveFolderUrl(value) {
  const trimmed = value.trim()
  const normalized = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`

  try {
    const url = new URL(normalized)
    return (
      ['drive.google.com', 'www.drive.google.com'].includes(url.hostname) &&
      /\/folders\/[A-Za-z0-9_-]+/.test(url.pathname)
    )
  } catch {
    return false
  }
}

function App() {
  const [folderUrl, setFolderUrl] = useState('')
  const [folder, setFolder] = useState(null)
  const [files, setFiles] = useState([])
  const [selectedIds, setSelectedIds] = useState([])
  const [language, setLanguage] = useState(INITIAL_LANGUAGE)
  const [validationState, setValidationState] = useState('idle')
  const [isProcessing, setIsProcessing] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [batch, setBatch] = useState(null)
  const [activeFile, setActiveFile] = useState(null)
  const [notice, setNotice] = useState(null)
  const [apiStatus, setApiStatus] = useState('unchecked')

  const supportedFiles = useMemo(
    () => files.filter((file) => ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'].includes(file.mimeType)),
    [files],
  )
  const allFilesSelected = supportedFiles.length > 0 && selectedIds.length === supportedFiles.length
  const hasUnsupportedFiles = supportedFiles.length !== files.length
  const canProcess = selectedIds.length > 0 && !isProcessing && !isExporting

  function updateFolderUrl(value) {
    setFolderUrl(value)
    setFolder(null)
    setFiles([])
    setSelectedIds([])
    setBatch(null)
    setActiveFile(null)
    setValidationState('idle')
    setNotice(null)
  }

  async function handleValidate(event) {
    event.preventDefault()
    setNotice(null)

    if (!folderUrl.trim()) {
      setValidationState('error')
      setNotice({ type: 'error', message: 'Enter a Google Drive folder link to continue.' })
      return
    }

    if (!isGoogleDriveFolderUrl(folderUrl)) {
      setValidationState('error')
      setNotice({ type: 'error', message: 'Enter a valid Google Drive folder URL containing a folder ID.' })
      return
    }

    setValidationState('loading')
    setFolder(null)
    setFiles([])
    setSelectedIds([])
    setBatch(null)
    setActiveFile(null)

    try {
      const validatedFolder = await validateFolder(folderUrl.trim())
      if (!validatedFolder.valid) {
        throw new Error(validatedFolder.message || 'This Google Drive folder could not be validated.')
      }

      const fileResponse = await getDriveFiles(folderUrl.trim())
      setFolder({
        folder_id: validatedFolder.folder_id || fileResponse.folder_id,
        folder_name: validatedFolder.folder_name || fileResponse.folder_name,
      })
      setFiles(Array.isArray(fileResponse.files) ? fileResponse.files : [])
      setSelectedIds(
        (Array.isArray(fileResponse.files) ? fileResponse.files : [])
          .filter((file) => ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'].includes(file.mimeType))
          .map((file) => file.id),
      )
      setValidationState('success')
      setApiStatus('connected')
      setNotice({
        type: 'success',
        message: fileResponse.total_files === 0
          ? 'Folder is accessible, but it contains no supported files.'
          : `Folder connected. ${fileResponse.total_files} ${fileResponse.total_files === 1 ? 'file is' : 'files are'} ready.`,
      })
    } catch (error) {
      setValidationState('error')
      setApiStatus(isApiConnectionError(error) ? 'disconnected' : 'connected')
      setNotice({ type: 'error', message: await getApiErrorMessage(error) })
    }
  }

  function handleToggleFile(fileId) {
    setSelectedIds((current) =>
      current.includes(fileId) ? current.filter((id) => id !== fileId) : [...current, fileId],
    )
  }

  function handleToggleAll() {
    setSelectedIds(allFilesSelected ? [] : supportedFiles.map((file) => file.id))
  }

  async function handleProcess() {
    if (!folder || !canProcess) {
      return
    }

    setIsProcessing(true)
    setNotice(null)
    setBatch(null)
    setActiveFile(null)

    try {
      const createdBatch = await createBatch(folderUrl.trim(), language, selectedIds)
      setApiStatus('connected')
      try {
        const storedBatch = await getBatch(createdBatch.batch_id)
        setBatch(storedBatch)
        setNotice({ type: 'success', message: 'Processing finished. Your results are ready below.' })
      } catch (error) {
        setBatch(createdBatch)
        setNotice({
          type: 'error',
          message: `The batch was created, but its saved results could not be refreshed: ${await getApiErrorMessage(error)}`,
        })
      }
    } catch (error) {
      setApiStatus(isApiConnectionError(error) ? 'disconnected' : 'connected')
      setNotice({ type: 'error', message: await getApiErrorMessage(error) })
    } finally {
      setIsProcessing(false)
    }
  }

  async function handleExport() {
    if (!batch?.batch_id || isExporting) {
      return
    }

    setIsExporting(true)
    setNotice(null)
    try {
      const response = await exportBatch(batch.batch_id)
      const blob = response.data instanceof Blob
        ? response.data
        : new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' })
      const downloadUrl = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = downloadUrl
      anchor.download = `batch_${batch.batch_id}.json`
      document.body.appendChild(anchor)
      anchor.click()
      anchor.remove()
      window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 1000)
      setApiStatus('connected')
      setNotice({ type: 'success', message: 'Batch JSON downloaded.' })
    } catch (error) {
      setApiStatus(isApiConnectionError(error) ? 'disconnected' : 'connected')
      setNotice({ type: 'error', message: await getApiErrorMessage(error) })
    } finally {
      setIsExporting(false)
    }
  }

  function handleSelectResult(result) {
    setActiveFile((current) => current?.file_id === result.file_id ? null : result)
  }

  const noticeIcon = notice?.type === 'success' ? Check : AlertCircle
  const NoticeIcon = noticeIcon

  return (
    <div className="app-shell">
      <Header apiStatus={apiStatus} />
      <main className="main-content">
        <div className="page-intro">
          <div className="eyebrow"><span className="eyebrow-dot" /> DOCUMENT WORKSPACE</div>
          <h1>Turn your documents<br className="desktop-break" /> into <span>searchable text.</span></h1>
          <p>Connect a Drive folder, choose your language, and let your documents do the talking.</p>
        </div>

        <div className="workflow">
          <section className="panel connection-panel" aria-labelledby="connect-title">
            <div className="panel-heading">
              <div className="step-mark">01</div>
              <div>
                <h2 id="connect-title">Connect a folder</h2>
                <p>Start with a publicly accessible Google Drive folder.</p>
              </div>
            </div>
            <DriveFolderInput
              folderUrl={folderUrl}
              onChange={updateFolderUrl}
              onSubmit={handleValidate}
              isLoading={validationState === 'loading'}
              isConnected={validationState === 'success'}
            />
            {folder && (
              <div className="folder-summary">
                <span className="folder-check"><Check size={15} strokeWidth={2.5} /></span>
                <div className="folder-meta">
                  <strong>{folder.folder_name}</strong>
                  <span>Folder ID <code>{folder.folder_id}</code></span>
                </div>
                <span className="connected-tag">CONNECTED</span>
              </div>
            )}
          </section>

          {notice && (
            <div className={`notice notice-${notice.type}`} role={notice.type === 'error' ? 'alert' : 'status'}>
              <NoticeIcon size={17} />
              <span>{notice.message}</span>
            </div>
          )}

          {folder && (
            <>
              <section className="panel file-panel" aria-labelledby="files-title">
                <div className="panel-heading panel-heading-between">
                  <div className="heading-with-step">
                    <div className="step-mark">02</div>
                    <div>
                      <h2 id="files-title">Your files</h2>
                      <p>Choose the files you want to include in this batch.</p>
                    </div>
                  </div>
                  {files.length > 0 && <span className="file-total">{files.length} {files.length === 1 ? 'FILE' : 'FILES'}</span>}
                </div>
                <FileList
                  files={files}
                  selectedIds={selectedIds}
                  onToggleFile={handleToggleFile}
                  onToggleAll={handleToggleAll}
                />
              </section>

              {files.length > 0 && (
                <ProcessingOptions
                  language={language}
                  onLanguageChange={setLanguage}
                  selectedCount={selectedIds.length}
                  fileCount={supportedFiles.length}
                  hasUnsupportedFiles={hasUnsupportedFiles}
                  isProcessing={isProcessing}
                  canProcess={canProcess}
                  onProcess={handleProcess}
                />
              )}
            </>
          )}

          {isProcessing && (
            <div className="processing-banner" role="status">
              <LoaderCircle size={18} className="spin" />
              <div><strong>Processing selected files</strong><span>This may take a little while for image-heavy files.</span></div>
            </div>
          )}

          {batch && (
            <section className="results-section" aria-labelledby="results-title">
              <div className="results-heading">
                <div className="heading-with-step">
                  <div className="step-mark">04</div>
                  <div>
                    <h2 id="results-title">Processing results</h2>
                    <p>Review extracted text and download the complete JSON.</p>
                  </div>
                </div>
                <button className="button button-secondary export-button" type="button" onClick={handleExport} disabled={isExporting}>
                  {isExporting ? <LoaderCircle size={16} className="spin" /> : <Download size={16} />}
                  {isExporting ? 'Exporting…' : 'Export JSON'}
                </button>
              </div>
              <ProcessingResults
                batch={batch}
                activeFileId={activeFile?.file_id}
                onSelectResult={handleSelectResult}
              />
              {activeFile && <ExtractedTextViewer result={activeFile} />}
            </section>
          )}
        </div>

        {!folder && validationState !== 'loading' && (
          <div className="empty-workspace">
            <div className="empty-icon"><FileSearch size={21} /></div>
            <span>YOUR WORKSPACE</span>
            <p>Your files and extraction results will appear here once you connect a folder.</p>
          </div>
        )}
      </main>
      <footer className="app-footer">
        <span>DRIVE TO TEXT <span className="footer-separator">·</span> DOCUMENT EXTRACTION WORKSPACE</span>
        <span>Files stay in your Google Drive</span>
      </footer>
    </div>
  )
}

export default App
