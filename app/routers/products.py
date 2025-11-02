from fastapi import HTTPException
from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.product import Product
from app.database import get_session
from app.models.product import ProductCreate, ProductRead, ProductUpdate
from app.models.user import User
from app.routers.profile import current_active_user

router = APIRouter()


@router.get("/products/", response_model=List[ProductRead])
async def list_products(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    category: str | None = Query(None, description="Filter by category"),
):
    query = select(Product)

    if category:
        query = query.where(Product.category == category)

    query = query.order_by(Product.id).offset(offset).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()


@router.post(
    "/products/", response_model=ProductRead, status_code=status.HTTP_201_CREATED
)
async def create_product(
    product_data: ProductCreate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    product = Product(**product_data.model_dump())
    session.add(product)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Product with this name exists")
    await session.refresh(product)
    return product


@router.put("/products/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)

    await session.commit()
    await session.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await session.delete(product)
    await session.commit()
    return
