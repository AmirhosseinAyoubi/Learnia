from fastapi import APIRouter, BackgroundTasks, HTTPException
from ..schemas import ProcessDocumentMessage
from ..services import process_document

router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.post("/process")
def trigger_processing(message: ProcessDocumentMessage, background_tasks: BackgroundTasks):
    """Manually trigger document processing via HTTP (alternative to RabbitMQ)."""
    try:
        background_tasks.add_task(process_document, message.documentId, message.fileUrl, message.fileType)
        return {"status": "accepted", "documentId": message.documentId}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
