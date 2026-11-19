# Drive to Text

React and Vite frontend for the Drive to Text FastAPI service.

## Requirements

- Node.js and npm
- The FastAPI backend running at `http://localhost:8000` (or a configured API URL)

## Install and run

```sh
npm install
npm run dev
```

Vite prints the local development URL after startup (by default, `http://localhost:5173`).

To use a different backend address, set `VITE_API_BASE_URL` in `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

The variable is optional; the default is `http://localhost:8000`.

## API integration

`src/services/api.js` owns the Axios client and communicates with the FastAPI endpoints to validate a Drive folder, list its files, create a batch, retrieve batch results, and download the JSON export. Batch creation sends the selected file IDs; the API processes only those files. For backward compatibility, requests that omit `selected_file_ids` still process the entire folder.

The export endpoint returns a download-ready JSON object with `batch_id`, the overall `status`, `total`, `success`, `failed`, and per-file `filename`, `status`, `method`, `text`, and `error` fields.

The page can be built with `npm run build`.
