"""FastAPI application entrypoint.

Run with: uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request, status as http_status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers.tasks import router as tasks_router

app = FastAPI(
    title="Team Kanban API",
    version="0.1.0",
    description="Implements openapi.yaml at the repository root.",
)

# Wide open by design: docs/specs.md §5.2 makes the whole board accessible to
# anyone with the shared URL, with no accounts and nothing to authenticate,
# so there is no origin to restrict this to and no credentials in play.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks_router)


@app.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    return {"status": "ok"}


# openapi.yaml's Error schema is a flat {"message": string}. FastAPI's
# defaults don't produce that shape on their own — HTTPException nests its
# detail under a "detail" key, and body-validation failures return 422
# rather than the 400 the contract documents — so both are normalized here
# to keep the implementation matching the contract exactly.


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"message": message})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first = exc.errors()[0]
    location = ".".join(str(part) for part in first["loc"] if part != "body")
    message = f"{location}: {first['msg']}" if location else first["msg"]
    return JSONResponse(status_code=http_status.HTTP_400_BAD_REQUEST, content={"message": message})
