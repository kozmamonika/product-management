"""
Product Management API with Shopping Cart

This module provides a FastAPI-based REST API for managing products and shopping cart functionality.
It includes endpoints for CRUD operations on products, cart management, and stock tracking.

The API supports:
- Product management (create, read, update, delete)
- Shopping cart operations (add, remove, clear)
- Stock tracking and validation
- Concurrent cart operations with proper stock management

Author: Product Management Team
Version: 1.0.0
"""

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the application lifecycle.

    This context manager handles application startup and shutdown tasks:
    - Creates database tables on startup
    - Ensures proper cleanup on shutdown

    Args:
        app (FastAPI): The FastAPI application instance

    Yields:
        None: Control back to the application
    """
    await create_tables()
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
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: Welcome message for the API
    """
    return {"message": "Welcome to the product store"}

class ProductDTO(BaseModel):
    """
    Product Data Transfer Object for API responses.

    This model represents a product with all its attributes
    as returned by the API endpoints.

    Attributes:
        id (int): Unique product identifier
        name (str): Product name
        price (float): Product price in USD
        description (str | None): Optional product description
        stock (int): Available stock quantity
    """
    id: int
    name: str
    price: float
    description: str | None = None
    stock: int


class ProductCreate(BaseModel):
    """
    Product creation request model.

    This model defines the required and optional fields
    for creating a new product.

    Attributes:
        name (str): Product name (required, must be unique)
        price (float): Product price in USD (required, must be positive)
        description (str | None): Optional product description
        stock (int): Initial stock quantity (required, must be non-negative)
    """
    name: str
    price: float
    description: str | None = None
    stock: int


class ProductUpdate(BaseModel):
    """
    Product update request model.

    This model defines the fields that can be updated for an existing product.
    All fields are optional to support partial updates.

    Attributes:
        price (Optional[float]): New product price
        stock (Optional[int]): New stock quantity
        description (Optional[str]): New product description
    """
    price: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None


class CartItemDTO(BaseModel):
    """
    Cart Item Data Transfer Object for API responses.

    This model represents a cart item with its associated product
    information and calculated line total.

    Attributes:
        id (int): Unique cart item identifier
        product_id (int): Associated product identifier
        quantity (int): Quantity of the product in cart
        product (ProductDTO): Complete product information
        line_total (float): Calculated total for this line item (price × quantity)
    """
    id: int
    product_id: int
    quantity: int
    product: ProductDTO
    line_total: float


class CartItemAdd(BaseModel):
    """
    Cart item addition request model.

    This model defines the data required to add an item to the cart.

    Attributes:
        product_id (int): ID of the product to add
        quantity (int): Quantity to add (defaults to 1)
    """
    product_id: int
    quantity: int = 1


class CartSummary(BaseModel):
    """
    Shopping cart summary model.

    This model provides a complete overview of the shopping cart
    including all items, totals, and item count.

    Attributes:
        items (List[CartItemDTO]): List of all cart items
        total (float): Total cart value
        item_count (int): Number of different products in cart
    """
    items: List[CartItemDTO]
    total: float
    item_count: int


