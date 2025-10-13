from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.password import PasswordHelper
from sqlmodel import UUID

from app.auth.user_manager import get_user_manager
from app.models.user import (
    User,
    UserRead,
    UserCreate,
    UserUpdate,
    ChangePasswordRequest,
)
from app.core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.storage import save_avatar, delete_avatar

router = APIRouter()

# Configure bearer transport
bearer_transport = BearerTransport(tokenUrl="/auth/jwt/login")


# Configure JWT Strategy
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET_KEY,
        lifetime_seconds=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        token_audience=["fastapi-users:auth"],
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](  # type: ignore[type-var]
    get_user_manager,
    [auth_backend],
)

# Include fastapi-users routers
router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Export current_user dependencies
current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_user_optional = fastapi_users.current_user(optional=True)


@router.get("/me")
async def get_me(user: User = Depends(current_active_user)):
    return user


@router.post("/change-password", response_model=UserRead)
async def change_password(
    password_data: ChangePasswordRequest,
    user: User = Depends(current_active_user),
):
    """
    Change user password with current password verification.
    """
    password_helper = PasswordHelper()

    # Verify current password
    is_valid, _ = password_helper.verify_and_update(
        password_data.current_password, user.hashed_password
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Check if new password is different from current
    is_same, _ = password_helper.verify_and_update(
        password_data.new_password, user.hashed_password
    )

    if is_same:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Hash new password
    new_hashed_password = password_helper.hash(password_data.new_password)

    # Update user in database
    from app.database import async_session
    from sqlalchemy import select

    async with async_session() as session:
        # Get user from this session
        result = await session.execute(select(User).where(User.id == user.id))
        db_user = result.scalar_one()

        # Update password
        db_user.hashed_password = new_hashed_password

        await session.commit()
        await session.refresh(db_user)

        return db_user


@router.post("/upload-avatar", response_model=UserRead)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
):
    """
    Upload user avatar image.
    """
    from app.database import async_session
    from sqlalchemy import select

    # Delete old avatar if exists
    if user.avatar_url:
        delete_avatar(user.avatar_url)

    # Save new avatar
    avatar_url = await save_avatar(file, str(user.id))

    # Update user avatar_url in database
    async with async_session() as session:
        # Get user from this session
        result = await session.execute(select(User).where(User.id == user.id))
        db_user = result.scalar_one()

        # Update avatar_url
        db_user.avatar_url = avatar_url

        await session.commit()
        await session.refresh(db_user)

        return db_user


@router.delete("/delete-avatar", response_model=UserRead)
async def delete_user_avatar(user: User = Depends(current_active_user)):
    """
    Delete user avatar image.
    """
    from app.database import async_session
    from sqlalchemy import select

    # Delete avatar file
    if user.avatar_url:
        delete_avatar(user.avatar_url)

        # Update user in database
        async with async_session() as session:
            # Get user from this session
            result = await session.execute(select(User).where(User.id == user.id))
            db_user = result.scalar_one()

            # Clear avatar_url
            db_user.avatar_url = None

            await session.commit()
            await session.refresh(db_user)

            return db_user

    return user
