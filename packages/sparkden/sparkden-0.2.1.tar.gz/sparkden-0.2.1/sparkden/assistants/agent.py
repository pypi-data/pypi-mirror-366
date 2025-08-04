from typing import Any, Callable

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import BaseTool, ToolContext

from .helpers import (
    reset_progress_info,
    update_progress_info,
)
from .models import ToolResponse


class Agent(LlmAgent):
    def __init__(
        self,
        /,
        **data,
    ) -> None:
        # Define callback types and their default methods
        callback_types = {
            "before_agent": self.default_before_agent_callback,
            "after_agent": self.default_after_agent_callback,
            "before_tool": self.default_before_tool_callback,
            "after_tool": self.default_after_tool_callback,
            "before_model": self.default_before_model_callback,
            "after_model": self.default_after_model_callback,
        }

        # Process each callback type
        for callback_type, default_callback in callback_types.items():
            callback_key = f"{callback_type}_callback"
            user_callback = data.pop(callback_key, None)

            # Wrap the callback if provided, otherwise use default
            if user_callback is not None:
                if callback_type.startswith("before"):
                    wrapped_callback = self.wrap_before_callback(
                        default_callback, user_callback
                    )
                elif callback_type.startswith("after"):
                    wrapped_callback = self.wrap_after_callback(
                        default_callback, user_callback
                    )
                else:
                    raise ValueError(f"Invalid callback type: {callback_type}")
            else:
                wrapped_callback = default_callback

            data[callback_key] = wrapped_callback

        super().__init__(**data)

    @staticmethod
    def default_before_agent_callback(
        callback_context: CallbackContext,
    ) -> None:
        update_progress_info(callback_context, callback_context.agent_name)
        return None

    @staticmethod
    def default_after_agent_callback(
        callback_context: CallbackContext,
    ) -> None:
        return None

    @staticmethod
    def default_before_tool_callback(
        tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
    ) -> None:
        return None

    @staticmethod
    def default_after_tool_callback(
        tool: BaseTool,
        args: dict[str, Any],
        tool_context: ToolContext,
        tool_response: ToolResponse,
    ) -> None:
        return None

    @staticmethod
    def default_before_model_callback(
        callback_context: CallbackContext, llm_request: LlmRequest
    ) -> None:
        return None

    @staticmethod
    def default_after_model_callback(
        callback_context: CallbackContext, llm_response: LlmResponse
    ) -> None:
        reset_progress_info(callback_context)
        return None

    @staticmethod
    def wrap_after_callback(
        default_callback: Callable, callback: Callable | None
    ) -> Callable:
        def wrapped_callback(*args: Any, **kwargs: Any) -> Any:
            default_callback(*args, **kwargs)
            return callback(*args, **kwargs) if callback else None

        return wrapped_callback

    @staticmethod
    def wrap_before_callback(
        default_callback: Callable, callback: Callable | None
    ) -> Callable:
        def wrapped_callback(*args: Any, **kwargs: Any) -> Any:
            result = callback(*args, **kwargs) if callback else None
            if result is None:
                default_callback(*args, **kwargs)
            return result

        return wrapped_callback
