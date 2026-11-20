# Third-Party Licenses

The project itself is licensed under MIT; see [LICENSE](./LICENSE). This file records the versions and license choices for the main runtime and development dependencies. Versions correspond to the checked-in Python requirements and npm lockfile.

“Commercial use” below describes the dependency license only, not Google API terms, privacy obligations, or other laws. Preserve required license and copyright notices when redistributing dependencies. This is an engineering inventory, not legal advice.

## Backend — Python

| Dependency | Version | License | Closed-source commercial use | Notes |
|---|---:|---|---|---|
| FastAPI | 0.162.5 | MIT | Yes | Preserve license notice. |
| Uvicorn | 0.54.0 | BSD-3-Clause | Yes | Preserve license notice. |
| Requests | 2.34.2 | Apache-2.0 | Yes | Preserve license and any required NOTICE. |
| PyMuPDF (`pymupdf`) | 1.28.2 | GNU AGPL-3.0 **or** Artifex Commercial License | **Only with a separate Artifex commercial license** | This POC retains PyMuPDF and uses its AGPL-3.0 option for open-source use. AGPL obligations apply to the covered application; the project's MIT license does not override them. Do not use this dependency in a closed-source commercial deployment without obtaining the appropriate Artifex license or replacing PyMuPDF. |
| pypdf | 7.1.0 | BSD-3-Clause | Yes | Preserve license notice. |
| pytesseract | 0.3.13 | Apache-2.0 | Yes | Python wrapper; Tesseract executable and language data have separate notices below. |
| Pillow | 12.3.0 | MIT-CMU | Yes | Preserve license notice. |
| Pydantic | 2.14.3 | MIT | Yes | Preserve license notice. |
| python-dotenv | 1.2.4 | BSD-3-Clause | Yes | Preserve license notice. |
| python-multipart | 0.0.32 | Apache-2.0 | Yes | Preserve license and any required NOTICE. |
| pytest (development) | 9.2.0 | MIT | Yes | Test-only dependency. |

The backend's full installed dependency inventory, including transitive packages and versions, is in [backend/python-licenses.md](./backend/python-licenses.md).

## Frontend — npm

| Dependency | Version | License | Closed-source commercial use | Notes |
|---|---:|---|---|---|
| React | 19.3.1 | MIT | Yes | Preserve license notice. |
| React DOM | 19.3.1 | MIT | Yes | Preserve license notice. |
| Vite | 8.3.8 | MIT | Yes | Build tool. |
| Tailwind CSS | 4.3.5 | MIT | Yes | Build-time styling. |
| @tailwindcss/vite | 4.3.5 | MIT | Yes | Build integration. |
| Axios | 1.21.1 | MIT | Yes | Preserve license notice. |
| Lucide React | 1.76.0 | ISC | Yes | Preserve license notice. |
| @vitejs/plugin-react | 6.3.0 | MIT | Yes | Development/build dependency. |
| @types/react | 19.3.0 | MIT | Yes | Development-only type declarations. |
| @types/react-dom | 19.3.0 | MIT | Yes | Development-only type declarations. |
| Oxlint | 1.94.0 | MIT | Yes | Development-only linter. |
| license-checker | 25.0.1 | BSD-3-Clause | Yes | Development-only inventory tool. |

The complete npm dependency inventory, including transitive packages and versions, is in [frontend/npm-licenses.md](./frontend/npm-licenses.md). It includes permissively usable dependencies as well as components with additional conditions, such as MPL-2.0 packages; review each package's license before redistribution, especially if modifying and distributing an MPL-covered component.

## External tools and services

| Tool or service | Version | License / terms | Commercial use | Notes |
|---|---|---|---|---|
| Tesseract OCR | Installed separately; not pinned by this repository | Apache-2.0 | Yes | Install the executable and preserve its notices. |
| Tesseract language data (`eng`, `fra`, `ara`, OSD) | Installed separately; not pinned by this repository | Apache-2.0 | Yes | Language data is not installed by the Python wrapper. |
| Google Drive API v3 | API service; not a packaged dependency | Google API Terms of Service | Subject to Google's terms | The POC accesses only folders shared publicly; API keys must remain server-side. |

## Copyleft decision

PyMuPDF is the only direct runtime dependency in this inventory with a copyleft/commercial dual-license choice. It is retained for PDF page rendering, which the scanned-PDF OCR path needs. For this open-source proof of concept, the selected route is to comply with its AGPL-3.0 terms and make the corresponding source available. That route is **not** a claim that the application can be incorporated into a closed-source commercial product. Such use requires a separate Artifex commercial license or replacing PyMuPDF with a suitably licensed renderer and revalidating PDF rendering/OCR.

The MIT project license applies to this project's own code only. Check the actual license files and current terms of all dependencies before redistributing or deploying a product.
