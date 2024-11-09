from fastapi.responses import JSONResponse
from jose import jwt, JWTError
from fastapi import  Request
from config.secrets import JWT_SECRET
from config.settings import  ALGO


async def is_admin(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        return JSONResponse(status_code=401, content={"error": "No token provided"})
    token = token.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGO])
        
        role = payload.get("role", "")
        if not role or "Admin" not in role.split("."):
            return JSONResponse(status_code=403, content={"error": "Not authorized"})

        request.state.user = payload
        return None  
        
    except JWTError as err:
        print("JWT decoding error:", err)
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    except Exception as err2:
        print("Unexpected error:", err2)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})

