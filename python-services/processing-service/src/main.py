"""
Learnia Processing Service
Handles document processing (PDF, PPTX, TXT) and text chunking
"""
import logging
import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import router
from .consumers import start_consumer

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Learnia Processing Service",
    description="Document processing and text chunking service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def start_rabbitmq_consumer():
    thread = threading.Thread(target=start_consumer, daemon=True)
    thread.start()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "processing-service"}


@app.get("/")
async def root():
    return {"message": "Learnia Processing Service", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
