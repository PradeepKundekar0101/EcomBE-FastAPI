from fastapi import FastAPI
from routes.admin import adminRouter
from routes.auth import authRouter
from routes.order import orderRouter
from db.db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def health_check():
    return {"message":"Server is running"}


app.include_router(adminRouter, prefix="/admin", tags=["admin"])
app.include_router(authRouter, prefix="/auth",tags=["auth"])
app.include_router(orderRouter, prefix="/order", tags=["order"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app,host="0.0.0.0",port=8000)