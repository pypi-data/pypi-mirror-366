from typing import Any

from google.adk.agents.callback_context import CallbackContext

from .models import ProgressItemStatus


def update_progress_info(
    ctx: CallbackContext,
    key: str,
    status: ProgressItemStatus = ProgressItemStatus.RUNNING,
) -> None:
    progress_info = ctx.state.get("progress_info") or {}
    progress_info[key] = status
    ctx.state["progress_info"] = progress_info


def reset_progress_info(ctx: CallbackContext, key: str | None = None) -> None:
    progress_info = ctx.state.get("progress_info")
    if key and progress_info:
        progress_info.pop(key, None)
        ctx.state["progress_info"] = progress_info
    else:
        ctx.state["progress_info"] = None


def update_state_if_necessary(ctx: CallbackContext, delta: dict[str, Any]) -> None:
    for key, value in delta.items():
        if ctx.state.get(key) != value:
            ctx.state[key] = value
