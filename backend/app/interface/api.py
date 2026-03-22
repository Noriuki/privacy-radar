"""FastAPI application with CORS and /api/v1 router."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.interface.routes import router


def _version() -> str:
    try:
        from importlib.metadata import version
        return version("privacy-radar")
    except Exception:
        return "1.0.0"


app = FastAPI(
    title="PrivacyRadar API",
    description="Assistente de privacidade LGPD: questionário guiado + análise de contrato OpenAPI/GraphQL.",
    version=_version(),
)

# CORS for frontend (dev: 5173, prod: same host or configured origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def index():
    return {"name": "PrivacyRadar", "version": _version(), "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "PrivacyRadar"}
