from datetime import datetime
from typing import cast, override

from google.adk.sessions import Session
from google.adk.sessions.base_session_service import ListSessionsResponse
from google.adk.sessions.database_session_service import (
    DatabaseSessionService,
    StorageSession,
)


class SessionService(DatabaseSessionService):
    @override
    async def list_sessions(
        self,
        *,
        app_name: str | None = None,
        user_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> ListSessionsResponse:
        with self.database_session_factory() as session:
            query = session.query(StorageSession)
            if app_name is not None:
                query = query.filter(StorageSession.app_name == app_name)
            results = (
                query.filter(StorageSession.user_id == user_id)
                .order_by(StorageSession.update_time.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            sessions = []
            for storage_session in results:
                session = Session(
                    app_name=storage_session.app_name,
                    user_id=user_id,
                    id=storage_session.id,
                    state=storage_session.state,
                    last_update_time=cast(
                        datetime, storage_session.update_time
                    ).timestamp(),
                )
                sessions.append(session)
            return ListSessionsResponse(sessions=sessions)

    async def sessions_total_count(
        self, *, app_name: str | None = None, user_id: str
    ) -> int:
        with self.database_session_factory() as session:
            query = session.query(StorageSession)
            if app_name is not None:
                query = query.filter(StorageSession.app_name == app_name)
            return query.filter(StorageSession.user_id == user_id).count()
