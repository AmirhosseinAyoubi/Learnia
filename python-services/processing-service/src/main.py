"""
Learnia Processing Service
Handles document processing (PDF, PPTX, TXT) and text chunking.

Endpoints:
    GET  /api/v1/processing/health  — service health check
    POST /api/v1/processing/process — upload a document, receive text chunks
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import router

app = FastAPI(
    title="Learnia Processing Service",
    description="Document processing and text chunking service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the processing router (health + process endpoints)
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint — service info."""
    return {"message": "Learnia Processing Service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
