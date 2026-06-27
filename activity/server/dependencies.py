from typing import Optional

from fastapi import Header, HTTPException

from application.services import ServerRolePurposeService
from infrastructure.config import get_config
from infrastructure.database.connection import DatabaseManager
from infrastructure.database.repositories import ServerRolePurposeRepository


_db: Optional[DatabaseManager] = None
_role_purpose_service: Optional[ServerRolePurposeService] = None


async def initialize_activity_dependencies() -> None:
    global _db, _role_purpose_service
    config = get_config()
    _db = DatabaseManager(config.database_url)
    await _db.initialize()
    _role_purpose_service = ServerRolePurposeService(ServerRolePurposeRepository(_db))


async def shutdown_activity_dependencies() -> None:
    if _db:
        await _db.close()


def get_db() -> DatabaseManager:
    if _db is None:
        raise HTTPException(status_code=503, detail="Database is not initialized")
    return _db


def get_role_purpose_service() -> ServerRolePurposeService:
    if _role_purpose_service is None:
        raise HTTPException(status_code=503, detail="Role purpose service is not initialized")
    return _role_purpose_service


def require_bearer_token(authorization: str = Header(default="")) -> str:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Bearer token is required")
    return authorization[len(prefix):].strip()
