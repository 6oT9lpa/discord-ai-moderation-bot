from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.domain.server_role_purpose import ServerRolePurpose


@dataclass(frozen=True)
class ServerRolePurposeDTO:
    guild_id: int
    purpose: ServerRolePurpose
    role_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
