import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.product import Product
from app.models.cart import Cart, CartItem, CartStatus
from app.models.order import Order, OrderStatus, PaymentStatus
from uuid import uuid4
from datetime import datetime


@pytest.mark.asyncio
async def test_checkout_creates_order(client: AsyncClient, async_session: AsyncSession):
    """Test successful checkout creates an order."""
    # Create a test user
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed_password",
        username="testuser",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    async_session.add(user)

    # Create test products
    product1 = Product(name="Product 1", price=10.99)
    product2 = Product(name="Product 2", price=20.50)
    async_session.add(product1)
    async_session.add(product2)
    await async_session.commit()
    await async_session.refresh(product1)
    await async_session.refresh(product2)

    # Create cart with items
    cart = Cart(
        id=uuid4(),
        user_id=user.id,
        status=CartStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(cart)
    await async_session.commit()

    cart_item1 = CartItem(
        id=uuid4(),
        cart_id=cart.id,
        product_id=product1.id,
        quantity=2,
        unit_price=product1.price,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    cart_item2 = CartItem(
        id=uuid4(),
        cart_id=cart.id,
        product_id=product2.id,
        quantity=1,
        unit_price=product2.price,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(cart_item1)
    async_session.add(cart_item2)
    await async_session.commit()

    # Mock the current user dependency
    from app.main import app as fastapi_app
    from app.routers.profile import current_active_user

    async def override_current_user():
        return user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    # Prepare checkout request
    checkout_data = {
        "shipping_address": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "12345",
            "country": "USA",
        },
        "notes": "Please deliver to front door",
    }

    # Perform checkout
    response = await client.post("/orders/checkout", json=checkout_data)

    fastapi_app.dependency_overrides.clear()

    # Assertions
    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["order_number"].startswith("ORD-")
    assert data["status"] == OrderStatus.PENDING
    assert data["payment_status"] == PaymentStatus.PENDING
    assert data["subtotal"] == 42.48  # (10.99 * 2) + 20.50
    assert data["total"] == 42.48
    assert data["shipping_name"] == "John Doe"
    assert data["shipping_email"] == "john@example.com"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_checkout_empty_cart_fails(
    client: AsyncClient, async_session: AsyncSession
):
    """Test checkout with empty cart fails."""
    # Create a test user
    user = User(
        id=uuid4(),
        email="test2@example.com",
        hashed_password="hashed_password",
        username="testuser2",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    async_session.add(user)
    await async_session.commit()

    # Create empty cart
    cart = Cart(
        id=uuid4(),
        user_id=user.id,
        status=CartStatus.ACTIVE,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(cart)
    await async_session.commit()

    # Mock auth
    from app.main import app as fastapi_app
    from app.routers.profile import current_active_user

    async def override_current_user():
        return user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    checkout_data = {
        "shipping_address": {
            "name": "John Doe",
            "email": "john@example.com",
            "address": "123 Main St",
            "city": "Anytown",
            "postal_code": "12345",
            "country": "USA",
        }
    }

    response = await client.post("/orders/checkout", json=checkout_data)
    fastapi_app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "empty" in response.json()["detail"]["errors"][0].lower()


@pytest.mark.asyncio
async def test_get_orders_list(client: AsyncClient, async_session: AsyncSession):
    """Test retrieving user's orders list."""
    # Create user
    user = User(
        id=uuid4(),
        email="test3@example.com",
        hashed_password="hashed_password",
        username="testuser3",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    async_session.add(user)

    # Create test product
    product = Product(name="Test Product", price=15.00)
    async_session.add(product)
    await async_session.commit()
    await async_session.refresh(product)

    # Create orders
    from app.services.checkout_service import CheckoutService

    checkout_service = CheckoutService(async_session)
    order_number1 = checkout_service.generate_order_number()
    order_number2 = checkout_service.generate_order_number()

    order1 = Order(
        id=uuid4(),
        user_id=user.id,
        order_number=order_number1,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=15.00,
        tax=0.0,
        shipping_cost=0.0,
        total=15.00,
        shipping_name="Test User",
        shipping_email="test@example.com",
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    order2 = Order(
        id=uuid4(),
        user_id=user.id,
        order_number=order_number2,
        status=OrderStatus.CONFIRMED,
        payment_status=PaymentStatus.PAID,
        subtotal=30.00,
        tax=0.0,
        shipping_cost=0.0,
        total=30.00,
        shipping_name="Test User",
        shipping_email="test@example.com",
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(order1)
    async_session.add(order2)
    await async_session.commit()

    # Mock auth
    from app.main import app as fastapi_app
    from app.routers.profile import current_active_user

    async def override_current_user():
        return user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    response = await client.get("/orders")
    fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_order_by_id(client: AsyncClient, async_session: AsyncSession):
    """Test retrieving a specific order by ID."""
    # Create user
    user = User(
        id=uuid4(),
        email="test4@example.com",
        hashed_password="hashed_password",
        username="testuser4",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    async_session.add(user)

    # Create product
    product = Product(name="Test Product", price=25.00)
    async_session.add(product)
    await async_session.commit()
    await async_session.refresh(product)

    # Create order
    from app.services.checkout_service import CheckoutService

    checkout_service = CheckoutService(async_session)
    order_number = checkout_service.generate_order_number()

    order = Order(
        id=uuid4(),
        user_id=user.id,
        order_number=order_number,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=25.00,
        tax=0.0,
        shipping_cost=0.0,
        total=25.00,
        shipping_name="Test User",
        shipping_email="test@example.com",
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    # Mock auth
    from app.main import app as fastapi_app
    from app.routers.profile import current_active_user

    async def override_current_user():
        return user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    response = await client.get(f"/orders/{order.id}")
    fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(order.id)
    assert data["order_number"] == order_number


@pytest.mark.asyncio
async def test_cancel_order(client: AsyncClient, async_session: AsyncSession):
    """Test cancelling a pending order."""
    # Create user
    user = User(
        id=uuid4(),
        email="test5@example.com",
        hashed_password="hashed_password",
        username="testuser5",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )
    async_session.add(user)
    await async_session.commit()

    # Create order
    from app.services.checkout_service import CheckoutService

    checkout_service = CheckoutService(async_session)
    order_number = checkout_service.generate_order_number()

    order = Order(
        id=uuid4(),
        user_id=user.id,
        order_number=order_number,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=25.00,
        tax=0.0,
        shipping_cost=0.0,
        total=25.00,
        shipping_name="Test User",
        shipping_email="test@example.com",
        shipping_address="123 Test St",
        shipping_city="Test City",
        shipping_postal_code="12345",
        shipping_country="USA",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    async_session.add(order)
    await async_session.commit()
    await async_session.refresh(order)

    # Mock auth
    from app.main import app as fastapi_app
    from app.routers.profile import current_active_user

    async def override_current_user():
        return user

    fastapi_app.dependency_overrides[current_active_user] = override_current_user

    response = await client.post(f"/orders/{order.id}/cancel")
    fastapi_app.dependency_overrides.clear()

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == OrderStatus.CANCELLED
