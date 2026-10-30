from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from app.api.routes.tasks import router
from app.services.task_service import TaskNotFound

ROOT = Path(__file__).parent
app = FastAPI(title="TaskFlow", version="0.1.0")
app.include_router(router)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.exception_handler(TaskNotFound)
async def not_found(request: Request, exc: TaskNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "タスクが見つかりません"})


@app.exception_handler(RequestValidationError)
async def invalid_input(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Do not echo user content or internal validation context.
    errors = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(Exception)
async def server_error(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "処理に失敗しました"})


@app.middleware("http")
async def security_headers(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    if request.url.path == "/" or request.url.path.startswith("/static/"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        )
    return response


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(ROOT / "templates" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
