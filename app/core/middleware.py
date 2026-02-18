from fastapi import Request
from fastapi.responses import JSONResponse
import jwt
from app.core.config import JWT_SECRET, JWT_ALGO

async def jwt_middleware(request: Request, call_next):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("Bearer "):
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    try:
        token = auth.replace("Bearer ", "")
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        request.state.user_email = payload["email"].strip().lower()
    except Exception:
        return JSONResponse(status_code=401, content={"detail": "Invalid token"})

    return await call_next(request)
