"""
Database Models and Configuration

This module defines the SQLAlchemy database models and configuration for the
Product Management API. It includes models for products and cart items,
along with database session management and table creation utilities.

The module provides:
- Product model with stock tracking
- CartItem model for shopping cart functionality
- Database session management
- Table creation utilities
- Relationship definitions between models

Author: Product Management Team
Version: 1.0.0
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from config import settings

# Create async database engine with configuration from settings
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

# Create declarative base for model definitions
Base = declarative_base()

class Product(Base):
    """
    Product model representing items available for purchase.

    This model stores product information including pricing, description,
    and stock levels. Products have a one-to-many relationship with cart items.

    Attributes:
        id (int): Primary key, auto-incrementing product identifier
        name (str): Unique product name, indexed for fast lookups
        price (float): Product price in USD, required field
        description (str, optional): Product description, can be null
        stock (int): Current stock level, defaults to 0
        created_at (datetime): Timestamp when product was created
        cart_items (relationship): Related cart items containing this product

    Constraints:
        - name must be unique across all products
        - price cannot be null
        - stock defaults to 0 if not specified

    Cascade Behavior:
        - Deleting a product will automatically remove all associated cart items
        - Uses both SQLAlchemy ORM-level and database-level cascade deletion
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    stock = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to cart items with cascade deletion
    cart_items = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True
    )


class CartItem(Base):
    """
    Cart item model representing products added to the shopping cart.

    This model tracks which products are in the cart, their quantities,
    and maintains timestamps for creation and updates. Each cart item
    is linked to a specific product via foreign key relationship.

    Attributes:
        id (int): Primary key, auto-incrementing cart item identifier
        product_id (int): Foreign key reference to the product with cascade delete
        quantity (int): Number of units of this product in cart, defaults to 1
        created_at (datetime): Timestamp when item was added to cart
        updated_at (datetime): Timestamp when item was last modified
        product (relationship): Related product object

    Constraints:
        - product_id must reference a valid product
        - quantity defaults to 1 if not specified
        - updated_at automatically updates on modifications
        - Cart item will be automatically deleted if parent product is deleted
    """
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to product
    product = relationship("Product", back_populates="cart_items")


async def get_db():
    """
    Database session dependency for FastAPI.

    This function provides a database session for each request and ensures
    proper cleanup after the request is completed. It's designed to be used
    as a FastAPI dependency.

    Yields:
        AsyncSession: Database session for the current request

    Usage:
        Use with FastAPI's Depends() to inject database sessions:
        async def endpoint(db: AsyncSession = Depends(get_db)):
    """
    async with AsyncSessionLocal() as session:
        yield session


async def create_tables():
    """
    Create all database tables based on the defined models.

    This function creates all tables defined by the SQLAlchemy models
    in the database. It's typically called during application startup
    to ensure the database schema is properly initialized.

    The function uses the global engine to establish a connection and
    runs the table creation synchronously within an async context.

    Raises:
        SQLAlchemyError: If table creation fails due to database issues

    Note:
        This function is idempotent - it won't fail if tables already exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