@app.post("/products/", response_model=ProductDTO)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new product.

    This endpoint creates a new product in the database with the provided information.
    Product names must be unique across the system.

    Args:
        product (ProductCreate): Product data for creation
        db (AsyncSession): Database session dependency

    Returns:
        ProductDTO: The created product with assigned ID

    Raises:
        HTTPException: 400 if product name already exists
    """
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
    """
    Retrieve all products.

    This endpoint returns a list of all products in the database
    with their current stock levels and details.

    Args:
        db (AsyncSession): Database session dependency

    Returns:
        List[ProductDTO]: List of all products
    """
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products


@app.put("/products/{product_id}", response_model=ProductDTO)
async def update_product(
    product_id: int, product_update: ProductUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an existing product.

    This endpoint allows partial updates to product information.
    Only the provided fields will be updated.

    Args:
        product_id (int): ID of the product to update
        product_update (ProductUpdate): Fields to update
        db (AsyncSession): Database session dependency

    Returns:
        ProductDTO: The updated product

    Raises:
        HTTPException: 404 if product not found
    """
    result = await db.execute(select(Product).filter(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_update.price is not None:
        db_product.price = product_update.price
    if product_update.stock is not None:
        db_product.stock = product_update.stock
    if product_update.description is not None:
        db_product.description = product_update.description

    await db.commit()
    await db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a product.

    This endpoint removes a product from the database.
    Associated cart items should be handled before deletion.

    Args:
        product_id (int): ID of the product to delete
        db (AsyncSession): Database session dependency

    Raises:
        HTTPException: 404 if product not found
    """
    result = await db.execute(select(Product).filter(Product.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    await db.delete(db_product)
    await db.commit()
    return


@app.get("/products/{product_id}", response_model=ProductDTO)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single product by ID.

    This endpoint returns detailed information about a specific product.

    Args:
        product_id (int): ID of the product to retrieve
        db (AsyncSession): Database session dependency

    Returns:
        ProductDTO: The requested product

    Raises:
        HTTPException: 404 if product not found
    """
    result = await db.execute(select(Product).filter(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# Cart endpoints
@app.post("/cart/items/", response_model=CartItemDTO)
async def add_to_cart(cart_item: CartItemAdd, db: AsyncSession = Depends(get_db)):
    """
    Add an item to the shopping cart.

    This endpoint adds a product to the cart or increases the quantity
    if the product is already in the cart. It performs stock validation
    to ensure sufficient inventory is available.

    Stock Management:
    - Checks total available stock (current stock + already in cart)
    - Validates that the requested quantity doesn't exceed availability
    - Updates product stock by reducing the added quantity
    - Handles both new cart items and quantity updates

    Args:
        cart_item (CartItemAdd): Item to add with product ID and quantity
        db (AsyncSession): Database session dependency

    Returns:
        CartItemDTO: The cart item with product details and line total

    Raises:
        HTTPException: 404 if product not found
        HTTPException: 409 if insufficient stock available
    """
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
    """
    Retrieve the complete shopping cart.

    This endpoint returns all items in the cart with their associated
    product information, quantities, line totals, and overall cart summary.
    It also handles cleanup of orphaned cart items (items referencing deleted products).

    Calculations:
    - Line total: product price × quantity for each item
    - Cart total: sum of all line totals
    - Item count: number of different products in cart

    Args:
        db (AsyncSession): Database session dependency

    Returns:
        CartSummary: Complete cart information with items and totals
    """
    result = await db.execute(
        select(CartItem).options(selectinload(CartItem.product))
    )
    cart_items = result.scalars().all()

    items = []
    total = 0
    orphaned_items = []

    for cart_item in cart_items:
        # Check if the cart item has a valid associated product
        if cart_item.product is None:
            # This is an orphaned cart item - product was deleted but cart item wasn't
            orphaned_items.append(cart_item)
            continue

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

    # Clean up orphaned cart items if any were found
    if orphaned_items:
        for orphaned_item in orphaned_items:
            await db.delete(orphaned_item)
        await db.commit()

    return CartSummary(
        items=items,
        total=total,
        item_count=len(items)
    )


@app.patch("/cart/items/{cart_item_id}/remove-one", response_model=CartItemDTO)
async def remove_one_from_cart(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Remove one unit of an item from the cart.

    This endpoint decrements the quantity of a cart item by 1.
    If the quantity reaches 0, the entire cart item is removed.
    Stock is restored to the product when items are removed.

    Behavior:
    - Decreases cart item quantity by 1
    - Restores 1 unit to product stock
    - Removes cart item completely if quantity becomes 0
    - Returns updated cart item or 204 if completely removed

    Args:
        cart_item_id (int): ID of the cart item to modify
        db (AsyncSession): Database session dependency

    Returns:
        CartItemDTO: Updated cart item with new quantity and totals

    Raises:
        HTTPException: 404 if cart item not found
        HTTPException: 204 if item completely removed (quantity reached 0)
    """
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
    """
    Remove an entire item from the cart.

    This endpoint completely removes a cart item regardless of quantity.
    All units of the product are restored to stock.

    Args:
        cart_item_id (int): ID of the cart item to remove
        db (AsyncSession): Database session dependency

    Raises:
        HTTPException: 404 if cart item not found
    """
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
    """
    Clear all items from the shopping cart.

    This endpoint removes all cart items and restores all quantities
    back to their respective product stock levels.

    Process:
    1. Retrieve all cart items with product information
    2. Restore each item's quantity to its product stock
    3. Delete all cart items
    4. Commit changes atomically

    Args:
        db (AsyncSession): Database session dependency
    """
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
    """
    Application entry point for development server.

    This block runs the FastAPI application using Uvicorn when the script
    is executed directly. In production, use a proper ASGI server.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
