from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID,uuid4
from enum import Enum

class Role(Enum):
    Admin = "ADMIN"
    User = "USER"

# =============USER======================
class UserBase(SQLModel):
    username:str
    password:str
    address:str
    role: Role | None = Field(default=Role.Admin)

class User(UserBase,table=True):
    id: UUID = Field(default_factory= uuid4,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class UserLogin(BaseModel):
    username:str
    password:str

# =============PRODUCT======================
class ProductBase(SQLModel):
    name: str
    description: str
    price: int

class Product(ProductBase,table=True):
    id: UUID = Field(default_factory=uuid4,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="product")

class ProductCreate(ProductBase):
    pass

# =============ORDER======================
class OrderBase(SQLModel):
    user_id: UUID = Field(foreign_key="user.id")
    product_id: UUID = Field(foreign_key="product.id")
    quantity: int = 0
    amount: int = 0

class Order(OrderBase,table=True):
    id: UUID = Field(primary_key=True,default_factory=uuid4)
    user: User = Relationship(back_populates="orders")
    product: Product = Relationship(back_populates="orders")

