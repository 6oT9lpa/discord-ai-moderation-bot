from typing import Any, Optional

from activity.server.dependencies import get_db
from activity.server.services.access_service import ActivityAccessService


class LogsService:
    def __init__(self) -> None:
        self._access_service = ActivityAccessService()

    async def list_logs(
        self,
        guild_id: int,
        source: str,
        event_type: Optional[str],
        query: str,
        limit: int,
        access_token: str,
    ) -> dict[str, list[dict[str, Any]]]:
        await self._access_service.ensure_panel_access(access_token, str(guild_id))
        return {
            "messages": [] if source == "audit" else await self._query_message_logs(guild_id, event_type, query, limit),
            "audit": [] if source == "messages" else await self._query_audit_logs(guild_id, event_type, query, limit),
        }

    async def _query_message_logs(
        self,
        guild_id: int,
        event_type: Optional[str],
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        clauses = ["guild_id = ?"]
        params: list[Any] = [guild_id]
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)
        if query.strip():
            clauses.append("(content LIKE ? OR author_name LIKE ?)")
            like = f"%{query.strip()}%"
            params.extend([like, like])
        params.append(limit)
        return await get_db().fetch_all(
            f"""
            SELECT * FROM message_logs
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            tuple(params),
        )

    async def _query_audit_logs(
        self,
        guild_id: int,
        event_type: Optional[str],
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        clauses = ["guild_id = ?"]
        params: list[Any] = [guild_id]
        if event_type:
            clauses.append("event_type = ?")
            params.append(event_type)
        if query.strip():
            clauses.append("(details LIKE ? OR actor_name LIKE ? OR target_name LIKE ?)")
            like = f"%{query.strip()}%"
            params.extend([like, like, like])
        params.append(limit)
        return await get_db().fetch_all(
            f"""
            SELECT * FROM guild_event_logs
            WHERE {' AND '.join(clauses)}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            tuple(params),
        )
