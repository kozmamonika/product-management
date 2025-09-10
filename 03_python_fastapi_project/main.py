from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import settings
from database import Product, CartItem, create_tables, get_db, engine


async def create_sample_data():
    """Create sample products for testing"""
    async with AsyncSession(bind=engine) as session:
        # Check if products already exist
        result = await session.execute(select(Product))
        existing_products = result.scalars().all()

        if not existing_products:
            sample_products = [
                Product(name="Laptop", price=999.99, description="High-performance laptop for work and gaming", stock=5),
                Product(name="Wireless Mouse", price=29.99, description="Ergonomic wireless mouse with long battery life", stock=15),
                Product(name="Mechanical Keyboard", price=129.99, description="RGB mechanical keyboard for gaming", stock=8),
                Product(name="Monitor", price=299.99, description="24-inch 4K monitor with HDR support", stock=3),
                Product(name="Webcam", price=79.99, description="HD webcam for video calls and streaming", stock=12),
                Product(name="Headphones", price=159.99, description="Noise-cancelling wireless headphones", stock=0),  # Out of stock for testing
            ]

            for product in sample_products:
                session.add(product)

            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await create_sample_data()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the product store"}

class ProductDTO(BaseModel):
    id: int
    name: str
    price: float
    description: str | None = None
    stock: int


class ProductCreate(BaseModel):
    name: str
    price: float
    description: str | None = None
    stock: int


class ProductUpdate(BaseModel):
    price: Optional[float] = None
    stock: Optional[int] = None


class CartItemDTO(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductDTO
    line_total: float


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartSummary(BaseModel):
    items: List[CartItemDTO]
    total: float
    item_count: int


@app.post("/products/", response_model=ProductDTO)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.name == product.name))
    db_product = result.first()

    if db_product:
        raise HTTPException(status_code=400, detail="Product name already registered")

    db_product = Product(
        name=product.name,
        price=product.price,
        description=product.description,
        stock=product.stock,
    )
    db.add(db_product)
    await db.commit()
    await db.refresh(db_product)
    return db_product


@app.get("/products/", response_model=List[ProductDTO])
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products


@app.put("/products/{product_id}", response_model=ProductDTO)
async def update_product(
    product_id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.stock is not None:
        db_product.stock = product_update.stock

    await db.commit()
    await db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(db_product)
    await db.commit()
    return


@app.get("/products/{product_id}", response_model=ProductDTO)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# Cart endpoints
@app.post("/cart/items/", response_model=CartItemDTO)
async def add_to_cart(cart_item: CartItemAdd, db: AsyncSession = Depends(get_db)):
    # Check if product exists
    result = await db.execute(select(Product).filter(Product.id == cart_item.product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if item already exists in cart
    result = await db.execute(
        select(CartItem).filter(CartItem.product_id == cart_item.product_id)
    )
    existing_cart_item = result.scalar_one_or_none()

    # Calculate current cart quantity and new total
    current_cart_quantity = existing_cart_item.quantity if existing_cart_item else 0
    new_cart_total = current_cart_quantity + cart_item.quantity

    # Calculate total available stock (current stock + already in cart)
    total_available = product.stock + current_cart_quantity

    # Check if we have enough total stock
    if total_available < new_cart_total:
        raise HTTPException(
            status_code=409,
            detail=f"Insufficient stock. Available: {total_available}, Requested total: {new_cart_total}"
        )

    if existing_cart_item:
        # Update existing cart item
        existing_cart_item.quantity = new_cart_total
        db_cart_item = existing_cart_item
    else:
        # Create new cart item
        db_cart_item = CartItem(
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(db_cart_item)

    # Update product stock (reduce by the quantity being added)
    product.stock -= cart_item.quantity

    await db.commit()
    await db.refresh(db_cart_item)
    await db.refresh(product)

    # Return cart item with product details
    return CartItemDTO(
        id=db_cart_item.id,
        product_id=db_cart_item.product_id,
        quantity=db_cart_item.quantity,
        product=ProductDTO(
            id=product.id,
            name=product.name,
            price=product.price,
            description=product.description,
            stock=product.stock
        ),
        line_total=product.price * db_cart_item.quantity
    )


@app.get("/cart/", response_model=CartSummary)
async def get_cart(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.product))
    )
    cart_items = result.scalars().all()

    items = []
    total = 0

    for cart_item in cart_items:
        line_total = cart_item.product.price * cart_item.quantity
        total += line_total

        items.append(CartItemDTO(
            id=cart_item.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            product=ProductDTO(
                id=cart_item.product.id,
                name=cart_item.product.name,
                price=cart_item.product.price,
                description=cart_item.product.description,
                stock=cart_item.product.stock
            ),
            line_total=line_total
        ))

    return CartSummary(
        items=items,
        total=total,
        item_count=len(items)
    )


@app.patch("/cart/items/{cart_item_id}/remove-one", response_model=CartItemDTO)
async def remove_one_from_cart(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.id == cart_item_id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Decrease quantity by 1
    cart_item.quantity -= 1

    # Restore 1 item to stock
    cart_item.product.stock += 1

    # If quantity becomes 0, remove the cart item
    if cart_item.quantity <= 0:
        await db.delete(cart_item)
        await db.commit()
        raise HTTPException(status_code=204, detail="Cart item removed completely")

    await db.commit()
    await db.refresh(cart_item)
    await db.refresh(cart_item.product)

    # Return updated cart item with product details
    return CartItemDTO(
        id=cart_item.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        product=ProductDTO(
            id=cart_item.product.id,
            name=cart_item.product.name,
            price=cart_item.product.price,
            description=cart_item.product.description,
            stock=cart_item.product.stock
        ),
        line_total=cart_item.product.price * cart_item.quantity
    )


@app.delete("/cart/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.product)).filter(CartItem.id == cart_item_id)
    )
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # Restore stock to product
    cart_item.product.stock += cart_item.quantity

    await db.delete(cart_item)
    await db.commit()
    return


@app.delete("/cart/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(db: AsyncSession = Depends(get_db)):
    # Restore stock for all items in cart
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.product))
    )
    cart_items = result.scalars().all()

    for cart_item in cart_items:
        cart_item.product.stock += cart_item.quantity
        await db.delete(cart_item)

    await db.commit()
    return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
