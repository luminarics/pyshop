from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from app.models.user import User, UserRead, UserCreate, UserUpdate
from app.auth.user_manager import get_user_manager
from app.auth.backend import auth_backend
from uuid import UUID

fastapi_users = FastAPIUsers[User, UUID](  # type: ignore[type-var]
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

# Include auth routes (login, logout)
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Include registration route
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Include user management routes (get/update/delete current user)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Export current_user dependency for protecting routes
current_active_user = fastapi_users.current_user(active=True)
