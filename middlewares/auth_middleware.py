from starlette.requests import Request
from starlette import status
from starlette.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "false").lower() == "true"


async def api_key_middleware(request: Request, call_next):
    if DISABLE_AUTH:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized."}
        )

    # Extract the token after Bearer
    token = auth_header.split(" ")[1]

    if token != API_KEY:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Unauthorized."}
        )

    return await call_next(request)
