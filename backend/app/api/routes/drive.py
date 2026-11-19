
from fastapi import APIRouter, HTTPException

from app.schemas.drive import (
    DriveValidateRequest,
    DriveFilesResponse
)

from app.utils.drive_url import extract_folder_id

from app.services.drive_service import (
    get_folder_metadata,
    list_folder_files,
    DriveServiceError
)


router = APIRouter(
    prefix="/api/drive",
    tags=["Google Drive"]
)


# ============================================================
# POST /api/drive/validate
# ============================================================

@router.post("/validate")
def validate_drive_folder(request: DriveValidateRequest):
    """
    Vérifie le lien Google Drive et l'accessibilité du dossier.
    """

    try:
        folder_id = extract_folder_id(request.folder_url)

        folder_metadata = get_folder_metadata(folder_id)

        return {
            "valid": True,
            "folder_id": folder_id,
            "folder_name": folder_metadata["name"],
            "message": "Google Drive folder is accessible."
        }

    except DriveServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )


# ============================================================
# POST /api/drive/files
# ============================================================

@router.post("/files", response_model=DriveFilesResponse)
def get_drive_files(request: DriveValidateRequest):
    """
    Récupère la liste des fichiers supportés
    présents dans le dossier Google Drive.
    """

    try:
        folder_id = extract_folder_id(request.folder_url)

        files_data = list_folder_files(folder_id)

        return files_data

    except DriveServiceError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )
