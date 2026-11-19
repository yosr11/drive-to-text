import pytest
from fastapi import HTTPException, Response

from app.api.routes import batches
from app.schemas.batch import BatchCreateRequest


FILES = [
    {"id": "file-1", "name": "one.pdf", "mimeType": "application/pdf"},
    {"id": "file-2", "name": "two.png", "mimeType": "image/png"},
]


def configure_batch_route(monkeypatch):
    created_files = []
    monkeypatch.setattr(batches, "extract_folder_id", lambda _: "folder-1")
    monkeypatch.setattr(
        batches,
        "list_folder_files",
        lambda _: {"files": FILES},
    )

    def create_batch(files):
        created_files.extend(files)
        return {"batch_id": "batch-1"}

    monkeypatch.setattr(batches, "create_batch", create_batch)
    monkeypatch.setattr(
        batches,
        "process_batch",
        lambda batch_id, language: {
            "batch_id": batch_id,
            "status": "done",
            "total_files": len(created_files),
            "successful_files": len(created_files),
            "failed_files": 0,
            "results": [],
        },
    )
    return created_files


def test_batch_processes_only_selected_file(monkeypatch):
    created_files = configure_batch_route(monkeypatch)
    request = BatchCreateRequest(
        folder_url="https://drive.google.com/drive/folders/folder-1",
        language="fra",
        selected_file_ids=["file-2"],
    )

    result = batches.create_and_process_batch(request)

    assert [file["id"] for file in created_files] == ["file-2"]
    assert result["total_files"] == 1


def test_batch_without_selection_keeps_processing_whole_folder(monkeypatch):
    created_files = configure_batch_route(monkeypatch)
    request = BatchCreateRequest(
        folder_url="https://drive.google.com/drive/folders/folder-1",
    )

    batches.create_and_process_batch(request)

    assert [file["id"] for file in created_files] == ["file-1", "file-2"]


@pytest.mark.parametrize("selected_file_ids", [[], ["not-in-this-folder"]])
def test_batch_rejects_empty_or_unknown_selection(monkeypatch, selected_file_ids):
    configure_batch_route(monkeypatch)
    request = BatchCreateRequest(
        folder_url="https://drive.google.com/drive/folders/folder-1",
        selected_file_ids=selected_file_ids,
    )

    with pytest.raises(HTTPException) as error:
        batches.create_and_process_batch(request)

    assert error.value.status_code == 400


@pytest.mark.parametrize(
    ("failed_files", "expected_status"),
    [(0, "completed"), (1, "completed_with_errors")],
)
def test_export_returns_structured_json(monkeypatch, failed_files, expected_status):
    batch = {
        "batch_id": "batch-1",
        "status": "done",
        "total_files": 2,
        "successful_files": 2 - failed_files,
        "failed_files": failed_files,
        "results": [
            {
                "file_id": "file-1",
                "filename": "invoice.pdf",
                "mime_type": "application/pdf",
                "status": "done",
                "method": "pdf_text",
                "text": "Extracted text",
                "error": None,
            },
            {
                "file_id": "file-2",
                "filename": "photo.png",
                "mime_type": "image/png",
                "status": "failed" if failed_files else "done",
                "method": None if failed_files else "ocr",
                "text": None if failed_files else "Recognized text",
                "error": "OCR failed" if failed_files else None,
            },
        ],
    }
    monkeypatch.setattr(batches, "get_batch_result", lambda _: batch)
    response = Response()

    exported = batches.export_batch("batch-1", response)

    assert exported == {
        "batch_id": "batch-1",
        "status": expected_status,
        "total": 2,
        "success": 2 - failed_files,
        "failed": failed_files,
        "results": [
            {
                "filename": "invoice.pdf",
                "status": "done",
                "method": "pdf_text",
                "text": "Extracted text",
                "error": None,
            },
            {
                "filename": "photo.png",
                "status": "failed" if failed_files else "done",
                "method": None if failed_files else "ocr",
                "text": None if failed_files else "Recognized text",
                "error": "OCR failed" if failed_files else None,
            },
        ],
    }
    assert response.headers["Content-Disposition"] == (
        'attachment; filename="batch_batch-1.json"'
    )
