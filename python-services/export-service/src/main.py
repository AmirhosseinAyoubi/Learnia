# AI-assisted implementation.
# Tool: Claude Sonnet 4.6 (claude-sonnet-4-6)
# Prompts used: see project README §12 "Own Work vs AI-Assisted Work"
"""Entry point for the Learnia Export Service.

Configures the FastAPI application, registers the export router, and exposes
standard health-check and root endpoints.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routers.export import router

app = FastAPI(
    title="Learnia Export Service",
    description=(
        "Auxiliary service that converts AI-generated study materials "
        "(stored as JSON in the ai-service) into portable study formats: "
        "Markdown study guide, Anki-compatible CSV, and plain text."
    ),
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


@app.get("/health", tags=["infrastructure"])
async def health_check() -> dict:
    """Return a simple liveness probe response."""
    return {"status": "healthy", "service": "export-service"}


@app.get("/", tags=["infrastructure"])
async def root() -> dict:
    """Return service name, version, and available export formats."""
    return {
        "message": "Learnia Export Service",
        "version": "1.0.0",
        "formats": ["markdown", "anki", "text"],
    }


if __name__ == "__main__":  # pragma: no cover
    import uvicorn  # pylint: disable=import-outside-toplevel

    uvicorn.run(app, host="0.0.0.0", port=8004)
