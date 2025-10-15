"""Unit tests for JWT authentication backend."""

import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.auth.backend import get_jwt_strategy, bearer_transport, auth_backend
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES


class TestJWTStrategy:
    """Test JWT strategy configuration."""

    def test_jwt_strategy_configuration(self):
        """Test JWT strategy is properly configured."""
        strategy = get_jwt_strategy()

        assert strategy.secret == SECRET_KEY
        assert strategy.lifetime_seconds == ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @pytest.mark.asyncio
    async def test_jwt_strategy_rejects_invalid_token(self):
        """Test JWT strategy rejects invalid tokens."""
        strategy = get_jwt_strategy()

        invalid_token = "invalid.token.here"

        decoded = await strategy.read_token(invalid_token, ["fastapi-users:auth"])
        assert decoded is None

    def test_jwt_token_decode_expired(self):
        """Test manually decoding expired JWT tokens."""
        from jose import exceptions
        import time

        # Create token with immediate expiration (use Unix timestamp)
        expired_timestamp = int(time.time()) - 10  # 10 seconds ago
        expired_data = {
            "sub": "test-user-id",
            "aud": ["fastapi-users:auth"],
            "exp": expired_timestamp,
        }
        expired_token = jwt.encode(expired_data, SECRET_KEY, algorithm="HS256")

        # Manual decode should fail for expired token
        with pytest.raises(exceptions.ExpiredSignatureError):
            jwt.decode(
                expired_token,
                SECRET_KEY,
                algorithms=["HS256"],
                audience="fastapi-users:auth",
            )

    def test_jwt_token_wrong_signature(self):
        """Test manually decoding tokens with wrong signature."""
        from jose import exceptions

        wrong_key = "wrong_secret_key_12345"
        token_data = {
            "sub": "test-user-id",
            "aud": ["fastapi-users:auth"],
            "exp": datetime.now() + timedelta(hours=1),
        }
        wrong_token = jwt.encode(token_data, wrong_key, algorithm="HS256")

        # Decode with correct key should fail
        with pytest.raises((exceptions.JWSError, exceptions.JWTError)):
            jwt.decode(wrong_token, SECRET_KEY, algorithms=["HS256"])


class TestBearerTransport:
    """Test Bearer token transport configuration."""

    def test_bearer_transport_exists(self):
        """Test bearer transport is configured."""
        assert bearer_transport is not None

    def test_bearer_transport_scheme_name(self):
        """Test bearer transport uses OAuth2 scheme."""
        # BearerTransport uses OAuth2PasswordBearer internally
        assert hasattr(bearer_transport, "scheme")


class TestAuthBackend:
    """Test authentication backend configuration."""

    def test_auth_backend_name(self):
        """Test auth backend has correct name."""
        assert auth_backend.name == "jwt"

    def test_auth_backend_transport(self):
        """Test auth backend uses bearer transport."""
        assert auth_backend.transport == bearer_transport

    def test_auth_backend_strategy_callable(self):
        """Test auth backend strategy is callable."""
        assert callable(auth_backend.get_strategy)

    def test_auth_backend_creates_strategy(self):
        """Test auth backend can create JWT strategy."""
        strategy = auth_backend.get_strategy()
        assert strategy is not None
        assert hasattr(strategy, "write_token")
        assert hasattr(strategy, "read_token")
