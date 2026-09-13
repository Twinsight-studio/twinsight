
from app.core.schema import CamelModel


class UserInfo(CamelModel):
    """User info returned by the `/auth/me` endpoint."""

    username: str
    role: str = "admin"

class LoginRequest(CamelModel):
    """Request body for login endpoint."""

    username: str
    password: str

class LoginResponse(CamelModel):
    """Response body for login endpoint."""

    access_token: str
    token_type: str = "bearer"