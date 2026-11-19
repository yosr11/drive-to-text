
from pydantic import BaseModel
from typing import List, Optional


class BatchCreateRequest(BaseModel):
    folder_url: str
    language: str = "eng"
    selected_file_ids: Optional[List[str]] = None


class BatchFileResult(BaseModel):
    file_id: str
    filename: str
    mime_type: Optional[str] = None
    status: str
    method: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None


class BatchResponse(BaseModel):
    batch_id: str
    status: str
    total_files: int
    successful_files: int
    failed_files: int
    results: List[BatchFileResult]


class BatchExportFileResult(BaseModel):
    filename: str
    status: str
    method: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None


class BatchExportResponse(BaseModel):
    batch_id: str
    status: str
    total: int
    success: int
    failed: int
    results: List[BatchExportFileResult]
