# Drive to Text

Drive to Text is a web application for finding PDF and image files in a publicly accessible Google Drive folder, extracting text from selected files, reviewing the results, and downloading a structured JSON export.

The project has a React/Vite frontend and a FastAPI backend. PDF text is extracted directly when available, with OCR used for scanned pages; PNG and JPEG files are processed with Tesseract OCR.

## 1. Project Overview

Connect a Google Drive folder using its share URL. The application validates that the folder is accessible, lists supported files, and lets the user select one or more files. The backend downloads only the selected files for a batch, extracts their text using the configured OCR language, and returns per-file results.

The frontend is a local development interface by default. It calls the backend at `http://localhost:8000`; it does not contain sample data or simulated processing results.

### Public demonstration folder

The public Google Drive folder used for testing and demonstration is:

https://drive.google.com/drive/folders/12U8yuf2EOL5UPj2RF4uIJ8VJSUnjI32J

It can be pasted directly into the application. Access must remain public for anyone with the link; if the folder permissions are changed or the folder is removed, validation and integration tests that use it may fail.

## 2. Features

- Validate public Google Drive folder URLs and show folder information.
- List PDF, PNG, and JPEG files with their MIME types and readable sizes.
- Select or deselect individual files, or select all supported files.
- Process one selected file or any selected subset of files.
- Choose OCR languages: English (`eng`), French (`fra`), Arabic (`ara`), or supported combinations.
- Extract embedded PDF text and use OCR for scanned PDF pages and image files.
- Show per-file status, extraction method, extracted text, and errors.
- Update batch and per-file statuses while extraction is running.
- Copy extracted text and view its character count.
- Download a JSON export for a completed batch.
- Display API errors and operation loading states in the UI.
- Provide FastAPI's interactive API documentation at `/docs`.

## 3. Architecture

```text
drive-to-text/
├── backend/
│   ├── app/
│   │   ├── api/routes/       # Drive and batch HTTP endpoints
│   │   ├── schemas/          # Pydantic request/response models
│   │   ├── services/         # Google Drive, PDF, OCR, and batch logic
│   │   ├── utils/            # Drive URL and file helpers
│   │   ├── config.py         # Environment and Google API key loading
│   │   └── main.py           # FastAPI app, CORS, and health check
│   ├── tests/                # Backend tests and test documents
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/       # Dashboard and reusable UI components
│   │   ├── services/api.js   # Axios client and API functions
│   │   ├── App.jsx           # Application workflow and state
│   │   └── index.css         # Tailwind import and UI styles
│   ├── package.json
│   └── vite.config.js
├── LICENSE                   # Project MIT license
├── LICENSES.md               # Dependency versions, licenses, and commercial use
├── LICENSE.md                # Supplementary third-party license notices
├── examples/
│   └── sample-batch.json     # Sample export from the public test Drive folder
├── .gitignore
└── requirements.txt          # Python dependency list
```

The frontend calls the backend REST API over HTTP. The backend retrieves folder metadata and file bytes from the Google Drive API, performs extraction locally, and returns batch results. The frontend and backend are separate processes; run both during local development.

## 4. Technologies Used and Their Justification

### Frontend

- **React 19**: React is used to model the interface as reusable components and to manage the application's interactive state. Hooks are particularly suited to this workflow because they track the selected folder, selected files, processing progress, displayed results, and extraction errors while keeping the code organised.
- **Vite**: Vite provides a fast development server and an optimised production build. It is a suitable fit for this focused single-page application and avoids the configuration and runtime overhead of a full-stack framework.
- **JavaScript**: JavaScript is the native language of the React ecosystem and communicates directly with browser APIs such as the clipboard and file download mechanism. It provides a simple integration point with the REST API exposed by the backend.
- **Tailwind CSS**: Tailwind is used to build a consistent, responsive interface efficiently. It provides reusable design conventions for layout, spacing, states, typography, and smaller-screen adaptations without requiring a large custom CSS framework.
- **Axios**: Axios centralises HTTP communication with FastAPI, handles JSON requests, supports connection and response errors, and makes binary Blob downloads possible for the JSON export.
- **Lucide React**: Lucide provides lightweight SVG icons that remain consistent with the interface style and can be adapted through React properties such as size and stroke width.

