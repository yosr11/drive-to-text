# Third-Party Licenses

This project is licensed under the **MIT License**. See the [`LICENSE`](./LICENSE) file for the full license text.

This document lists the licenses of the third-party software and dependencies used by this project.

## 1. Backend — Python dependencies

The backend uses the following third-party packages:

| Package | License |
|---|---|
| FastAPI | MIT |
| Uvicorn | BSD-3-Clause |
| Requests | Apache-2.0 |
| PyMuPDF | GNU AGPL-3.0 or Artifex Commercial License |
| pypdf | BSD-3-Clause |
| pytesseract | Apache-2.0 |
| Pillow | MIT-CMU |
| Pydantic | MIT |
| Starlette | BSD-3-Clause |
| HTTPX | BSD-3-Clause |
| AnyIO | MIT |
| certifi | MPL-2.0 |
| charset-normalizer | MIT |
| click | BSD-3-Clause |
| httpcore | BSD-3-Clause |
| idna | BSD-3-Clause |
| opentelemetry-api | Apache-2.0 |
| packaging | Apache-2.0 OR BSD-2-Clause |
| python-dotenv | BSD-3-Clause |
| python-multipart | Apache-2.0 |
| urllib3 | MIT |
| typing-extensions | PSF-2.0 |
| typing-inspection | MIT |
| annotated-doc | MIT |
| annotated-types | MIT |
| exceptiongroup | MIT |
| h11 | MIT |
| iniconfig | MIT |
| pluggy | MIT |
| Pygments | BSD-2-Clause |
| pydantic-core | MIT |
| pytest | MIT |
| tomli | MIT |

## 2. Frontend — npm dependencies

The frontend uses the following packages:

| Package | License |
|---|---|
| React | MIT |
| React DOM | MIT |
| Vite | MIT |
| Tailwind CSS | MIT |
| Axios | MIT |
| Lucide React | ISC |
| @tailwindcss/vite | MIT |
| @vitejs/plugin-react | MIT |
| @types/react | MIT |
| @types/react-dom | MIT |
| Oxlint | MIT |
| license-checker | BSD-3-Clause |

Additional transitive dependencies are listed in [`frontend/npm-licenses.md`](./frontend/npm-licenses.md).

## 3. External software

### Tesseract OCR

Tesseract OCR is used for optical character recognition.

- License: Apache License 2.0
- Official repository: https://github.com/tesseract-ocr/tesseract

The language data files used by Tesseract (Arabic, English, French and OSD) are distributed under Apache License 2.0.

- Official repository: https://github.com/tesseract-ocr/tessdata

## 4. License notices

The licenses of third-party dependencies remain applicable to their respective components.

Their copyright notices and license conditions must be preserved when redistributing those components.

For complete dependency license information, see:

- [`backend/python-licenses.md`](./backend/python-licenses.md)
- [`frontend/npm-licenses.md`](./frontend/npm-licenses.md)

## 5. Important note

PyMuPDF is dual-licensed under GNU AGPL-3.0 or a commercial Artifex license. Its licensing terms are separate from this project's MIT License.

See: https://pymupdf.readthedocs.io/en/latest/about.html#license-and-copyright
