
import pytest
import requests

from unittest.mock import Mock

from app.services import drive_service

from app.services.drive_service import (
    get_folder_metadata,
    list_folder_files,
    download_file_content,
    DriveServiceError,
    FolderNotFoundError,
    PrivateFolderError,
    GoogleDriveAPIError,
    DriveFileNotFoundError,
)


# --------------------------------------------------
# Helper : simuler une réponse HTTP
# --------------------------------------------------

def mock_response(
    status_code=200,
    json_data=None,
    content=b"",
    text=""
):
    response = Mock()
    response.status_code = status_code
    response.ok = 200 <= status_code < 400
    response.json.return_value = json_data or {}
    response.content = content
    response.text = text
    return response


FOLDER_DATA = {
    "id": "folder-1",
    "name": "Test Folder",
    "mimeType": "application/vnd.google-apps.folder",
}


FILES = [
    {
        "id": "file-1",
        "name": "document.pdf",
        "mimeType": "application/pdf",
        "size": "1024",
    },
    {
        "id": "file-2",
        "name": "image.png",
        "mimeType": "image/png",
        "size": "2048",
    },
]


# ==================================================
# 1. TESTS get_folder_metadata()
# ==================================================

def test_get_folder_metadata_success(monkeypatch):
    response = mock_response(json_data=FOLDER_DATA)

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    result = get_folder_metadata("folder-1")

    assert result == FOLDER_DATA


def test_get_folder_metadata_not_a_folder(monkeypatch):
    response = mock_response(
        json_data={
            "id": "file-1",
            "name": "document.pdf",
            "mimeType": "application/pdf",
        }
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(DriveServiceError):
        get_folder_metadata("file-1")


def test_get_folder_metadata_not_found(monkeypatch):
    response = mock_response(
        status_code=404,
        json_data={"error": {"message": "Not found"}}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(FolderNotFoundError):
        get_folder_metadata("unknown-folder")


def test_get_folder_metadata_private_folder(monkeypatch):
    response = mock_response(
        status_code=403,
        json_data={"error": {"message": "Permission denied"}}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(PrivateFolderError):
        get_folder_metadata("private-folder")


def test_get_folder_metadata_api_error(monkeypatch):
    response = mock_response(
        status_code=500,
        json_data={"error": {"message": "Internal server error"}}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(GoogleDriveAPIError):
        get_folder_metadata("folder-1")


def test_get_folder_metadata_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.Timeout("Connection timed out")

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        raise_timeout
    )

    with pytest.raises(DriveServiceError, match="Délai dépassé"):
        get_folder_metadata("folder-1")


# ==================================================
# 2. TESTS list_folder_files()
# ==================================================

def test_list_folder_files_success(monkeypatch):
    monkeypatch.setattr(
        drive_service,
        "get_folder_metadata",
        lambda _: FOLDER_DATA
    )

    response = mock_response(
        json_data={"files": FILES}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    result = list_folder_files("folder-1")

    assert result["folder_id"] == "folder-1"
    assert result["folder_name"] == "Test Folder"
    assert result["total_files"] == 2
    assert len(result["files"]) == 2
    assert result["files"][0]["name"] == "document.pdf"


def test_list_folder_files_empty_folder(monkeypatch):
    monkeypatch.setattr(
        drive_service,
        "get_folder_metadata",
        lambda _: FOLDER_DATA
    )

    response = mock_response(json_data={"files": []})

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    result = list_folder_files("folder-1")

    assert result["total_files"] == 0
    assert result["files"] == []


def test_list_folder_files_pagination(monkeypatch):
    monkeypatch.setattr(
        drive_service,
        "get_folder_metadata",
        lambda _: FOLDER_DATA
    )

    responses = [
        mock_response(
            json_data={
                "files": [FILES[0]],
                "nextPageToken": "next-page",
            }
        ),
        mock_response(
            json_data={
                "files": [FILES[1]]
            }
        ),
    ]

    calls = []

    def fake_get(url, params, timeout):
        calls.append(params.copy())
        return responses.pop(0)

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        fake_get
    )

    result = list_folder_files("folder-1")

    assert result["total_files"] == 2
    assert len(result["files"]) == 2
    assert len(calls) == 2
    assert calls[1]["pageToken"] == "next-page"


def test_list_folder_files_api_error(monkeypatch):
    monkeypatch.setattr(
        drive_service,
        "get_folder_metadata",
        lambda _: FOLDER_DATA
    )

    response = mock_response(
        status_code=500,
        json_data={"error": {"message": "Server error"}}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(GoogleDriveAPIError):
        list_folder_files("folder-1")


def test_list_folder_files_timeout(monkeypatch):
    monkeypatch.setattr(
        drive_service,
        "get_folder_metadata",
        lambda _: FOLDER_DATA
    )

    def raise_timeout(*args, **kwargs):
        raise requests.Timeout("Connection timed out")

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        raise_timeout
    )

    with pytest.raises(DriveServiceError, match="Délai dépassé"):
        list_folder_files("folder-1")


# ==================================================
# 3. TESTS download_file_content()
# ==================================================

def test_download_file_content_success(monkeypatch):
    expected_content = b"Fake PDF content"

    response = mock_response(content=expected_content)

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    result = download_file_content("file-1")

    assert result == expected_content
    assert isinstance(result, bytes)


def test_download_file_content_not_found(monkeypatch):
    response = mock_response(
        status_code=404,
        json_data={"error": {"message": "File not found"}}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(DriveFileNotFoundError):
        download_file_content("unknown-file")


def test_download_file_content_empty(monkeypatch):
    response = mock_response(content=b"")

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(DriveServiceError, match="vide"):
        download_file_content("file-1")


def test_download_file_content_private_file(monkeypatch):
    response = mock_response(
        status_code=403,
        json_data={"error": {"message": "Permission denied"}}
    )

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        lambda *args, **kwargs: response
    )

    with pytest.raises(PrivateFolderError):
        download_file_content("private-file")


def test_download_file_content_timeout(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.Timeout("Connection timed out")

    monkeypatch.setattr(
        drive_service.requests,
        "get",
        raise_timeout
    )

    with pytest.raises(DriveServiceError, match="Délai dépassé"):
        download_file_content("file-1")
