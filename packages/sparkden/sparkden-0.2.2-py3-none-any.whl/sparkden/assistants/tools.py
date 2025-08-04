from google.adk.tools import ToolContext
from pydantic import ValidationError

from sparkden.models.shared import BaseModel

from .models import (
    ToolResponse,
    ToolResponseStatus,
    UserApprovalRequest,
)


def update_approval_request_state(
    *,
    resource: dict,
    reason: str,
    tool_call_id: str,
    tool_call_name: str,
    tool_context: ToolContext,
) -> ToolResponse:
    tool_context.state["user_approval_request"] = UserApprovalRequest(
        resource=resource,
        reason=reason,
        tool_call_id=tool_call_id,
        tool_call_name=tool_call_name,
    ).model_dump()
    tool_context.actions.skip_summarization = True
    return ToolResponse(
        result=None,
        status=ToolResponseStatus.PENDING,
    )


def update_approval_result_state(
    *,
    resource: dict | None,
    state_key: str,
    tool_context: ToolContext,
) -> None:
    tool_context.state[state_key] = resource
    tool_context.state["user_approval_request"] = None


def validate_tool_param(
    tool_name: str, param_value: dict, param_type: type[BaseModel]
) -> ToolResponse | None:
    try:
        param_type.model_validate(param_value)
    except ValidationError as e:
        error_str = f"""Invoking `{tool_name}()` failed as the input parameters validation failed:
{str(e)}
You could retry calling this tool, but it is IMPORTANT for you to follow the input parameters schema."""
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=error_str,
        )
    return None
