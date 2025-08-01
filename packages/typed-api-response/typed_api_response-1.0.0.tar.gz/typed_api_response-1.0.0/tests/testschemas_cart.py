from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class CartItemDataclass:
    product_id: str
    name: str
    quantity: int
    price: float 


@dataclass
class CartDataclass:
    items: list[CartItemDataclass]
    session_id: str


class CartItemPydantic(BaseModel):
    product_id: str
    name: str
    quantity: int
    price: float
    
    
class CartPydantic(BaseModel):
    items: list[CartItemPydantic]
    session_id: str

