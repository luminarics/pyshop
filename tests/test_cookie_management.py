import pytest
from fastapi import FastAPI, Request, Response
from httpx import AsyncClient, ASGITransport
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette.routing import Route

from app.utils.cookies import (
    CookieManager,
    SecureCookie,
    CookieStore,
    create_session_cookie,
    create_user_preference_cookie,
    create_remember_me_cookie,
)
from app.middleware.session import SessionMiddleware, CookieCleanupMiddleware


class TestCookieManager:
    """Test the core cookie management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CookieManager(secret_key="test_secret_key_32_characters_long")

    def test_signature_creation_and_verification(self):
        """Test HMAC signature creation and verification."""
        value = "test_session_id_12345"
        signature = self.manager.create_signature(value)

        assert len(signature) == 64  # SHA256 hex digest length
        assert self.manager.verify_signature(value, signature)

        # Test invalid signature
        invalid_signature = "invalid_signature"
        assert not self.manager.verify_signature(value, invalid_signature)

        # Test tampered value
        tampered_value = "tampered_session_id"
        assert not self.manager.verify_signature(tampered_value, signature)

    def test_encryption_and_decryption(self):
        """Test value encryption and decryption."""
        original_value = "sensitive_session_data_12345"

        # Encrypt value
        encrypted_value = self.manager.encrypt_value(original_value)
        assert encrypted_value != original_value
        assert len(encrypted_value) > len(original_value)

        # Decrypt value
        decrypted_value = self.manager.decrypt_value(encrypted_value)
        assert decrypted_value == original_value

        # Test invalid encrypted data
        invalid_encrypted = "invalid_encrypted_data"
        assert self.manager.decrypt_value(invalid_encrypted) is None

    def test_data_serialization(self):
        """Test JSON data serialization and deserialization."""
        test_data = {
            "user_id": "12345",
            "preferences": {"theme": "dark", "language": "en"},
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # Serialize
        serialized = self.manager.serialize_data(test_data)
        assert isinstance(serialized, str)
        assert "user_id" in serialized

        # Deserialize
        deserialized = self.manager.deserialize_data(serialized)
        assert deserialized == test_data

        # Test invalid JSON
        invalid_json = "invalid json data"
        assert self.manager.deserialize_data(invalid_json) is None


class TestSecureCookie:
    """Test secure cookie functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = CookieManager(secret_key="test_secret_key_32_characters_long")
        self.secure_cookie = SecureCookie(
            name="test_cookie",
            manager=self.manager,
            encrypt=True,
            sign=True,
        )

    @pytest.mark.asyncio
    async def test_secure_cookie_operations(self):
        """Test setting and getting secure cookies."""
        app = FastAPI()

        @app.get("/set-cookie")
        async def set_cookie_endpoint(response: Response):
            self.secure_cookie.set_cookie(response, "test_session_value")
            return {"status": "cookie_set"}

        @app.get("/get-cookie")
        async def get_cookie_endpoint(request: Request):
            cookie_value = self.secure_cookie.get_cookie(request)
            return {"cookie_value": cookie_value}

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        # Set cookie
        response = await client.get("/set-cookie")
        assert response.status_code == 200
        assert "test_cookie" in response.cookies

        # Get cookie
        cookies = {"test_cookie": response.cookies["test_cookie"]}
        response = await client.get("/get-cookie", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["cookie_value"] == "test_session_value"

        await client.aclose()

    @pytest.mark.asyncio
    async def test_signed_cookie_tamper_protection(self):
        """Test that tampered signed cookies are rejected."""
        app = FastAPI()

        @app.get("/get-cookie")
        async def get_cookie_endpoint(request: Request):
            cookie_value = self.secure_cookie.get_cookie(request)
            return {"cookie_value": cookie_value}

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        # Try with tampered cookie
        tampered_cookie = "tampered_value.invalid_signature"
        cookies = {"test_cookie": tampered_cookie}
        response = await client.get("/get-cookie", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["cookie_value"] is None

        await client.aclose()

    @pytest.mark.asyncio
    async def test_dictionary_cookie_storage(self):
        """Test storing dictionary data in cookies."""
        app = FastAPI()

        @app.get("/set-dict-cookie")
        async def set_dict_cookie_endpoint(response: Response):
            test_data = {
                "user_id": "123",
                "role": "admin",
                "preferences": {"theme": "dark"},
            }
            self.secure_cookie.set_cookie(response, test_data)
            return {"status": "cookie_set"}

        @app.get("/get-dict-cookie")
        async def get_dict_cookie_endpoint(request: Request):
            cookie_data = self.secure_cookie.get_cookie_data(request)
            return {"cookie_data": cookie_data}

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        # Set dictionary cookie
        response = await client.get("/set-dict-cookie")
        assert response.status_code == 200

        # Get dictionary cookie
        cookies = {"test_cookie": response.cookies["test_cookie"]}
        response = await client.get("/get-dict-cookie", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["cookie_data"]["user_id"] == "123"
        assert data["cookie_data"]["role"] == "admin"

        await client.aclose()


class TestCookieStore:
    """Test cookie store functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cookie_store = CookieStore(
            cookie_name="test_store",
            secret_key="test_secret_key_32_characters_long",
        )

    @pytest.mark.asyncio
    async def test_cookie_store_operations(self):
        """Test cookie store set, get, and delete operations."""
        app = FastAPI()

        @app.get("/store-value")
        async def store_value_endpoint(request: Request, response: Response):
            self.cookie_store.set_value(request, response, "username", "john_doe")
            return {"status": "value_stored"}

        @app.get("/get-value")
        async def get_value_endpoint(request: Request):
            username = self.cookie_store.get_value(request, "username")
            return {"username": username}

        @app.get("/delete-value")
        async def delete_value_endpoint(request: Request, response: Response):
            self.cookie_store.delete_value(request, response, "username")
            return {"status": "value_deleted"}

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        # Store value
        response = await client.get("/store-value")
        assert response.status_code == 200
        cookies = dict(response.cookies)

        # Get value
        response = await client.get("/get-value", cookies=cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "john_doe"

        # Delete value
        response = await client.get("/delete-value", cookies=cookies)
        assert response.status_code == 200
        updated_cookies = dict(response.cookies)

        # Verify deletion
        response = await client.get("/get-value", cookies=updated_cookies)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] is None

        await client.aclose()


class TestEnhancedSessionMiddleware:
    """Test enhanced session middleware with secure cookies."""

    @pytest.mark.asyncio
    async def test_secure_session_middleware(self):
        """Test that enhanced session middleware uses secure cookies."""

        async def endpoint(request):
            session_id = getattr(request.state, "session_id", None)
            return JSONResponse({"session_id": session_id})

        app = Starlette(
            routes=[Route("/cart", endpoint)],
            middleware=[
                Middleware(SessionMiddleware, secure=False)  # False for testing
            ],
        )

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        response = await client.get("/cart")
        assert response.status_code == 200
        data = response.json()

        # Should have session ID
        assert "session_id" in data
        assert data["session_id"] is not None

        # Should set secure cookie
        assert "pyshop_cart_session" in response.cookies
        cookie_value = response.cookies["pyshop_cart_session"]

        # Cookie should be signed (contains signature after dot)
        assert "." in cookie_value

        await client.aclose()

    @pytest.mark.asyncio
    async def test_cookie_validation_on_subsequent_requests(self):
        """Test that subsequent requests validate existing cookies."""

        async def endpoint(request):
            session_id = getattr(request.state, "session_id", None)
            return JSONResponse({"session_id": session_id})

        app = Starlette(
            routes=[Route("/cart", endpoint)],
            middleware=[Middleware(SessionMiddleware, secure=False)],
        )

        client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

        # First request - gets new session
        response1 = await client.get("/cart")
        session_id1 = response1.json()["session_id"]
        cookie_value = response1.cookies["pyshop_cart_session"]

        # Second request with valid cookie
        cookies = {"pyshop_cart_session": cookie_value}
        response2 = await client.get("/cart", cookies=cookies)
        session_id2 = response2.json()["session_id"]

        # Should use same session ID
        assert session_id1 == session_id2

        await client.aclose()

    @pytest.mark.asyncio
    async def test_tampered_cookie_generates_new_session(self):
        """Test that tampered cookies result in new session generation."""

        async def endpoint(request):
            session_id = getattr(request.state, "session_id", None)
            return JSONResponse({"session_id": session_id})

        app = Starlette(
            routes=[Route("/cart", endpoint)],
            middleware=[Middleware(SessionMiddleware, secure=False)],
        )

        # Use separate clients to avoid cookie jar interference
        client1 = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
        # First request - gets new session
        response1 = await client1.get("/cart")
        session_id1 = response1.json()["session_id"]
        await client1.aclose()

        # New client with tampered cookie
        client2 = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test", cookies={}
        )
        # Second request with tampered cookie
        tampered_cookie = "tampered_session_id.invalid_signature"
        cookies = {"pyshop_cart_session": tampered_cookie}
        response2 = await client2.get("/cart", cookies=cookies)
        session_id2 = response2.json()["session_id"]

        # Should generate new session ID due to invalid cookie
        assert session_id1 != session_id2
        assert session_id2 is not None

        await client2.aclose()


class TestCookieFactoryFunctions:
    """Test cookie factory functions."""

    def test_create_session_cookie(self):
        """Test session cookie factory."""
        session_cookie = create_session_cookie()
        assert session_cookie.name == "pyshop_cart_session"
        assert session_cookie.httponly is True
        assert session_cookie.samesite == "lax"
        assert session_cookie.sign is True
        assert session_cookie.encrypt is False

    def test_create_user_preference_cookie(self):
        """Test user preference cookie factory."""
        pref_cookie = create_user_preference_cookie()
        assert pref_cookie.cookie.name == "pyshop_preferences"
        assert pref_cookie.cookie.httponly is False  # Accessible to JS
        assert pref_cookie.cookie.encrypt is True
        assert pref_cookie.cookie.sign is True

    def test_create_remember_me_cookie(self):
        """Test remember-me cookie factory."""
        remember_cookie = create_remember_me_cookie()
        assert remember_cookie.name == "pyshop_remember"
        assert remember_cookie.httponly is True
        assert remember_cookie.samesite == "strict"
        assert remember_cookie.encrypt is True
        assert remember_cookie.sign is True
