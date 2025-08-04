from _typeshed import Incomplete
from enum import StrEnum
from gllm_agents.utils.logger_manager import LoggerManager as LoggerManager
from typing import Any

logger: Incomplete
METADATA_STATUS_KEY: str
TIME_KEY: str

class Kind(StrEnum):
    """Constants for metadata kind values."""
    AGENT_STEP = 'agent_step'
    FINAL_RESPONSE = 'final_response'
    AGENT_DEFAULT = 'agent_default'

class Status(StrEnum):
    """Constants for metadata status values."""
    RUNNING = 'running'
    FINISHED = 'finished'
    STOPPED = 'stopped'

def detect_agent_step_content(content: str, default_kind: str, tool_calls: Any | None = None) -> str:
    """Detect if content corresponds to agent step patterns from LangGraph.

    Args:
        content: The content to detect.
        default_kind: The default kind to return if the content does not match any of the patterns.
        tool_calls: The tool calls to detect.

    Returns:
        The kind of the content.
    """
def create_metadata(content: str = '', kind: str = ..., status: str = ..., tool_calls: Any | None = None, is_final: bool = False, time: float | None = None) -> dict[str, Any]:
    """Create metadata for A2A responses with content-based message.

    Args:
        content: The content to create metadata for.
        kind: The kind of the content.
        status: The status of the content.
        tool_calls: The tool calls to create metadata for.
        is_final: Whether the content is final.
        time: The time of the content.

    Returns:
        The metadata for the content.
    """
