from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session
from db.db import get_session
from db.schema import Product, ProductCreate, Stock

adminRouter = APIRouter()

@adminRouter.post("/product")
def create_product(data: ProductCreate, session: Session = Depends(get_session)):
    try:
        product = Product(
            name=data.name, price=data.price, description=data.description
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        product_stock = Stock(product_id=product.id, quantity=data.default_quantity)
        session.add(product_stock)
        session.commit()
        session.refresh(product_stock)
        return JSONResponse(
            content={
                "name": product.name,
                "price": product.price,
                "description": product.description,
                "id": str(product.id),
                "default_quantity": product_stock.quantity,
            },
            status_code=201,
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error")


@adminRouter.delete("/product/{productId}")
def delete_product(productId: str, session: Session = Depends(get_session)):
    if not productId:
        raise HTTPException(status_code=400, detail="Product Id not provided")
    try:
        product = session.get(Product, productId)
        product_stock = session.get(Stock,product.stock.id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        session.delete(product)
        session.delete(product_stock)
        session.commit()
        return {"message": "Product deleted", "data": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


@adminRouter.put("/product/{id}")
def update_product(
    id: str, product: ProductCreate, session: Session = Depends(get_session)
):
    try:
        if not id:
            raise HTTPException(status_code=400, detail="Id not provided")
        productFound = session.get(Product, id)
        if not productFound:
            raise HTTPException(status_code=404, detail="Product not found")
        productFound.name = product.name
        productFound.price = product.price
        productFound.description = product.description
        session.commit()
        return {
            "message": "Product updated successfully",
            "data": {
                "id": id,
                "name": productFound.name,
                "price": productFound.price,
                "description": productFound.description,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
