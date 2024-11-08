import json
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session,select
from db.db import get_session
from db.schema import Product

productRouter = APIRouter()

@productRouter.get("/")
def getAllProducts(session: Session = Depends(get_session)):
    try:
        products = session.exec(select(Product)).all()
        if not products:
            raise HTTPException(status_code=400, detail="Products not found")
        return {"message":"Products","data":([p.dict() for p in products])}
    except HTTPException as e:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error")


