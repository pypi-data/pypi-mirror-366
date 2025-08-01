from .testschemas_cart import (
    CartDataclass, 
    CartItemDataclass, 
    CartPydantic, 
    CartItemPydantic
)

cart_item_pydantic = CartItemPydantic(product_id="SKU-2242", name="watermelon", quantity=1, price=6.89)
cart_item_dataclass = CartItemDataclass(product_id="SKU=1414", name="rice", quantity=4391, price=4.45)

cart_dataclass = CartDataclass(
    session_id="session-abc123",
    items=[
        CartItemDataclass(product_id="SKU-001", name="Tactical Spork", quantity=2, price=7.99),
        CartItemDataclass(product_id="SKU-002", name="Solar-Powered Flashlight", quantity=1, price=19.95),
        CartItemDataclass(product_id="SKU-003", name="Bulletproof Coffee Beans", quantity=3, price=14.50),
    ],
)

cart_pydantic = CartPydantic(
    session_id="session-abc123",
    items=[
        CartItemPydantic(product_id="SKU-001", name="Tactical Spork", quantity=2, price=7.99),
        CartItemPydantic(product_id="SKU-002", name="Solar-Powered Flashlight", quantity=1, price=19.95),
        CartItemPydantic(product_id="SKU-003", name="Bulletproof Coffee Beans", quantity=3, price=14.50),
    ],
)