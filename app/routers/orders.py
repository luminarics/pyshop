from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.user import User
from app.routers.profile import current_active_user
from app.models.order import (
    CheckoutRequest,
    OrderRead,
    OrderListItem,
    OrderStatus,
)
from app.services.checkout_service import CheckoutService
from app.dependencies.cart import get_user_cart

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def checkout(
    checkout_request: CheckoutRequest,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create an order from the current user's cart.

    Validates cart contents, creates order with shipping details,
    and marks cart as converted.
    """
    checkout_service = CheckoutService(session)

    # Get user's cart
    cart = await get_user_cart(user.id, session)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )

    # Validate cart before checkout
    is_valid, errors = await checkout_service.validate_cart_for_checkout(cart)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Cart validation failed", "errors": errors},
        )

    try:
        # Create order from cart
        order = await checkout_service.create_order_from_cart(
            cart=cart, user_id=user.id, checkout_request=checkout_request
        )

        # Convert to read model
        order_read = await checkout_service.get_order_read_model(order)

        return order_read
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order",
        ) from e


@router.get("", response_model=List[OrderListItem])
async def get_orders(
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get list of user's orders.

    Returns paginated list of orders sorted by creation date (newest first).
    """
    if limit > 100:
        limit = 100

    checkout_service = CheckoutService(session)
    orders = await checkout_service.get_user_orders(
        user_id=user.id, limit=limit, offset=offset
    )

    # Convert to list items
    order_list = []
    for order in orders:
        order_list.append(
            OrderListItem(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                payment_status=order.payment_status,
                total=order.total,
                items_count=len(order.items),
                created_at=order.created_at,
            )
        )

    return order_list


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed order information.

    Returns full order details including all items and shipping information.
    """
    checkout_service = CheckoutService(session)
    order = await checkout_service.get_order_by_id(order_id=order_id, user_id=user.id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    order_read = await checkout_service.get_order_read_model(order)
    return order_read


@router.get("/number/{order_number}", response_model=OrderRead)
async def get_order_by_number(
    order_number: str,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get order by order number.

    Alternative way to retrieve order using the human-readable order number.
    """
    checkout_service = CheckoutService(session)
    order = await checkout_service.get_order_by_number(
        order_number=order_number, user_id=user.id
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    order_read = await checkout_service.get_order_read_model(order)
    return order_read


@router.post("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    order_id: UUID,
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Cancel an order.

    Only orders with status PENDING or CONFIRMED can be cancelled.
    """
    checkout_service = CheckoutService(session)
    order = await checkout_service.get_order_by_id(order_id=order_id, user_id=user.id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Check if order can be cancelled
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel order with status {order.status}",
        )

    updated_order = await checkout_service.update_order_status(
        order_id=order_id, user_id=user.id, status=OrderStatus.CANCELLED
    )

    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    order_read = await checkout_service.get_order_read_model(updated_order)
    return order_read
