from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.router import api_router
from src.core.exceptions import BaseAppError

app = FastAPI()

app.include_router(api_router)


@app.exception_handler(BaseAppError)
async def app_exception_handler(request: Request, exc: BaseAppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.message,
            "code": exc.code,
        },
        headers=exc.headers,
    )
