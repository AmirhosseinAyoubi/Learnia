# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Entry point for the Learnia AI Service.

Configures the FastAPI application, registers the router, and exposes
standard health-check and root endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routers import router

app = FastAPI(
    title="Learnia AI Service",
    description="AI/LLM integration service for generating study materials",
    version="1.0.0",
)


def _custom_openapi() -> dict:
    """Inject the X-API-Key security scheme into the generated OpenAPI spec."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    schema.setdefault("components", {})["securitySchemes"] = {
        "X-API-Key": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
    }
    schema["security"] = [{"X-API-Key": []}]
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi  # type: ignore[method-assign]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check() -> dict:
    """Return a simple liveness probe response."""
    return {"status": "healthy", "service": "ai-service"}


@app.get("/")
async def root() -> dict:
    """Return service name and version."""
    return {"message": "Learnia AI Service", "version": "1.0.0"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn  # pylint: disable=import-outside-toplevel
    uvicorn.run(app, host="0.0.0.0", port=8003)
