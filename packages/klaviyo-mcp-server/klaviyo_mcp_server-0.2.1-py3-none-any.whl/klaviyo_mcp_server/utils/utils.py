import os
from datetime import datetime
from typing import Any, Callable, List

from klaviyo_api import KlaviyoAPI
from openapi_client.api_arg_options import USE_DICTIONARY_FOR_RESPONSE_DATA
from fastmcp.server.dependencies import get_context
from functools import partial
from klaviyo_mcp_server.version import __version__

USER_AGENT_HEADER = "klaviyo-mcp"


class ModelData:
    """Holds data about an AI model using the MCP server."""

    model: str | None = None


current_model_data = ModelData()
"""Data about the AI model currently being used."""


def get_klaviyo_client() -> KlaviyoAPI:
    private_key = os.getenv("PRIVATE_API_KEY")
    if not private_key:
        raise ValueError(
            "Please set PRIVATE_API_KEY environment variable to your Klaviyo private API key"
        )
    client = KlaviyoAPI(private_key, options={USE_DICTIONARY_FOR_RESPONSE_DATA: True})

    try:
        # get_context will return a RuntimeError if the context is not available for some reason
        ctx = get_context()
        client_info = ctx.session._client_params.clientInfo
    except RuntimeError:
        client_info = None

    user_agent = f"{USER_AGENT_HEADER}/{__version__}"
    if client_info and client_info.name and client_info.version:
        user_agent += f" {client_info.name}/{client_info.version}"

    if current_model_data.model:
        user_agent += f" {current_model_data.model}"

    client.api_client.user_agent = user_agent
    return client


def clean_result(data: dict | list):
    if isinstance(data, list):
        for d in data:
            clean_result(d)
    else:
        data.pop("relationships", None)
        data.pop("links", None)


def get_filter_string(filters: list[Any] | None) -> str | None:
    if not filters:
        return None

    formatted_filters = []
    for filter in filters:
        if hasattr(filter, "value"):
            value = _get_filter_value_string(filter.value)
            formatted_filters.append(f"{filter.operator}({filter.field},{value})")
        else:
            # unary operator
            formatted_filters.append(f"{filter.operator}({filter.field})")
    return ",".join(formatted_filters)


def _get_filter_value_string(value: Any) -> str:
    """Transforms a value into its string representation for the filter query param."""
    if isinstance(value, list):
        return f"[{','.join([_get_filter_value_string(v) for v in value])}]"
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, bool):
        return str(value).lower()
    return repr(value)


def make_parallel_requests_threaded(
    request_functions: List[Callable], max_workers: int = 10
) -> List[Any]:
    """
    Makes parallel requests using threads.

    Args:
        request_functions: List of functions that make API calls
        max_workers: Maximum number of worker threads and requests per second

    Returns:
        List of results in the same order as functions
    """

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(request_function) for request_function in request_functions
        ]
        # If these requests use Klaviyo API, they handle retries internally
        # If some are being rate limited they will do their own exponential backoff, so we don't need to handle that here. Since we are using threads, a thread will wait for the next request to start from its client if the rate limit is exceeded.
        return [future.result() for future in futures]


def get_campaigns_threaded(ids: List[str], max_workers: int = 10) -> List[dict]:
    """
    Gets campaigns using threads.

    Args:
        max_workers: Maximum number of worker threads and requests per second
    """
    client = get_klaviyo_client()

    def get_campaign(id: str):
        result = client.Campaigns.get_campaign(
            id,
            include=[
                "tags",
            ],
            fields_campaign=["name", "status", "send_time"],
            fields_tag=["name"],
        )
        clean_result(result["data"])
        return result["data"]

    return make_parallel_requests_threaded(
        [partial(get_campaign, id) for id in ids], max_workers
    )


def get_flow_details(flow_ids: List[str]):
    """
    Use the get_flows endpoint to get flow details from a list of flow_ids.
    Processes batches of 50 IDs sequentially.

    Args:
        flow_ids: List of flow IDs to get details for

    Returns:
        List of flow details
    """
    if not flow_ids:
        return []

    flows = {id: None for id in flow_ids}
    client = get_klaviyo_client()
    batch_size = 50

    # Process batches of 50 IDs sequentially
    for i in range(0, len(flow_ids), batch_size):
        batch_ids = flow_ids[i : i + batch_size]

        # Create filter with format: any(id,['id1','id2','id3'])
        batch_id_filter = "any(id,[" + ",".join([f"'{id}'" for id in batch_ids]) + "])"
        batch_flows = client.Flows.get_flows(
            filter=batch_id_filter,
            include=[
                "tags",
            ],
            fields_flow=["name", "status", "created"],
            fields_tag=["name"],
        )

        if "data" in batch_flows:
            # Add results to flows dict
            for flow in batch_flows["data"]:
                clean_result(flow)
                flows[flow["id"]] = flow

    # Return results in the same order as flow_ids
    return [flows[id] for id in flow_ids]
