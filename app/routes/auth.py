from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from db.db import get_session
from db.schema import User, UserCreate, UserLogin
authRouter = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"],deprecated=["auto"])

JWT_SECRET="pradeep@123"
ALGO="HS256"

@authRouter.post("/signup", response_model=User, status_code=status.HTTP_201_CREATED)
def createAccount(userData:UserCreate,session:Session=Depends(get_session)):
    try:
        existing_user = session.exec(select(User).where(User.username==userData.username)).first()
        if existing_user:
            raise HTTPException(status_code=409,detail="Username already taken")
        hashed_password = pwd_context.hash(userData.password)
        user = User(address=userData.address,username=userData.username,password=hashed_password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500,detail="Error")

@authRouter.post("/signin", status_code=status.HTTP_200_OK)
def login(userData:UserLogin,session:Session=Depends(get_session)):
    user = session.exec(select(User).where(User.username==userData.username)).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    verified_password = pwd_context.verify(userData.password,user.password)
    if not verified_password:
        raise HTTPException(status_code=403,detail="Incorrect password")
    token = jwt.encode({"user_id":str(user.id),"exp":str(datetime.utcnow()+timedelta(days=7))},JWT_SECRET,algorithm=ALGO)

    return {"user":{
        "username":user.username,
        "id":str(user.id),
        "address":str(user.address)
    },"token":token}
