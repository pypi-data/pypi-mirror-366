from typing import Any

import websockets
from temporalio import activity
from temporalio.exceptions import ApplicationError

from .observability import log_with_context, logger

activity.logger.logger = logger


class ActivityLogger:
    """Enables consistent formatting for function logs."""

    def __init__(self) -> None:
        self._logger = activity.logger

    def _log(
        self,
        level: str,
        message: str,
        **kwargs: Any,
    ) -> None:
        try:
            activity.info()
            getattr(self._logger, level)(
                message,
                extra={
                    "extra_fields": {
                        **kwargs,
                        "client_log": True,
                    },
                },
            )
        except RuntimeError:
            log_with_context(level.upper(), message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._log("debug", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        self._log("error", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        self._log("critical", message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log an exception with traceback (equivalent to `logging.exception`)."""
        kwargs["exc_info"] = True
        self._log("exception", message, **kwargs)


log = ActivityLogger()

function_info = activity.info
heartbeat = activity.heartbeat
function = activity


class NonRetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=True)


class RetryableError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, non_retryable=False)


__all__ = [
    "NonRetryableError",
    "RetryableError",
    "function_info",
    "heartbeat",
    "log",
    "mcp_progress",
]


def mcp_progress(
    progress: float,
    total: float | None = None,
    message: str | None = None,
) -> bool:
    """Send an MCP-compliant progress information.

    Example:

    .. code-block:: python

        # Basic progress
        mcp_progress(progress=25, total=100, message="Loading data")

        # Progress update
        mcp_progress(progress=50, total=100, message="Processing data")

    Args:
        progress (float): Current progress value (must increase with each call)
        total (float, optional): Total progress value if known
        message (str, optional): Human-readable progress message

    Returns:
        bool: True if the progress information was sent successfully, False otherwise

    """
    try:
        info = activity.info()

        mcp_data = {
            "_mcp_progress": True,
            "progress": float(progress),
            "activity_id": info.activity_id,
            "activity_type": info.activity_type,
        }

        # Add optional fields
        if total is not None:
            mcp_data["total"] = float(total)

        if message is not None:
            mcp_data["message"] = str(message)

        heartbeat(mcp_data)

        log.debug(
            "MCP progress sent: progress=%s, total=%s, message=%s",
            progress,
            total,
            message,
        )

    except Exception:
        log.exception("Error sending MCP progress")
        return False
    else:
        return True


def current_workflow() -> Any:
    return activity.Context.current().info


def _extract_response_info(chunk: Any) -> tuple[Any, str | None, Any, bool]:
    """Extract response information from a chunk.

    Returns:
        tuple: (final_response, response_id, usage_info, has_completion)
    """
    final_response = None
    response_id = None
    usage_info = None
    has_completion = False

    # Extract final response from completion events
    if hasattr(chunk, "response") and chunk.response:
        final_response = chunk.response
        if hasattr(chunk.response, "id"):
            response_id = chunk.response.id
        has_completion = True

        # Extract usage information
        if hasattr(chunk.response, "usage") and chunk.response.usage:
            usage_info = chunk.response.usage

    # Extract usage from standalone usage events
    elif hasattr(chunk, "usage") and chunk.usage:
        usage_info = chunk.usage

    return final_response, response_id, usage_info, has_completion


def _extract_text_content(chunk_dict: dict) -> str:
    """Extract text content from a chunk dictionary.

    Returns:
        str: Extracted text content
    """
    # Simple text extraction - just look for delta fields
    # This works for both responses API and chat completion
    delta = chunk_dict.get("delta", "")
    if isinstance(delta, str) and delta:
        return delta

    # Legacy chat completion support
    if "choices" in chunk_dict:
        choices = chunk_dict["choices"]
        if choices and len(choices) > 0:
            choice = choices[0]
            if "delta" in choice and "content" in choice["delta"]:
                content = choice["delta"]["content"]
                if isinstance(content, str):
                    return content

    return ""


def _build_websocket_url(api_address: str, workflow_id: str, run_id: str) -> str:
    """Build the WebSocket URL for streaming.

    Returns:
        str: The WebSocket URL
    """
    protocol = "ws" if api_address.startswith("localhost") else "wss"
    return f"{protocol}://{api_address}/stream/ws/agent?agentId={workflow_id}&runId={run_id}"


def _get_activity_info() -> dict:
    """Get current activity information.

    Returns:
        dict: Activity information
    """
    return {
        "activityId": activity.info().activity_id,
        "workflowId": activity.info().workflow_id,
        "runId": activity.info().workflow_run_id,
        "activityType": activity.info().activity_type,
        "taskQueue": activity.info().task_queue,
    }


async def _process_openai_stream(data: Any, websocket: Any) -> dict:
    """Process OpenAI stream data and send to WebSocket.

    Returns:
        dict: Collected data including events, text, and metadata
    """
    collected_events = []
    collected_text = ""
    final_response = None
    response_id = None
    usage_info = None
    has_completion = False

    for chunk in data:
        raw_chunk_json = chunk.model_dump_json()
        heartbeat(raw_chunk_json)
        await websocket.send(message=raw_chunk_json)

        # Store the raw event
        chunk_dict = chunk.model_dump()
        collected_events.append(chunk_dict)

        # Extract response information
        chunk_final_response, chunk_response_id, chunk_usage_info, chunk_has_completion = _extract_response_info(chunk)

        if chunk_final_response:
            final_response = chunk_final_response
        if chunk_response_id:
            response_id = chunk_response_id
        if chunk_usage_info:
            usage_info = chunk_usage_info
        has_completion = has_completion or chunk_has_completion

        # Extract text content
        collected_text += _extract_text_content(chunk_dict)

    return {
        "events": collected_events,
        "text": collected_text,
        "final_response": final_response,
        "response_id": response_id,
        "usage": usage_info,
        "has_completion": has_completion,
    }


async def stream_to_websocket(
    api_address: str | None = None,
    data: Any = None,
) -> Any:
    """Stream data to Restack Engine WebSocket API endpoint.

    This function streams data to the Restack Engine and returns a comprehensive result
    with collected events, concatenated text, and metadata. It handles both simple text
    extraction and full response aggregation in a single, robust implementation.

    Args:
        api_address (str): The address of the Restack Engine API.
        data (Any): The streamed data from an OpenAI-compatible API or a JSON dict.

    Returns:
        dict: A dictionary containing:
            - events: List of all collected events (raw chunks)
            - text: Concatenated text content from delta events
            - event_count: Number of events collected
            - final_response: Complete aggregated response (if available)
            - response_id: Response ID if available
            - usage: Usage statistics if available
            - has_completion: Whether a completion event was received

    Example:
        >>> from openai import OpenAI
        >>> client = OpenAI()
        >>> # Stream a response
        >>> stream = client.responses.create(
        ...     model="gpt-4o", input="Hello, how are you?", stream=True
        ... )
        >>> # Stream to websocket and get comprehensive result
        >>> result = await stream_to_websocket(data=stream)
        >>> # Access the concatenated text
        >>> print(result["text"])
        >>> # Access the complete reconstructed response
        >>> if result["final_response"]:
        ...     print(f"Complete response: {result['final_response']}")
        >>> # Access metadata
        >>> print(f"Response ID: {result['response_id']}")
        >>> print(f"Usage: {result['usage']}")
    """
    if api_address is None:
        api_address = "localhost:9233"

    info = _get_activity_info()
    websocket_url = _build_websocket_url(api_address, info["workflowId"], info["runId"])

    try:
        async with websockets.connect(websocket_url) as websocket:
            try:
                heartbeat(info)

                # Check if module name is openai (no need to import openai package in this library)
                if data.__class__.__module__.startswith("openai"):
                    result = await _process_openai_stream(data, websocket)
                else:
                    # Handle non-OpenAI data (placeholder for future implementation)
                    result = {
                        "events": [],
                        "text": "",
                        "final_response": None,
                        "response_id": None,
                        "usage": None,
                        "has_completion": False,
                    }
            finally:
                # Ensure the WebSocket connection is closed
                await websocket.send(message="[DONE]")
                await websocket.close()

            # Validate streaming completed successfully
            if not result["has_completion"]:
                log.warning(
                    "Streaming completed without final response event",
                )

            return {
                "events": result["events"],
                "text": result["text"],
                "event_count": len(result["events"]),
                "final_response": result["final_response"],
                "response_id": result["response_id"],
                "usage": result["usage"],
                "has_completion": result["has_completion"],
            }
    except Exception as e:
        error_message = (
            f"Error with restack stream to websocket: {e}"
        )
        log.exception(error_message)
        raise ApplicationError(error_message) from e
