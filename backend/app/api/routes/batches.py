
from fastapi import APIRouter, HTTPException, Response

from app.schemas.batch import (
    BatchCreateRequest,
    BatchResponse,
    BatchExportResponse,
)

from app.utils.drive_url import extract_folder_id

from app.services.drive_service import (
    list_folder_files,
    DriveServiceError
)

from app.services.batch_service import (
    create_batch,
    process_batch,
    get_batch_result
)


router = APIRouter(
    prefix="/api/batches",
    tags=["Batches"]
)


# ============================================================
# POST /api/batches
# ============================================================

@router.post("", response_model=BatchResponse)
def create_and_process_batch(request: BatchCreateRequest):
    """
    Crée un batch à partir d'un dossier Google Drive,
    puis traite les fichiers individuellement.
    """

    try:
        # 1. Extraire l'identifiant du dossier
        folder_id = extract_folder_id(request.folder_url)

        # 2. Récupérer les fichiers du dossier
        folder_data = list_folder_files(folder_id)
        files = folder_data["files"]

        if request.selected_file_ids is not None:
            if not request.selected_file_ids:
                raise HTTPException(
                    status_code=400,
                    detail="Sélectionnez au moins un fichier à traiter."
                )

            requested_ids = set(request.selected_file_ids)
            available_ids = {file["id"] for file in files}
            unknown_ids = requested_ids - available_ids
            if unknown_ids:
                raise HTTPException(
                    status_code=400,
                    detail="Un ou plusieurs fichiers sélectionnés ne sont pas dans ce dossier."
                )

            files = [
                file for file in files
                if file["id"] in requested_ids
            ]

        if not files:
            raise HTTPException(
                status_code=400,
                detail="Aucun fichier supporté dans ce dossier."
            )

        # 3. Créer le batch
        batch = create_batch(files)

        # 4. Traiter les fichiers
        result = process_batch(
            batch_id=batch["batch_id"],
            language=request.language
        )

        return result

    except HTTPException:
        raise

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
# GET /api/batches/{batch_id}
# ============================================================

@router.get("/{batch_id}", response_model=BatchResponse)
def get_batch(batch_id: str):
    """
    Récupère les informations et les résultats d'un batch.
    """

    try:
        return get_batch_result(batch_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )


# ============================================================
# GET /api/batches/{batch_id}/export
# ============================================================

@router.get("/{batch_id}/export", response_model=BatchExportResponse)
def export_batch(batch_id: str, response: Response):
    """
    Exporte les résultats d'un batch au format JSON.
    """

    try:
        batch = get_batch_result(batch_id)
        response.headers["Content-Disposition"] = (
            f'attachment; filename="batch_{batch_id}.json"'
        )

        return {
            "batch_id": batch["batch_id"],
            "status": (
                "completed_with_errors"
                if batch["failed_files"] > 0
                else "completed"
            ),
            "total": batch["total_files"],
            "success": batch["successful_files"],
            "failed": batch["failed_files"],
            "results": [
                {
                    "filename": result["filename"],
                    "status": result["status"],
                    "method": result.get("method"),
                    "text": result.get("text"),
                    "error": result.get("error"),
                }
                for result in batch["results"]
            ],
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )
