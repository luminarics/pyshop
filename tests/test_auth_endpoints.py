"""Integration tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from uuid import UUID


@pytest.mark.asyncio
class TestRegistrationEndpoint:
    """Test user registration endpoint."""

    async def test_register_valid_user(self, client: AsyncClient):
        """Test successful user registration."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == 201
        data = response.json()

        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert data["is_superuser"] is False
        assert data["is_verified"] is False
        assert "id" in data
        assert UUID(data["id"])  # Verify it's a valid UUID
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_register_duplicate_email(self, client: AsyncClient):
        """Test registration fails with duplicate email."""
        # Register first user
        await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user1",
                "password": "SecurePass123",
            },
        )

        # Attempt to register with same email
        response = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "username": "user2",
                "password": "SecurePass456",
            },
        )

        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "already exists" in detail or "user_already_exists" in detail

    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration fails with invalid email."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "notanemail",
                "username": "testuser",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == 422  # Validation error

    async def test_register_weak_password(self, client: AsyncClient):
        """Test registration fails with weak password."""
        # Missing uppercase
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "lowercase123",
            },
        )
        assert response.status_code == 422

        # Missing lowercase
        response = await client.post(
            "/auth/register",
            json={
                "email": "test2@example.com",
                "username": "testuser2",
                "password": "UPPERCASE123",
            },
        )
        assert response.status_code == 422

        # Missing digit
        response = await client.post(
            "/auth/register",
            json={
                "email": "test3@example.com",
                "username": "testuser3",
                "password": "NoDigitsHere",
            },
        )
        assert response.status_code == 422

    async def test_register_invalid_username(self, client: AsyncClient):
        """Test registration fails with invalid username."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "invalid@username",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == 422

    async def test_register_short_username(self, client: AsyncClient):
        """Test registration fails with too short username."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "ab",
                "password": "SecurePass123",
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
class TestLoginEndpoint:
    """Test login endpoint."""

    async def test_login_valid_credentials(self, client: AsyncClient):
        """Test successful login with valid credentials."""
        # Register user first
        await client.post(
            "/auth/register",
            json={
                "email": "login@example.com",
                "username": "loginuser",
                "password": "SecurePass123",
            },
        )

        # Login
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "login@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    async def test_login_invalid_password(self, client: AsyncClient):
        """Test login fails with invalid password."""
        # Register user
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "SecurePass123",
            },
        )

        # Attempt login with wrong password
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "test@example.com", "password": "WrongPassword123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 400
        assert "login_bad_credentials" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login fails for non-existent user."""
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "nonexistent@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 400

    async def test_login_requires_form_data(self, client: AsyncClient):
        """Test login requires form-encoded data (not JSON)."""
        # Register user
        await client.post(
            "/auth/register",
            json={
                "email": "formtest@example.com",
                "username": "formtest",
                "password": "SecurePass123",
            },
        )

        # Attempt login with JSON (should fail or not work as expected)
        response = await client.post(
            "/auth/jwt/login",
            json={"username": "formtest@example.com", "password": "SecurePass123"},
        )

        # This should fail because OAuth2 requires form data
        assert response.status_code != 200


@pytest.mark.asyncio
class TestLogoutEndpoint:
    """Test logout endpoint."""

    async def test_logout_with_valid_token(self, client: AsyncClient):
        """Test logout with valid authentication token."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "logout@example.com",
                "username": "logoutuser",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "logout@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Logout
        response = await client.post(
            "/auth/jwt/logout",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code in [200, 204]  # 204 No Content is also valid

    async def test_logout_without_token(self, client: AsyncClient):
        """Test logout fails without authentication token."""
        response = await client.post("/auth/jwt/logout")

        assert response.status_code == 401


@pytest.mark.asyncio
class TestProtectedEndpoints:
    """Test authentication protection on endpoints."""

    async def test_access_protected_route_with_token(self, client: AsyncClient):
        """Test accessing protected route with valid token."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "protected@example.com",
                "username": "protecteduser",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "protected@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Access protected endpoint (products)
        response = await client.get(
            "/products/",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

    async def test_access_protected_route_without_token(self, client: AsyncClient):
        """Test accessing protected route without token fails."""
        response = await client.get("/products/")

        assert response.status_code == 401

    async def test_access_protected_route_invalid_token(self, client: AsyncClient):
        """Test accessing protected route with invalid token fails."""
        response = await client.get(
            "/products/",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401

    async def test_access_protected_route_malformed_header(self, client: AsyncClient):
        """Test accessing protected route with malformed auth header fails."""
        # Missing 'Bearer' prefix
        response = await client.get(
            "/products/",
            headers={"Authorization": "some_token"},
        )

        assert response.status_code == 401


@pytest.mark.asyncio
class TestUserManagementEndpoints:
    """Test user management endpoints."""

    async def test_get_current_user(self, client: AsyncClient):
        """Test getting current user information."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "currentuser@example.com",
                "username": "currentuser",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "currentuser@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["email"] == "currentuser@example.com"
        assert data["username"] == "currentuser"
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_update_current_user(self, client: AsyncClient):
        """Test updating current user information."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "updateuser@example.com",
                "username": "updateuser",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "updateuser@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Update username
        response = await client.patch(
            "/users/me",
            json={"username": "newusername"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["username"] == "newusername"
        assert data["email"] == "updateuser@example.com"

    async def test_delete_requires_superuser(self, client: AsyncClient):
        """Test regular users cannot delete themselves (requires superuser)."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "deleteuser@example.com",
                "username": "deleteuser",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "deleteuser@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Attempt to delete user (should fail - requires superuser)
        response = await client.delete(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        # Regular users cannot delete themselves
        assert response.status_code == 403


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """Test complete authentication flows."""

    async def test_complete_registration_login_flow(self, client: AsyncClient):
        """Test complete flow: register -> login -> access protected resource."""
        # 1. Register
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "flowtest@example.com",
                "username": "flowtest",
                "password": "SecurePass123",
            },
        )
        assert register_response.status_code == 201

        # 2. Login
        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "flowtest@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Access protected resource
        products_response = await client.get(
            "/products/",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert products_response.status_code == 200

    async def test_multiple_concurrent_users(self, client: AsyncClient):
        """Test multiple users can register and login independently."""
        # Register user 1
        await client.post(
            "/auth/register",
            json={
                "email": "user1@example.com",
                "username": "user1",
                "password": "SecurePass123",
            },
        )

        # Register user 2
        await client.post(
            "/auth/register",
            json={
                "email": "user2@example.com",
                "username": "user2",
                "password": "SecurePass456",
            },
        )

        # Login user 1
        login1 = await client.post(
            "/auth/jwt/login",
            data={"username": "user1@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login1.status_code == 200
        token1 = login1.json()["access_token"]

        # Login user 2
        login2 = await client.post(
            "/auth/jwt/login",
            data={"username": "user2@example.com", "password": "SecurePass456"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login2.status_code == 200
        token2 = login2.json()["access_token"]

        # Verify tokens are different
        assert token1 != token2

        # Verify each user can access their own data
        me1 = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert me1.json()["username"] == "user1"

        me2 = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert me2.json()["username"] == "user2"

    async def test_logout_and_relogin_flow(self, client: AsyncClient):
        """Test user can logout and login again with same credentials."""
        # Register user
        await client.post(
            "/auth/register",
            json={
                "email": "relogin@example.com",
                "username": "reloginuser",
                "password": "SecurePass123",
            },
        )

        # First login
        login1 = await client.post(
            "/auth/jwt/login",
            data={"username": "relogin@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login1.status_code == 200
        token1 = login1.json()["access_token"]

        # Logout
        logout_response = await client.post(
            "/auth/jwt/logout",
            headers={"Authorization": f"Bearer {token1}"},
        )
        assert logout_response.status_code in [200, 204]

        # Login again
        login2 = await client.post(
            "/auth/jwt/login",
            data={"username": "relogin@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert login2.status_code == 200
        token2 = login2.json()["access_token"]

        # Verify new token works
        me_response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "relogin@example.com"

    async def test_profile_update_preserves_authentication(self, client: AsyncClient):
        """Test user can still authenticate after updating profile."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "profileupdate@example.com",
                "username": "originalname",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "profileupdate@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]

        # Update username
        update_response = await client.patch(
            "/users/me",
            json={"username": "updatedname"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert update_response.status_code == 200

        # Verify token still works after update
        me_response = await client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "updatedname"
        assert me_response.json()["email"] == "profileupdate@example.com"

        # Verify can login with updated credentials
        new_login = await client.post(
            "/auth/jwt/login",
            data={"username": "profileupdate@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert new_login.status_code == 200

    async def test_case_insensitive_email_login(self, client: AsyncClient):
        """Test login works with different email casing."""
        # Register with lowercase email
        await client.post(
            "/auth/register",
            json={
                "email": "casetest@example.com",
                "username": "caseuser",
                "password": "SecurePass123",
            },
        )

        # Try login with uppercase email
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "CASETEST@EXAMPLE.COM", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        # Should succeed (email lookup should be case-insensitive)
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_token_can_access_multiple_endpoints(self, client: AsyncClient):
        """Test a single token can access multiple protected endpoints."""
        # Register and login
        await client.post(
            "/auth/register",
            json={
                "email": "multiendpoint@example.com",
                "username": "multiuser",
                "password": "SecurePass123",
            },
        )

        login_response = await client.post(
            "/auth/jwt/login",
            data={"username": "multiendpoint@example.com", "password": "SecurePass123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Access multiple protected endpoints with same token
        products_response = await client.get("/products/", headers=headers)
        assert products_response.status_code == 200

        profile_response = await client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200

        # Verify consistent user data across endpoints
        assert profile_response.json()["email"] == "multiendpoint@example.com"
