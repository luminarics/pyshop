"""Unit tests for UserManager authentication logic."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from fastapi_users.exceptions import UserAlreadyExists
from app.auth.user_manager import UserManager, get_user_manager
from app.models.user import User, UserCreate


@pytest.mark.asyncio
class TestUserManager:
    """Test UserManager class functionality."""

    async def test_user_manager_has_secrets(self):
        """Test UserManager is configured with secret keys."""
        user_db = AsyncMock()
        manager = UserManager(user_db)

        assert manager.reset_password_token_secret is not None
        assert manager.verification_token_secret is not None
        assert manager.reset_password_token_secret == manager.verification_token_secret

    async def test_on_after_register_callback(self, capsys):
        """Test on_after_register callback is called after user registration."""
        user_db = AsyncMock()
        manager = UserManager(user_db)

        # Create a mock user
        user_id = uuid4()
        mock_user = User(
            id=user_id,
            email="test@example.com",
            username="testuser",
            hashed_password="hashed",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        )

        # Call the callback
        await manager.on_after_register(mock_user, request=None)

        # Check that the print statement was called (captured output)
        captured = capsys.readouterr()
        assert f"User {user_id} has registered." in captured.out

    async def test_user_manager_inheritance(self):
        """Test UserManager inherits from required base classes."""
        user_db = AsyncMock()
        manager = UserManager(user_db)

        # Check that UserManager has UUIDIDMixin methods
        assert hasattr(manager, "parse_id")

    async def test_get_user_manager_dependency(self):
        """Test get_user_manager dependency yields UserManager instance."""
        mock_user_db = AsyncMock()

        # Test the generator
        gen = get_user_manager(user_db=mock_user_db)
        manager = await gen.__anext__()

        assert isinstance(manager, UserManager)
        assert manager.user_db == mock_user_db

        # Ensure generator cleanup
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()


# Note: UserManager database integration tests are covered by the endpoint tests
# in test_auth_endpoints.py which test the full authentication flow including
# user creation, login, and password hashing through the API.
