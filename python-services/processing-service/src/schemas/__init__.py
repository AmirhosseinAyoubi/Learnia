from pydantic import BaseModel
from typing import Optional


class ProcessDocumentMessage(BaseModel):
    documentId: str
    fileUrl: str
    fileType: str


class StatusUpdate(BaseModel):
    status: str  # PENDING | PROCESSING | COMPLETED | FAILED
    pageCount: Optional[int] = None
    error: Optional[str] = None
