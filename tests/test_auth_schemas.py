"""Unit tests for authentication schemas and validators."""

import pytest
from pydantic import ValidationError
from app.models.user import UserCreate, UserUpdate, ChangePasswordRequest


class TestUserCreateValidation:
    """Test validation rules for UserCreate schema."""

    def test_valid_user_create(self):
        """Test creating user with valid data."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123",
        }
        user = UserCreate(**user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "SecurePass123"

    def test_username_min_length(self):
        """Test username must be at least 3 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab", email="test@example.com", password="SecurePass123"
            )
        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(e) for e in errors)

    def test_username_max_length(self):
        """Test username cannot exceed 50 characters."""
        long_username = "a" * 51
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username=long_username,
                email="test@example.com",
                password="SecurePass123",
            )
        errors = exc_info.value.errors()
        assert any("at most 50 characters" in str(e) for e in errors)

    def test_username_alphanumeric_only(self):
        """Test username validation for allowed characters."""
        # Valid usernames
        valid_usernames = ["user123", "test_user", "user-name", "User_Name-123"]
        for username in valid_usernames:
            user = UserCreate(
                username=username, email="test@example.com", password="SecurePass123"
            )
            assert user.username == username

    def test_username_invalid_characters(self):
        """Test username rejects special characters."""
        invalid_usernames = ["user@name", "user name", "user#123", "user.name"]
        for username in invalid_usernames:
            with pytest.raises(ValidationError) as exc_info:
                UserCreate(
                    username=username,
                    email="test@example.com",
                    password="SecurePass123",
                )
            errors = exc_info.value.errors()
            assert any(
                "can only contain letters, numbers, hyphens and underscores" in str(e)
                for e in errors
            )

    def test_invalid_email(self):
        """Test email validation."""
        invalid_emails = ["notanemail", "test@", "@example.com", "test@.com"]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                UserCreate(username="testuser", email=email, password="SecurePass123")

    def test_password_min_length(self):
        """Test password must be at least 8 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="testuser", email="test@example.com", password="Short1")
        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(e) for e in errors)

    def test_password_max_length(self):
        """Test password cannot exceed 128 characters."""
        long_password = "A1" + ("a" * 127)
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser", email="test@example.com", password=long_password
            )
        errors = exc_info.value.errors()
        assert any("at most 128 characters" in str(e) for e in errors)

    def test_password_requires_uppercase(self):
        """Test password must contain at least one uppercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser", email="test@example.com", password="lowercase123"
            )
        errors = exc_info.value.errors()
        assert any("at least one uppercase letter" in str(e) for e in errors)

    def test_password_requires_lowercase(self):
        """Test password must contain at least one lowercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser", email="test@example.com", password="UPPERCASE123"
            )
        errors = exc_info.value.errors()
        assert any("at least one lowercase letter" in str(e) for e in errors)

    def test_password_requires_digit(self):
        """Test password must contain at least one digit."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser", email="test@example.com", password="NoDigitsHere"
            )
        errors = exc_info.value.errors()
        assert any("at least one digit" in str(e) for e in errors)

    def test_password_valid_combinations(self):
        """Test valid password combinations."""
        valid_passwords = [
            "SecurePass123",
            "MyP@ssw0rd",
            "Test1234",
            "Abcdefg1",
            "P4ssW0rd!",
        ]
        for password in valid_passwords:
            user = UserCreate(
                username="testuser", email="test@example.com", password=password
            )
            assert user.password == password


class TestUserUpdateValidation:
    """Test validation rules for UserUpdate schema."""

    def test_update_with_none_values(self):
        """Test updating with all None values (no changes)."""
        update = UserUpdate()
        assert update.username is None
        assert update.email is None
        assert update.password is None

    def test_update_username_only(self):
        """Test updating only username."""
        update = UserUpdate(username="newusername")
        assert update.username == "newusername"
        assert update.email is None
        assert update.password is None

    def test_update_email_only(self):
        """Test updating only email."""
        update = UserUpdate(email="newemail@example.com")
        assert update.email == "newemail@example.com"
        assert update.username is None

    def test_update_password_only(self):
        """Test updating only password."""
        update = UserUpdate(password="NewPassword123")
        assert update.password == "NewPassword123"
        assert update.username is None

    def test_update_username_validation(self):
        """Test username validation in update."""
        # Valid update
        update = UserUpdate(username="valid_user-123")
        assert update.username == "valid_user-123"

        # Invalid update
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(username="invalid@user")
        errors = exc_info.value.errors()
        assert any(
            "can only contain letters, numbers, hyphens and underscores" in str(e)
            for e in errors
        )

    def test_update_password_validation(self):
        """Test password validation in update."""
        # Valid update
        update = UserUpdate(password="NewSecure123")
        assert update.password == "NewSecure123"

        # Missing uppercase
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(password="lowercase123")
        errors = exc_info.value.errors()
        assert any("at least one uppercase letter" in str(e) for e in errors)

        # Missing lowercase
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(password="UPPERCASE123")
        errors = exc_info.value.errors()
        assert any("at least one lowercase letter" in str(e) for e in errors)

        # Missing digit
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(password="NoDigitsHere")
        errors = exc_info.value.errors()
        assert any("at least one digit" in str(e) for e in errors)

    def test_update_email_validation(self):
        """Test email validation in update."""
        # Valid update
        update = UserUpdate(email="valid@example.com")
        assert update.email == "valid@example.com"

        # Invalid email
        with pytest.raises(ValidationError):
            UserUpdate(email="notanemail")


class TestChangePasswordRequestValidation:
    """Test validation rules for ChangePasswordRequest schema."""

    def test_valid_change_password(self):
        """Test valid password change request."""
        request = ChangePasswordRequest(
            current_password="OldPass123", new_password="NewPass456"
        )
        assert request.current_password == "OldPass123"
        assert request.new_password == "NewPass456"

    def test_new_password_requires_uppercase(self):
        """Test new password must contain uppercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="OldPass123", new_password="lowercase123"
            )
        errors = exc_info.value.errors()
        assert any("at least one uppercase letter" in str(e) for e in errors)

    def test_new_password_requires_lowercase(self):
        """Test new password must contain lowercase letter."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="OldPass123", new_password="UPPERCASE123"
            )
        errors = exc_info.value.errors()
        assert any("at least one lowercase letter" in str(e) for e in errors)

    def test_new_password_requires_digit(self):
        """Test new password must contain digit."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="OldPass123", new_password="NoDigitsHere"
            )
        errors = exc_info.value.errors()
        assert any("at least one digit" in str(e) for e in errors)

    def test_new_password_min_length(self):
        """Test new password minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(current_password="OldPass123", new_password="Short1")
        errors = exc_info.value.errors()
        assert any("at least 8 characters" in str(e) for e in errors)

    def test_new_password_max_length(self):
        """Test new password maximum length."""
        long_password = "A1" + ("a" * 127)
        with pytest.raises(ValidationError) as exc_info:
            ChangePasswordRequest(
                current_password="OldPass123", new_password=long_password
            )
        errors = exc_info.value.errors()
        assert any("at most 128 characters" in str(e) for e in errors)
