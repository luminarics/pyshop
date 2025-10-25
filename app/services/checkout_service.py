from datetime import datetime
from typing import Optional, Tuple
from uuid import UUID
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.cart import Cart, CartStatus
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    PaymentStatus,
    CheckoutRequest,
    OrderRead,
    OrderItemRead,
)
from app.models.product import Product


class CheckoutService:
    def __init__(self, session: AsyncSession):
        self.session = session

    def generate_order_number(self) -> str:
        """Generate unique order number."""
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        random_suffix = secrets.token_hex(4).upper()
        return f"ORD-{timestamp}-{random_suffix}"

    async def validate_cart_for_checkout(self, cart: Cart) -> Tuple[bool, list[str]]:
        """Validate cart is ready for checkout."""
        errors = []

        if not cart:
            errors.append("Cart not found")
            return False, errors

        if cart.status != CartStatus.ACTIVE:
            errors.append(f"Cart status is {cart.status}, must be active")
            return False, errors

        if not cart.items or len(cart.items) == 0:
            errors.append("Cart is empty")
            return False, errors

        # Validate all products still exist and prices are current
        for item in cart.items:
            product_query = select(Product).where(Product.id == item.product_id)
            product_result = await self.session.execute(product_query)
            product = product_result.scalar_one_or_none()

            if not product:
                errors.append(f"Product {item.product_id} no longer available")
            elif product.price != item.unit_price:
                errors.append(
                    f"Price changed for {product.name}: was ${item.unit_price}, now ${product.price}"
                )

        return len(errors) == 0, errors

    async def calculate_order_totals(
        self, cart: Cart, tax_rate: float = 0.0, shipping_cost: float = 0.0
    ) -> dict:
        """Calculate order totals."""
        subtotal = sum(item.quantity * item.unit_price for item in cart.items)
        tax = subtotal * tax_rate
        total = subtotal + tax + shipping_cost

        return {
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "shipping_cost": round(shipping_cost, 2),
            "total": round(total, 2),
        }

    async def create_order_from_cart(
        self, cart: Cart, user_id: UUID, checkout_request: CheckoutRequest
    ) -> Order:
        """Create order from cart contents."""
        # Validate cart
        is_valid, errors = await self.validate_cart_for_checkout(cart)
        if not is_valid:
            raise ValueError(f"Cart validation failed: {', '.join(errors)}")

        # Calculate totals (you can enhance this with tax calculation logic)
        totals = await self.calculate_order_totals(cart)

        # Generate order number
        order_number = self.generate_order_number()

        # Ensure uniqueness
        while await self._order_number_exists(order_number):
            order_number = self.generate_order_number()

        # Create order
        order = Order(
            user_id=user_id,
            order_number=order_number,
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            subtotal=totals["subtotal"],
            tax=totals["tax"],
            shipping_cost=totals["shipping_cost"],
            total=totals["total"],
            shipping_name=checkout_request.shipping_address.name,
            shipping_email=checkout_request.shipping_address.email,
            shipping_phone=checkout_request.shipping_address.phone,
            shipping_address=checkout_request.shipping_address.address,
            shipping_city=checkout_request.shipping_address.city,
            shipping_state=checkout_request.shipping_address.state,
            shipping_postal_code=checkout_request.shipping_address.postal_code,
            shipping_country=checkout_request.shipping_address.country,
            notes=checkout_request.notes,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.session.add(order)
        await self.session.flush()

        # Create order items from cart items
        for cart_item in cart.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                product_name=cart_item.product.name,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=round(cart_item.quantity * cart_item.unit_price, 2),
                created_at=datetime.utcnow(),
            )
            self.session.add(order_item)

        # Mark cart as converted
        cart.status = CartStatus.CONVERTED
        cart.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(order, ["items"])

        return order

    async def _order_number_exists(self, order_number: str) -> bool:
        """Check if order number already exists."""
        query = select(Order).where(Order.order_number == order_number)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_order_by_id(self, order_id: UUID, user_id: UUID) -> Optional[Order]:
        """Get order by ID for specific user."""
        query = select(Order).where(Order.id == order_id, Order.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_order_by_number(
        self, order_number: str, user_id: UUID
    ) -> Optional[Order]:
        """Get order by order number for specific user."""
        query = select(Order).where(
            Order.order_number == order_number, Order.user_id == user_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_user_orders(
        self, user_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[Order]:
        """Get all orders for a user."""
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_order_status(
        self, order_id: UUID, user_id: UUID, status: OrderStatus
    ) -> Optional[Order]:
        """Update order status."""
        order = await self.get_order_by_id(order_id, user_id)
        if not order:
            return None

        order.status = status
        order.updated_at = datetime.utcnow()

        # Update timestamps based on status
        if status == OrderStatus.SHIPPED and not order.shipped_at:
            order.shipped_at = datetime.utcnow()
        elif status == OrderStatus.DELIVERED and not order.delivered_at:
            order.delivered_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def update_payment_status(
        self, order_id: UUID, user_id: UUID, payment_status: PaymentStatus
    ) -> Optional[Order]:
        """Update payment status."""
        order = await self.get_order_by_id(order_id, user_id)
        if not order:
            return None

        order.payment_status = payment_status
        order.updated_at = datetime.utcnow()

        if payment_status == PaymentStatus.PAID and not order.paid_at:
            order.paid_at = datetime.utcnow()
            # Auto-confirm order on payment
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CONFIRMED

        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def get_order_read_model(self, order: Order) -> OrderRead:
        """Convert order to read model."""
        order_items = []
        for item in order.items:
            order_item_read = OrderItemRead(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                created_at=item.created_at,
            )
            order_items.append(order_item_read)

        return OrderRead(
            id=order.id,
            user_id=order.user_id,
            order_number=order.order_number,
            status=order.status,
            payment_status=order.payment_status,
            subtotal=order.subtotal,
            tax=order.tax,
            shipping_cost=order.shipping_cost,
            total=order.total,
            shipping_name=order.shipping_name,
            shipping_email=order.shipping_email,
            shipping_phone=order.shipping_phone,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city,
            shipping_state=order.shipping_state,
            shipping_postal_code=order.shipping_postal_code,
            shipping_country=order.shipping_country,
            notes=order.notes,
            items=order_items,
            created_at=order.created_at,
            updated_at=order.updated_at,
            paid_at=order.paid_at,
            shipped_at=order.shipped_at,
            delivered_at=order.delivered_at,
        )
