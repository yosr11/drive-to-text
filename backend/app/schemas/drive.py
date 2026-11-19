
from pydantic import BaseModel, Field
from typing import List, Optional


class DriveValidateRequest(BaseModel):
    folder_url: str = Field(
        ...,
        description="Lien du dossier Google Drive"
    )


class DriveFile(BaseModel):
    id: str
    name: str
    mimeType: str
    size: Optional[str] = None


class DriveFilesResponse(BaseModel):
    folder_id: str
    folder_name: str
    total_files: int
    files: List[DriveFile]