### Backend

- **Python**: Python is appropriate for this document-processing application because it offers a mature ecosystem for PDF libraries, image manipulation, OCR, testing, and API development.
- **FastAPI**: FastAPI provides a structured HTTP API with automatic request validation and interactive OpenAPI documentation. It was chosen for the speed of development and for the clear separation it creates between Drive operations, batch processing, and result retrieval.
- **Pydantic**: Pydantic validates request and response structures. It limits malformed data sent by the frontend and gives batch, file, and export responses a stable and predictable schema.
- **Uvicorn**: Uvicorn is an ASGI server that runs FastAPI efficiently in local development and can serve the application in a future production deployment.
- **Google Drive API v3**: The Drive API removes the need for manual file uploads. It allows the backend to validate a publicly shared folder, list the supported documents, and retrieve the bytes of only the files selected by the user.
- **PyMuPDF and pypdf**: These libraries provide complementary PDF handling. pypdf extracts text embedded in PDF pages, while PyMuPDF is used to render PDF pages as images when extraction by text alone is insufficient or a page contains scanned content.
- **Pillow**: Pillow opens, validates, and normalises PNG, JPEG, and rendered PDF images into RGB before OCR. It provides a consistent image representation and clear handling for malformed or empty images.
- **Tesseract OCR and pytesseract**: Tesseract performs local recognition of text in images and scanned PDF pages. pytesseract exposes it to Python, while configurable language data supports English, French, Arabic, and selected combinations. Local OCR avoids sending documents to an external AI or OCR service.
- **JSON**: JSON is used as the portable export format for batch metadata and per-file results. It preserves status, extraction method, extracted text, and error details in a structured form that can be downloaded, archived, or consumed by another application.
- **pytest**: pytest enables isolated tests for Drive URL handling, API routes, batch state, PDF processing, OCR integration, and JSON export. It helps verify that changes in one service do not silently break another part of the pipeline.

### Architecture rationale

React and FastAPI are separated to isolate the interactive interface from document-processing responsibilities. The frontend manages navigation and user feedback, while the backend owns Google Drive access, selected-file downloads, PDF extraction, OCR, batch state, and export generation. API credentials and Tesseract processing therefore remain on the backend and are not exposed to the browser.

This separation keeps the system understandable for a small project and allows independent evolution. For example, the extraction engine could later use a persistent queue or database, while an alternative frontend could consume the same REST API. The architecture is also local-first: it requires no third-party OCR service and can be run on a machine that has the Google API key and Tesseract installed.

## 5. Prerequisites

- Git
- Python 3.10 or newer, with `pip`
- Node.js compatible with Vite 8 (Node.js 20.19+ or 22.12+ recommended) and npm
- A Google API key with the Google Drive API enabled
- Tesseract OCR installed on the backend host, with the language data for the languages you intend to use (English, French, and/or Arabic)
- A Google Drive folder shared so that anyone with the link can view it

The Drive API key is used by the backend, not by the browser. Do not put it in a frontend environment variable or commit it to source control.

## 6. Installation

Clone the repository and enter its root directory:

```sh
git clone <repository-url>
cd drive-to-text
```

### Configure the backend

Create a Python virtual environment and install the pinned dependencies. From the repository root:

**Windows PowerShell**

```powershell
py -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

**macOS / Linux**

```sh
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Copy the example configuration and set your Google API key in `backend/.env`:

```dotenv
GOOGLE_DRIVE_API_KEY=your_google_drive_api_key
TESSERACT_CMD=
```

For PowerShell, run `Copy-Item backend\.env.example backend\.env`; on macOS/Linux, run `cp backend/.env.example backend/.env`. The example file contains no credentials.

Install Tesseract OCR separately using the package manager or installer for your operating system. Make sure the required `.traineddata` language files are installed; installing the Python `pytesseract` package alone does not install Tesseract itself or its language data.

### Configure the frontend

In a second terminal:

```sh
cd frontend
npm ci
```

The frontend defaults to the local API at `http://localhost:8000`. To use another backend address, create `frontend/.env.local`:

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

Vite environment variables are embedded in the frontend build, so this variable must not contain secrets.

## 7. Environment Variables

| Variable | Required | Used by | Description |
|---|---:|---|---|
| `GOOGLE_DRIVE_API_KEY` | Yes | Backend | Google API key used to access Google Drive API v3. Loaded from `backend/.env`. |
| `TESSERACT_CMD` | No | Backend | Full path to the Tesseract executable when it is not available on `PATH` or at the default Windows install location. |
| `VITE_API_BASE_URL` | No | Frontend | FastAPI base URL. Defaults to `http://localhost:8000`. Set in `frontend/.env.local` for local development. |

Example Windows `backend/.env`:

```dotenv
GOOGLE_DRIVE_API_KEY=your_google_drive_api_key
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

Example macOS/Linux `backend/.env`:

```dotenv
GOOGLE_DRIVE_API_KEY=your_google_drive_api_key
TESSERACT_CMD=/usr/bin/tesseract
```

`TESSERACT_CMD` is optional if Tesseract can be found on `PATH`. Keep `.env` and `.env.local` files private and out of version control.

## 8. Running the Application

Start the backend from the repository root with the Python virtual environment activated:

```sh
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://localhost:8000`. Check `http://localhost:8000/health` for the health response and `http://localhost:8000/docs` for interactive API documentation.

In a separate terminal, start the frontend:

```sh
cd frontend
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). The backend CORS configuration allows the standard localhost Vite origin on port 5173.

To create a production frontend bundle:

```sh
cd frontend
npm run build
```

The generated static assets are written to `frontend/dist/`.

## 9. API Endpoints

The default base URL is `http://localhost:8000`.

### Health check

`GET /health`

Returns the API status and a short message.

### Validate a Drive folder

`POST /api/drive/validate`

Request:

```json
{
  "folder_url": "https://drive.google.com/drive/folders/FOLDER_ID"
}
```

The response includes `valid`, `folder_id`, `folder_name`, and `message`. The URL must point to a Google Drive folder accessible to the configured API key.

### List supported files in a folder

`POST /api/drive/files`

Request body is the same as the validation endpoint. The response includes folder metadata, `total_files`, and a `files` array with `id`, `name`, `mimeType`, and optional `size`. The backend currently lists PDF, PNG, and JPEG files.

### Process selected files

`POST /api/batches`

Request:

```json
{
  "folder_url": "https://drive.google.com/drive/folders/FOLDER_ID",
  "language": "eng+fra",
  "selected_file_ids": ["FILE_ID_1"]
}
```

`selected_file_ids` is optional for backward compatibility. When supplied, it must contain at least one file ID belonging to the folder; only those files are included in the batch. When omitted, all supported files in the folder are processed. `language` defaults to `eng` and accepts the OCR language codes shown in the Features section.

The endpoint responds with HTTP `202 Accepted` and a batch whose files initially have `pending` status. Processing continues in the background. Per-file results include the Drive `file_id`, `filename`, `mime_type`, `status`, `method`, `text`, and `error`.

### Retrieve batch results

`GET /api/batches/{batch_id}`

Returns the current stored batch result using the same response shape as batch creation. Poll this endpoint while the batch or any file is `pending` or `processing`; successful files become `done`, failures become `failed`, and the batch ends as `done`.

### Export batch results

`GET /api/batches/{batch_id}/export`

Returns a JSON attachment named `batch_<batch_id>.json` with this export schema:

```json
{
  "batch_id": "batch-id",
  "status": "completed",
  "total": 1,
  "success": 1,
  "failed": 0,
  "results": [
    {
      "filename": "invoice.pdf",
      "status": "done",
      "method": "pdf_text",
      "text": "Extracted text...",
      "error": null
    }
  ]
}
```

PDF results report `pdf_text` when only the PDF parser was used and `pdf_text_ocr` when OCR was applied to scanned pages or embedded images. Image files report `ocr`. The export status is `completed` when there are no failed files and `completed_with_errors` when one or more files failed. The export result entries intentionally omit internal Drive IDs and MIME types.

## 10. Testing

Run backend tests from the `backend/` directory with the backend virtual environment activated:

```powershell
cd backend
python -m pytest tests -q
```

To run focused tests for batch processing and the export schema:

```sh
python -m pytest tests/test_batch_route.py -q
```

The batch-service integration test contacts Google Drive and may require a valid API key, network access, and its referenced public Drive folder to remain available. The committed sample export was generated from that public test folder. OCR tests that invoke Tesseract require the relevant executable and language data. Some PDF OCR tests may also depend on Tesseract.

Run frontend production compilation and linting from `frontend/`:

```sh
npm run build
npm run lint
```

## 11. Sample JSON Output

[`examples/sample-batch.json`](./examples/sample-batch.json) is a sample export generated from `OCR-LLM.pdf` in the public Drive test folder used by the backend integration test. Its `text` field is limited to an 80-character excerpt to keep the committed sample small; the application export contains the full extracted text. Review it before publishing if the test folder's contents change.

The **export endpoint** has this response shape:

```json
{
  "batch_id": "batch-001",
  "status": "completed_with_errors",
  "total": 2,
  "success": 1,
  "failed": 1,
  "results": [
    {
      "filename": "invoice.pdf",
      "status": "done",
      "method": "pdf_text",
      "text": "Invoice number: 1042",
      "error": null
    },
    {
      "filename": "photo.png",
      "status": "failed",
      "method": null,
      "text": null,
      "error": "Tesseract is not installed or could not be found."
    }
  ]
}
```

The processing and batch-retrieval endpoints use a different response schema: their counter names are `total_files`, `successful_files`, and `failed_files`, and result objects also include `file_id` and `mime_type`.

## 12. License Compliance

The project is distributed under the MIT License. See [`LICENSE`](./LICENSE) for the full text.

Third-party dependency versions, licenses, commercial-use notes, and the PyMuPDF copyleft decision are documented in [`LICENSES.md`](./LICENSES.md). Detailed inventories are in [`backend/python-licenses.md`](./backend/python-licenses.md) and [`frontend/npm-licenses.md`](./frontend/npm-licenses.md); supplementary notices are in [`LICENSE.md`](./LICENSE.md).

**Important:** This open-source POC uses PyMuPDF under its AGPL-3.0 option. It is not cleared for closed-source commercial deployment unless a separate Artifex commercial license is obtained or PyMuPDF is replaced. Tesseract OCR is Apache-2.0 licensed; Google Drive API usage is also subject to Google's applicable terms. The project's MIT license does not replace third-party licenses.

## 13. Known Limitations

- Google Drive access uses an API key and folders must be accessible to the API; this application does not implement Google OAuth or private per-user Drive authorization.
- The backend keeps batch results in process memory. They are lost when the backend restarts and are not shared across multiple backend workers.
- Batch processing is synchronous from the API caller's perspective; large folders or OCR-heavy documents can take time to finish.
- OCR quality depends on scan/image quality, installed Tesseract language data, and the selected language.
- The backend currently supports PDF, PNG, and JPEG files only.
- CORS is configured for localhost development origins. Production deployment requires configuring appropriate frontend origins and serving the frontend/backend securely.
- The application has no user accounts, persistent job queue, or long-term batch storage.

## 14. Future Improvements

- Add OAuth-based access to private Google Drive folders.
- Store batches and results in persistent storage and add background job processing.
- Add progress updates, cancellation, and retry controls for long-running batches.
- Support more document formats and configurable file-size/page limits.
- Add deployment-specific CORS, secrets management, and production hosting guidance.
- Expand automated API and frontend interaction tests.
