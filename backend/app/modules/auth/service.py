"""使用者註冊/登入/JWT 簽發 — service layer (business logic).

TODO: implement. Services call into repository.py for persistence and/or
provider clients for external APIs; routers must not talk to the DB directly.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import get_settings
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import LoginRequest, LoginResponse
class AuthService:
    def __init__(
        self,
        repository: AuthRepository,
        settings=None,
    ) -> None:
        self._repository = repository
        self._settings = settings or get_settings()

    # 發行JWT
    def _issue_token(self, username: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": username,
            "role": "admin",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._settings.jwt_expires_minutes)).timestamp()),
        }
        return jwt.encode(
            payload,
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    # 登入驗證
    async def login(self, request: LoginRequest) -> LoginResponse:
        username = request.username
        password = request.password

        if username != self._settings.auth_username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if password != self._settings.auth_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        token = self._issue_token(username)
        return LoginResponse(
            access_token=token,
            token_type="bearer",
        )

    # 驗證JWT
    def verify_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
            )
        except jwt.PyJWTError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

    
