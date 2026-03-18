"""
routers/processing.py — FastAPI router for document processing endpoints.

Endpoints:
    POST /api/v1/processing/process
        Upload a document (PDF, PPTX, or TXT) and receive extracted text
        split into chunks ready for embedding.

    GET /api/v1/processing/health
        Health check — returns service status.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ..services import process_document

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        200 OK with service status.
    """
    return {"status": "healthy", "service": "processing-service"}


@router.post("/process")
async def process_document_endpoint(file: UploadFile = File(...)):
    """
    Extract and chunk text from an uploaded document.

    Accepts a multipart/form-data file upload.
    Supported file types: PDF, PPTX, TXT.

    Args:
        file: the uploaded file (UploadFile from multipart form)

    Returns:
        200 OK with ProcessingResponse containing extracted text chunks
        and _links for HATEOAS navigation.

    Raises:
        400 Bad Request: unsupported file type or empty document
        500 Internal Server Error: extraction failure
    """
    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        file_type, chunks = process_document(file_bytes, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    response_body = {
        "filename":    file.filename,
        "file_type":   file_type,
        "chunk_count": len(chunks),
        "chunks":      [chunk.model_dump() for chunk in chunks],
        "_links": {
            "self":   {"href": "/api/v1/processing/process"},
            "health": {"href": "/api/v1/processing/health"},
        },
    }

    return JSONResponse(content=response_body, status_code=200)
