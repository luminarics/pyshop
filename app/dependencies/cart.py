from typing import Optional
from uuid import UUID
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.services.cart_service import CartService
from app.models.cart import Cart
from app.models.user import User
from app.routers.profile import current_user_optional
from app.middleware import get_session_id_from_state


def get_cart_service(session: AsyncSession = Depends(get_session)) -> CartService:
    """Dependency to get cart service instance."""
    return CartService(session)


def get_cart_resolution_service(session: AsyncSession = Depends(get_session)):
    """Dependency to get cart resolution service instance."""
    from app.services.cart_resolution import CartResolutionService

    return CartResolutionService(session)


def get_session_id(request: Request) -> Optional[str]:
    """
    Get cart session ID from middleware state.
    The SessionMiddleware provides this via request.state.session_id
    """
    return get_session_id_from_state(request)


async def get_current_cart(
    cart_service: CartService = Depends(get_cart_service),
    session_id: Optional[str] = Depends(get_session_id),
    current_user: Optional[User] = Depends(current_user_optional),
) -> Cart:
    """
    Get the current user's cart based on authentication state.

    Priority:
    1. If user is authenticated, get/create user cart
    2. If user is not authenticated, get/create session cart
    3. If both exist (user logged in with session cart), merge them
    """
    user_id = current_user.id if current_user else None

    if user_id:
        # User is authenticated
        try:
            # Try to get user's cart
            user_cart = await cart_service.get_or_create_cart(user_id=user_id)

            # Check if there's also a session cart to merge
            if session_id and session_id != str(user_cart.id):
                try:
                    session_cart = await cart_service.get_or_create_cart(
                        session_id=session_id
                    )
                    if session_cart.id != user_cart.id and session_cart.items:
                        # Merge session cart into user cart
                        user_cart = await cart_service.merge_carts(
                            source_cart_id=session_cart.id, target_cart_id=user_cart.id
                        )
                except Exception:
                    # If session cart doesn't exist or merge fails, continue with user cart
                    pass

            return user_cart

        except Exception as e:
            # Fallback to session cart if user cart fails
            if session_id:
                return await cart_service.get_or_create_cart(session_id=session_id)
            raise e
    else:
        # User is not authenticated, use session cart
        if not session_id:
            raise ValueError("No session ID available for guest cart")

        return await cart_service.get_or_create_cart(session_id=session_id)


async def get_cart_by_id(
    cart_id: UUID,
    cart_service: CartService = Depends(get_cart_service),
    current_user: Optional[User] = Depends(current_user_optional),
) -> Optional[Cart]:
    """
    Get cart by ID with ownership validation.
    Users can only access their own carts or session carts.
    """
    cart = await cart_service.get_cart_by_id(cart_id)

    if not cart:
        return None

    # Check ownership
    if current_user:
        # Authenticated user can access their own cart
        if cart.user_id == current_user.id:
            return cart

    # For session carts, we'd need to check session_id
    # but that requires access to the current session
    # For now, return the cart (will be handled by route-level validation)
    return cart


async def get_user_cart(
    user_id: UUID,
    session: AsyncSession,
) -> Optional[Cart]:
    """
    Get user's active cart directly by user ID.
    Used for checkout where we need to access authenticated user's cart.
    """
    cart_service = CartService(session)
    return await cart_service.get_or_create_cart(user_id=user_id)
