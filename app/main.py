from fastapi import Request
from middleware.auth import is_admin
from routes.admin import adminRouter
from routes.auth import authRouter
from routes.order import orderRouter
from routes.product import productRouter
from db.db import init_db
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def checkToken(request: Request, call_next):
    is_admin(request)
    return await call_next(request)


@app.get("/")
def health_check():
    return {"message": "Server is running"}


app.include_router(adminRouter, prefix="/admin", tags=["admin"])
app.include_router(authRouter, prefix="/auth", tags=["auth"])
app.include_router(orderRouter, prefix="/order", tags=["order"])
app.include_router(productRouter, prefix="/products", tags=["products"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=8000)
