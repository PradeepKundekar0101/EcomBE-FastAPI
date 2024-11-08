from fastapi.responses import JSONResponse
from jose import jwt, JWTError

from fastapi import Request
from config.settings import JWT_SECRET, ALGO


def is_admin(request: Request):
    if request.url.path.startswith("/admin"):
        token = request.headers.get("Authorization").replace("Bearer ", "")
        if not token:
            return JSONResponse(status_code=401, content="No token")
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
            if str(payload.get("role")).split(".").pop(1) != "Admin":
                return JSONResponse(status_code=403, content="Not an Admin")
            request.state.user = payload
        except JWTError as e:
            print(e)
            return JSONResponse(status_code=401, content="Invalid token")
    elif request.url.path.startswith("/user"):
        pass
