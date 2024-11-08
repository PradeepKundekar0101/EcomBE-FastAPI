import json
from fastapi import APIRouter, Depends, HTTPException

from sqlmodel import Session, select

from db.db import get_session
from db.schema import Order, OrderBase, Product
orderRouter = APIRouter()
@orderRouter.post("/buy")
def handleBuy(order:OrderBase,session:Session=Depends(get_session)):
    try:
        user = session.get(Order,order.user_id)
        if not user:
            raise HTTPException(status_code=404,detail="User not found")
        product = session.get(Product,order.product_id)
        if not product:
            raise HTTPException(status_code=404,detail="Product not found")
        new_order = Order(user_id=order.user_id,amount=order.amount,quantity=order.quantity,product_id=order.product_id)
        session.add(new_order)
        session.commit()
        session.refresh(new_order)
        return {"message":"Order place","data":json.dumps(new_order)}

    except HTTPException as e:
        raise
    except Exception as e:
        raise HTTPException(status_code=500,detail="Interval server error")
    
@orderRouter.get("/")
def get_all_orders(session:Session=Depends(get_session)):
    try:
        orders = session.exec(select(Order)).all()
        if not orders:
            raise HTTPException(status_code=400, detail="Orders not found")
        return {"message":"Order","data":([p.dict() for p in orders])}
    except HTTPException as e:
        raise
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error")




