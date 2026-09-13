"""使用者註冊/登入/JWT 簽發 — API routes.

TODO: no business logic here yet. Wire actual endpoints once product spec
for the auth module is ready.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginRequest, LoginResponse, UserInfo
from app.modules.auth.service import AuthService

security = HTTPBearer()
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_auth_service() -> AuthService:

    # 先DI 之後再改 DB + session
    return AuthService(
        repository = AuthRepository(session=None),
        settings = get_settings(),
    )

async def _get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    service: AuthService = Depends(get_auth_service),
) -> UserInfo:
    token = credentials.credentials
    payload = service.verify_token(token)

    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return UserInfo(
        username = username,
        role = payload.get("role", "admin"),
    )

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(request)

@router.get("/me", response_model=UserInfo)
async def me(current_user: UserInfo = Depends(_get_current_user)):
    return current_user