from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.api.router import api_router
from src.core.exceptions import UserAlreadyExistsError

app = FastAPI()

app.include_router(api_router)


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_exception_handler(
    request: Request, exc: UserAlreadyExistsError
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"message": exc.message}
    )
