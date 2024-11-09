from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select 
from sqlmodel import Session, select
from sqlalchemy.exc import OperationalError
import time
from typing import Optional

from db.db import get_session
from db.schema import Order, OrderBase, Product, Stock, User

orderRouter = APIRouter()

def acquire_stock_lock(session: Session, product_id: int, required_quantity: int, 
                      max_retries: int = 3, retry_delay: float = 0.1) -> Optional[Stock]:
    for attempt in range(max_retries):
        try:
            product_stock = session.exec(
                select(Stock)
                .with_for_update(nowait=True)
                .where(Stock.product_id == product_id)
            ).first()
            
            if not product_stock:
                raise HTTPException(status_code=404, detail="Product stock not found")
                
            if product_stock.quantity >= required_quantity:
                return product_stock
            else:
                return None
                
        except OperationalError as e:
            if attempt == max_retries - 1:
                raise HTTPException(
                    status_code=409,
                    detail="High load, please try again later"
                )
            time.sleep(retry_delay * (attempt + 1))  
            continue

@orderRouter.post("/buy")
def handle_buy(order: OrderBase, session: Session = Depends(get_session)):
    try:
        # Get user and product outside the transaction
        user = session.get(User, order.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        product = session.get(Product, order.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Start transaction for stock update and order creation
        product_stock = acquire_stock_lock(
            session=session,
            product_id=order.product_id,
            required_quantity=order.quantity
        )
        
        if product_stock is None:
            raise HTTPException(
                status_code=400,
                detail="Insufficient stock available"
            )
        
        total_amount = product.price * order.quantity
        
        new_order = Order(
            user_id=order.user_id,
            amount=total_amount,
            quantity=order.quantity,
            product_id=order.product_id
        )
        
        product_stock.quantity -= order.quantity
        
        # Add both changes to session
        session.add(product_stock)
        session.add(new_order)
        
        # Commit the transaction
        try:
            session.commit()
            session.refresh(new_order)
            return {
                "message": "Order placed successfully",
                "data": new_order.dict(),
                "remaining_stock": product_stock.quantity
            }
        except OperationalError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Concurrent update detected, please retry"
            )
            
    except HTTPException as e:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing order"
        )
    finally:
        session.close()

@orderRouter.get("/")
def get_all_orders(session: Session = Depends(get_session)):
    try:
        query = select(Order)
        orders = session.exec(query).all()
        
        response_data = {
            "message": "Orders retrieved successfully" if orders else "No orders found",
            "data": [order.dict() for order in orders] if orders else []
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Error retrieving orders"
        )
    finally:
        session.close()