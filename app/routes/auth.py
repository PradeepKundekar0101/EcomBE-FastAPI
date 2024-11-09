from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from config.secrets import JWT_SECRET
from db.db import get_session
from db.schema import User, UserCreate, UserLogin
from config.settings import ALGO
print(JWT_SECRET)
authRouter = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@authRouter.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def createAccount(userData: UserCreate, session: Session = Depends(get_session)):
    try:
        existing_user = session.exec(select(User).where(User.username == userData.username)).first()
        if existing_user:
            raise HTTPException(status_code=409, detail="Username already taken")
        
        hashed_password = pwd_context.hash(userData.password)
        user = User(
            address=userData.address,
            username=userData.username,
            password=hashed_password,
            role=userData.role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        print("Signup Error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@authRouter.post("/signin", status_code=status.HTTP_200_OK)
def login(userData: UserLogin, session: Session = Depends(get_session)):
    try:

        user = session.exec(select(User).where(User.username == userData.username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not pwd_context.verify(userData.password, user.password):
            raise HTTPException(status_code=403, detail="Incorrect password")
        
        token = jwt.encode(
            {
                "user_id": str(user.id),
                "role": str(user.role),
                "exp": datetime.utcnow() + timedelta(days=7),
            },
            JWT_SECRET,
            algorithm=ALGO,
        )
        
        return {
            "user": {
                "username": user.username,
                "id": str(user.id),
                "address": str(user.address),
                "role": str(user.role),
            },
            "token": token,
        }
    except HTTPException:
        raise
    except Exception as e:
        print("Signin Error:", e)
        raise HTTPException(status_code=500, detail="Internal server error")
