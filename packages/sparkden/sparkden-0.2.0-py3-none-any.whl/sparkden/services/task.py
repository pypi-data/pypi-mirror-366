from datetime import datetime
from typing import Any, AsyncGenerator
from zoneinfo import ZoneInfo

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.genai import types
from litestar.response import ServerSentEventMessage
from sparkden.adk.session_service import SessionService
from sparkden.assistants import assistants
from sparkden.models.shared import OffsetPagination

from ..models.task import Task, TaskItem, TaskSSEData


class TaskService:
    def __init__(self, adk_session_service: SessionService, user_id: str):
        self.adk_session_service = adk_session_service
        self.user_id = user_id

    async def list_tasks(
        self, *, limit: int = 30, offset: int = 0
    ) -> OffsetPagination[TaskItem]:
        list_response = await self.adk_session_service.list_sessions(
            user_id=self.user_id, limit=limit, offset=offset
        )
        total_count = await self.adk_session_service.sessions_total_count(
            user_id=self.user_id
        )
        return OffsetPagination(
            items=[
                TaskItem.from_session(session) for session in list_response.sessions
            ],
            total=total_count,
            limit=limit,
            offset=offset,
        )

    async def create_task(
        self, *, title: str, assistant_id: str, task_id: str | None = None
    ) -> Task:
        session = await self.adk_session_service.create_session(
            app_name=assistant_id,
            user_id=self.user_id,
            state={
                "title": title,
                "status": "idle",
                "start_time": datetime.now(tz=ZoneInfo("Asia/Shanghai")).isoformat(),
            },
            session_id=task_id,
        )
        return Task.from_session(session)

    async def get_task(self, *, assistant_id: str, task_id: str) -> Task | None:
        session = await self.adk_session_service.get_session(
            app_name=assistant_id, user_id=self.user_id, session_id=task_id
        )
        if session is None:
            return None
        return Task.from_session(session)

    async def run_task(
        self,
        *,
        assistant_id: str,
        task_id: str,
        message: str | types.Part,
        state_delta: dict[str, Any] | None = None,
    ) -> AsyncGenerator[ServerSentEventMessage, None]:
        assistant = assistants.get_assistant(assistant_id)
        if assistant is None:
            raise ValueError(f"Assistant {assistant_id} not found")

        runner = Runner(
            app_name=assistant_id,
            agent=assistant.root_agent,
            session_service=self.adk_session_service,
        )

        new_message = types.Content(
            role="user",
            parts=[
                message if isinstance(message, types.Part) else types.Part(text=message)
            ],
        )

        accumulated_text = ""
        async for event in runner.run_async(
            user_id=self.user_id,
            session_id=task_id,
            new_message=new_message,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            state_delta=state_delta,
        ):
            event_name, event_data = None, None
            if event.partial:
                event_name = "message/partial"
                accumulated_event = event.model_copy(deep=True)
                if (
                    accumulated_event.content
                    and accumulated_event.content.parts
                    and accumulated_event.content.parts[0].text
                ):
                    accumulated_text += accumulated_event.content.parts[0].text
                    accumulated_event.content.parts[0].text = accumulated_text
                # TODO: support partial function call
                event_data = TaskSSEData.from_event(
                    accumulated_event,
                ).model_dump_json(exclude_none=True, by_alias=True)
            else:
                accumulated_text = ""
                event_name = "message"
                event_data = TaskSSEData.from_event(
                    event,
                ).model_dump_json(
                    exclude_none=True,
                    by_alias=True,
                )
            yield ServerSentEventMessage(
                data=event_data,
                event=event_name,
            )
