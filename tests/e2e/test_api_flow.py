"""E2E tests for API flows."""

import pytest
from playwright.sync_api import APIRequestContext
import time


@pytest.mark.e2e
class TestRegistrationE2E:
    """E2E tests for user registration."""

    def test_successful_user_registration(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test complete user registration flow."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_register_{timestamp}@example.com",
            "username": f"e2e_register_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Register user
        response = api_context.post(
            f"{base_url}/auth/register",
            data=user_data,
        )
        assert response.ok, f"Registration failed: {response.text()}"

        user = response.json()
        assert user["email"] == user_data["email"]
        assert user["username"] == user_data["username"]
        assert user["is_active"] is True
        assert user["is_superuser"] is False
        assert user["is_verified"] is False
        assert "id" in user
        assert "password" not in user
        assert "hashed_password" not in user

    def test_registration_with_duplicate_email_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test registration fails with duplicate email."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_duplicate_{timestamp}@example.com",
            "username": f"e2e_user1_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Register first user
        response1 = api_context.post(f"{base_url}/auth/register", data=user_data)
        assert response1.ok, "First registration should succeed"

        # Try to register with same email but different username
        user_data["username"] = f"e2e_user2_{timestamp}"
        response2 = api_context.post(f"{base_url}/auth/register", data=user_data)
        assert response2.status == 400, "Second registration should fail"

        error_detail = response2.json()["detail"].lower()
        assert "already exists" in error_detail or "user_already_exists" in error_detail

    def test_registration_with_invalid_email_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test registration fails with invalid email format."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": "not_a_valid_email",
            "username": f"e2e_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        response = api_context.post(f"{base_url}/auth/register", data=user_data)
        assert response.status == 422, "Should fail with validation error"

    def test_registration_with_weak_password_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test registration fails with weak password."""
        timestamp = int(time.time() * 1000)

        # Test password without uppercase
        response = api_context.post(
            f"{base_url}/auth/register",
            data={
                "email": f"test1_{timestamp}@example.com",
                "username": f"user1_{timestamp}",
                "password": "weakpassword123",
            },
        )
        assert response.status == 422, "Should reject password without uppercase"

        # Test password without digit
        response = api_context.post(
            f"{base_url}/auth/register",
            data={
                "email": f"test2_{timestamp}@example.com",
                "username": f"user2_{timestamp}",
                "password": "WeakPassword",
            },
        )
        assert response.status == 422, "Should reject password without digit"


@pytest.mark.e2e
class TestLoginE2E:
    """E2E tests for user login."""

    def test_successful_login_with_email(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test successful login using email."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_login_{timestamp}@example.com",
            "username": f"e2e_login_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Register user first
        reg_response = api_context.post(f"{base_url}/auth/register", data=user_data)
        assert reg_response.ok, "Registration should succeed"

        # Login with email
        login_response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={
                "username": user_data["email"],
                "password": user_data["password"],
            },
        )
        assert login_response.ok, f"Login failed: {login_response.text()}"

        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        assert len(token_data["access_token"]) > 0

    def test_login_with_wrong_password_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test login fails with incorrect password."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_wrongpw_{timestamp}@example.com",
            "username": f"e2e_wrongpw_user_{timestamp}",
            "password": "CorrectPassword123!",
        }

        # Register user
        api_context.post(f"{base_url}/auth/register", data=user_data)

        # Try to login with wrong password
        response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={
                "username": user_data["email"],
                "password": "WrongPassword123!",
            },
        )
        assert response.status == 400, "Login should fail with wrong password"
        assert "login_bad_credentials" in response.json()["detail"].lower()

    def test_login_with_nonexistent_user_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test login fails for non-existent user."""
        timestamp = int(time.time() * 1000)

        response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={
                "username": f"nonexistent_{timestamp}@example.com",
                "password": "SomePassword123!",
            },
        )
        assert response.status == 400, "Login should fail for non-existent user"

    def test_login_token_grants_access_to_protected_endpoints(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test login token allows access to protected resources."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_access_{timestamp}@example.com",
            "username": f"e2e_access_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Register and login
        api_context.post(f"{base_url}/auth/register", data=user_data)
        login_response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={"username": user_data["email"], "password": user_data["password"]},
        )
        token = login_response.json()["access_token"]

        # Access protected endpoint
        response = api_context.get(
            f"{base_url}/products/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.ok, "Should access protected endpoint with valid token"

        # Verify can get user profile
        profile_response = api_context.get(
            f"{base_url}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_response.ok, "Should access user profile"
        profile = profile_response.json()
        assert profile["email"] == user_data["email"]


@pytest.mark.e2e
class TestLogoutE2E:
    """E2E tests for user logout."""

    def test_successful_logout(self, api_context: APIRequestContext, base_url: str):
        """Test successful logout flow."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_logout_{timestamp}@example.com",
            "username": f"e2e_logout_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Register and login
        api_context.post(f"{base_url}/auth/register", data=user_data)
        login_response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={"username": user_data["email"], "password": user_data["password"]},
        )
        token = login_response.json()["access_token"]

        # Logout
        logout_response = api_context.post(
            f"{base_url}/auth/jwt/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_response.status in [200, 204], "Logout should succeed"

    def test_logout_without_token_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test logout fails without authentication token."""
        response = api_context.post(f"{base_url}/auth/jwt/logout")
        assert response.status == 401, "Logout should fail without token"

    def test_logout_with_invalid_token_fails(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test logout fails with invalid token."""
        response = api_context.post(
            f"{base_url}/auth/jwt/logout",
            headers={"Authorization": "Bearer invalid_token_here"},
        )
        assert response.status == 401, "Logout should fail with invalid token"


@pytest.mark.e2e
class TestCompleteAuthFlowE2E:
    """E2E tests for complete authentication flows."""

    def test_register_login_access_logout_flow(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test complete auth flow: register -> login -> access -> logout."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_complete_{timestamp}@example.com",
            "username": f"e2e_complete_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Step 1: Register
        reg_response = api_context.post(f"{base_url}/auth/register", data=user_data)
        assert reg_response.ok, "Registration should succeed"
        user = reg_response.json()
        assert user["email"] == user_data["email"]

        # Step 2: Login
        login_response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={"username": user_data["email"], "password": user_data["password"]},
        )
        assert login_response.ok, "Login should succeed"
        token = login_response.json()["access_token"]

        # Step 3: Access protected resources
        products_response = api_context.get(
            f"{base_url}/products/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert products_response.ok, "Should access products"

        profile_response = api_context.get(
            f"{base_url}/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert profile_response.ok, "Should access profile"
        assert profile_response.json()["username"] == user_data["username"]

        # Step 4: Logout
        logout_response = api_context.post(
            f"{base_url}/auth/jwt/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout_response.status in [200, 204], "Logout should succeed"

    def test_logout_and_relogin_flow(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test user can logout and login again."""
        timestamp = int(time.time() * 1000)
        user_data = {
            "email": f"e2e_relogin_{timestamp}@example.com",
            "username": f"e2e_relogin_user_{timestamp}",
            "password": "SecurePassword123!",
        }

        # Register and first login
        api_context.post(f"{base_url}/auth/register", data=user_data)
        login1_response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={"username": user_data["email"], "password": user_data["password"]},
        )
        token1 = login1_response.json()["access_token"]

        # Logout
        logout_response = api_context.post(
            f"{base_url}/auth/jwt/logout",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert logout_response.status in [200, 204]

        # Login again
        login2_response = api_context.post(
            f"{base_url}/auth/jwt/login",
            form={"username": user_data["email"], "password": user_data["password"]},
        )
        assert login2_response.ok, "Should be able to login again after logout"
        token2 = login2_response.json()["access_token"]

        # Verify new token works
        profile_response = api_context.get(
            f"{base_url}/users/me",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert profile_response.ok, "New token should work"
        assert profile_response.json()["email"] == user_data["email"]

    def test_protected_endpoint_requires_auth(
        self, api_context: APIRequestContext, base_url: str
    ):
        """Test protected endpoints require authentication."""
        response = api_context.get(f"{base_url}/products/")
        assert response.status == 401, "Should require authentication"

        response = api_context.get(f"{base_url}/users/me")
        assert response.status == 401, "Should require authentication"


@pytest.mark.e2e
class TestProductFlow:
    """Test product CRUD flow."""

    def test_create_and_list_products(
        self,
        api_context: APIRequestContext,
        base_url: str,
        auth_headers: dict[str, str],
    ):
        """Test creating and listing products."""
        product_data = {
            "name": "Test Product E2E",
            "price": 99.99,
        }

        # Create product
        response = api_context.post(
            f"{base_url}/products/",
            headers=auth_headers,
            data=product_data,
        )
        assert response.ok, f"Product creation failed: {response.text()}"
        created_product = response.json()
        assert created_product["name"] == product_data["name"]
        assert created_product["price"] == product_data["price"]
        assert "id" in created_product

        # List products
        response = api_context.get(
            f"{base_url}/products/",
            headers=auth_headers,
        )
        assert response.ok
        products = response.json()
        assert isinstance(products, list)
        assert len(products) > 0

    def test_get_product_by_id(
        self,
        api_context: APIRequestContext,
        base_url: str,
        auth_headers: dict[str, str],
    ):
        """Test retrieving a product by ID via list endpoint."""
        # Create product first
        product_data = {"name": "Get Test Product", "price": 49.99}
        response = api_context.post(
            f"{base_url}/products/",
            headers=auth_headers,
            data=product_data,
        )
        assert response.ok
        created_product = response.json()
        product_id = created_product["id"]

        # Get all products and verify our product is in the list
        response = api_context.get(
            f"{base_url}/products/",
            headers=auth_headers,
        )
        assert response.ok
        products = response.json()
        product = next((p for p in products if p["id"] == product_id), None)
        assert product is not None
        assert product["name"] == product_data["name"]

    def test_update_product(
        self,
        api_context: APIRequestContext,
        base_url: str,
        auth_headers: dict[str, str],
    ):
        """Test updating a product."""
        # Create product
        product_data = {"name": "Original Name", "price": 29.99}
        response = api_context.post(
            f"{base_url}/products/",
            headers=auth_headers,
            data=product_data,
        )
        assert response.ok
        product_id = response.json()["id"]

        # Update product (using PUT not PATCH)
        updated_data = {"name": "Updated Name", "price": 39.99}
        response = api_context.put(
            f"{base_url}/products/{product_id}",
            headers=auth_headers,
            data=updated_data,
        )
        assert response.ok
        updated_product = response.json()
        assert updated_product["name"] == updated_data["name"]
        assert updated_product["price"] == updated_data["price"]

    def test_delete_product(
        self,
        api_context: APIRequestContext,
        base_url: str,
        auth_headers: dict[str, str],
    ):
        """Test deleting a product."""
        # Create product
        product_data = {"name": "To Be Deleted", "price": 19.99}
        response = api_context.post(
            f"{base_url}/products/",
            headers=auth_headers,
            data=product_data,
        )
        assert response.ok
        product_id = response.json()["id"]

        # Delete product
        response = api_context.delete(
            f"{base_url}/products/{product_id}",
            headers=auth_headers,
        )
        assert response.ok

        # Verify product is deleted by checking it's not in the list
        response = api_context.get(
            f"{base_url}/products/",
            headers=auth_headers,
        )
        assert response.ok
        products = response.json()
        deleted_product = next((p for p in products if p["id"] == product_id), None)
        assert deleted_product is None


@pytest.mark.e2e
class TestHealthCheck:
    """Test health check endpoint."""

    def test_health_check(self, api_context: APIRequestContext, base_url: str):
        """Test health check endpoint is accessible."""
        response = api_context.get(f"{base_url}/healthz")
        assert response.ok
        health_data = response.json()
        assert health_data["status"] == "ok"
