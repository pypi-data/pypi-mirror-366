from enum import StrEnum
from typing import Callable, NotRequired, Sequence, TypedDict

from google.adk.agents import BaseAgent
from litestar import Controller
from litestar.handlers import ASGIRouteHandler
from pydantic import ConfigDict

from sparkden.models.knowledge import DataSourceType
from sparkden.models.shared import BaseModel, ExtraInfoMixin, base_model_config
from sparkden.services.knowledge.data_loaders.data_fetchers.base import (
    BaseDataFetcher,
)
from sparkden.services.knowledge.data_loaders.data_splitters.base import (
    BaseDataSplitter,
)


class ToolResponseStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class ToolResponse[ResultT](TypedDict):
    """The base tool response."""

    result: NotRequired[ResultT]
    """The result of the tool."""

    status: NotRequired[ToolResponseStatus]
    """The status of the tool response."""

    error: NotRequired[str]
    """The error message of the tool response."""


class UserApprovalRequest[RessourceT](BaseModel):
    """The user approval request."""

    resource: RessourceT
    """The resource requested to be approved."""

    reason: str
    """The reason for the approval request."""

    tool_call_id: str
    """The tool call id."""

    tool_call_name: str
    """The name of the tool call."""


class TaskStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"


class ProgressItemStatus(StrEnum):
    COMPLETED = "completed"
    RUNNING = "running"
    PENDING = "pending"


class KnowledgeDataSourceDefinition(ExtraInfoMixin, BaseModel):
    model_config = ConfigDict(
        **base_model_config,
        arbitrary_types_allowed=True,
    )
    id: str
    type: DataSourceType
    data_fetcher: BaseDataFetcher | None = None
    data_splitter: BaseDataSplitter | None = None


AssistantApiRoute = type[Controller] | ASGIRouteHandler


class Assistant(BaseModel):
    model_config = ConfigDict(
        **base_model_config,
        arbitrary_types_allowed=True,
    )

    id: str
    disabled: bool = False
    root_agent: BaseAgent
    api_routes: Sequence[AssistantApiRoute] | None = None
    callbacks: dict[str, Callable] | None = None
    data_sources: list[KnowledgeDataSourceDefinition] | None = None
    sequence: int = 9999
