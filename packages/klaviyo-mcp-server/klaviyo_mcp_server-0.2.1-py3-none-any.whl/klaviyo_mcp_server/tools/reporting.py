from typing import Annotated, Literal

from pydantic import Field

from klaviyo_mcp_server.models.reporting import ReportPresetTimeframe, ReportTimeframe
from klaviyo_mcp_server.utils.param_types import (
    FilterConfig,
    FilterParam,
    UnionWrapper,
    create_filter_models,
)
from klaviyo_mcp_server.utils.utils import (
    clean_result,
    get_filter_string,
    get_klaviyo_client,
    get_campaigns_threaded,
    get_flow_details,
)
from klaviyo_mcp_server.utils.tool_decorator import mcp_tool


CampaignStatistic = Literal[
    "bounce_rate",
    "bounced",
    "bounced_or_failed",
    "bounced_or_failed_rate",
    "click_rate",
    "click_to_open_rate",
    "clicks",
    "clicks_unique",
    "conversion_rate",
    "conversion_uniques",
    "conversions",
    "delivered",
    "delivery_rate",
    "failed",
    "failed_rate",
    "open_rate",
    "opens",
    "opens_unique",
    "recipients",
    "spam_complaint_rate",
    "spam_complaints",
    "unsubscribe_rate",
    "unsubscribe_uniques",
    "unsubscribes",
]

CampaignValueStatistic = Literal[
    "average_order_value",
    "conversion_value",
    "revenue_per_recipient",
]

GetCampaignReportFilter = create_filter_models(
    [
        FilterConfig(
            field="send_channel",
            operators=["equals", "contains-any"],
            value_type=Literal["email", "sms", "push-notification"],
        ),
        FilterConfig(
            field="campaign_id", operators=["equals", "contains-any"], value_type=str
        ),
        FilterConfig(
            field="campaign_message_id",
            operators=["equals", "contains-any"],
            value_type=str,
        ),
    ]
)


@mcp_tool(has_writes=False)
def get_campaign_report(
    statistics: Annotated[
        list[CampaignStatistic], Field(description="List of statistics to query for.")
    ],
    conversion_metric_id: Annotated[
        str,
        Field(
            description="ID of the metric to be used for conversion statistics. You can get available metrics IDs using the get_metrics tool and just requesting the 'name' field. If a specific metric is not requested, use the ID of the metric named 'Placed Order'. If it doesn't exist, use any metric."
        ),
    ],
    value_statistics: Annotated[
        list[CampaignValueStatistic],
        Field(
            description="List of value statistics to query for. If you see an error about the conversion metric not supporting querying for values data, try again and leave this as an empty list."
        ),
    ] = None,
    timeframe: Annotated[
        UnionWrapper[ReportTimeframe],
        Field(
            ReportPresetTimeframe(key="last_30_days"),
            description="The timeframe to query for data within. The max length a timeframe can be is 1 year. If unspecified, use 1 year.",
        ),
    ] = UnionWrapper(value=ReportPresetTimeframe(key="last_30_days")),
    filters: FilterParam[GetCampaignReportFilter] = None,
) -> dict:
    """Returns a performance report for all campaigns. To get details about the returned campaigns (such as name, status, and creation date) use get_campaign.
    Ask the user if they would like to use an MCP prompt to analyze the data before continuing, and then end there.
    """

    # TODO: add elicit to ask if they would like to use a prompt instead of just doing docstring (INTL-14966)

    # TODO: add filtering by tag (INTL-14939)

    all_statistics = [*statistics, *(value_statistics or [])]

    body = {
        "data": {
            "type": "campaign-values-report",
            "attributes": {
                "statistics": all_statistics,
                "conversion_metric_id": conversion_metric_id,
                "timeframe": timeframe.value.model_dump(),
                "filter": get_filter_string(filters),
            },
        }
    }

    client = get_klaviyo_client()
    response = client.Reporting.query_campaign_values(body)

    clean_result(response["data"])

    # Get campaign details
    campaign_ids = [
        result["groupings"]["campaign_id"]
        for result in response["data"]["attributes"]["results"]
    ]

    # Currently, multiple requests takes too long for large reports
    if len(campaign_ids) < 20:
        try:
            # Get campaign details including campaign names, and insert into results
            campaign_details = get_campaigns_threaded(campaign_ids)
            for i, result in enumerate(response["data"]["attributes"]["results"]):
                result["campaign_details"] = campaign_details[i]

            return response
        except Exception:
            # If we can't get the campaign details, just return the response without them
            return response
    else:
        return response


FlowStatistic = CampaignStatistic
FlowValueStatistic = CampaignValueStatistic

GetFlowReportFilter = create_filter_models(
    [
        FilterConfig(
            field="send_channel",
            operators=["equals", "contains-any"],
            value_type=Literal["email", "sms", "push-notification"],
        ),
        FilterConfig(
            field="flow_id", operators=["equals", "contains-any"], value_type=str
        ),
        FilterConfig(
            field="flow_message_id",
            operators=["equals", "contains-any"],
            value_type=str,
        ),
    ]
)


@mcp_tool(has_writes=False)
def get_flow_report(
    statistics: Annotated[
        list[FlowStatistic], Field(description="List of statistics to query for.")
    ],
    conversion_metric_id: Annotated[
        str,
        Field(
            description="ID of the metric to be used for conversion statistics. You can get available metrics IDs using the get_metrics tool and just requesting the 'name' field. If a specific metric is not requested, use the ID of the metric named 'Placed Order'. If it doesn't exist, use any metric."
        ),
    ],
    value_statistics: Annotated[
        list[FlowValueStatistic],
        Field(
            description="List of value statistics to query for. If you see an error about the conversion metric not supporting querying for values data, try again and leave this as an empty list."
        ),
    ] = None,
    timeframe: Annotated[
        UnionWrapper[ReportTimeframe],
        Field(
            ReportPresetTimeframe(key="last_30_days"),
            description="The timeframe to query for data within. The max length a timeframe can be is 1 year. If unspecified, use 1 year.",
        ),
    ] = UnionWrapper(value=ReportPresetTimeframe(key="last_30_days")),
    filters: FilterParam[GetFlowReportFilter] = None,
) -> dict:
    """Returns a performance report for all flows.
    Ask the user if they would like to use an MCP prompt to analyze the data before continuing, and then end there.
    """
    all_statistics = [*statistics, *(value_statistics or [])]
    body = {
        "data": {
            "type": "flow-values-report",
            "attributes": {
                "statistics": all_statistics,
                "conversion_metric_id": conversion_metric_id,
                "timeframe": timeframe.value.model_dump(),
                "filter": get_filter_string(filters),
            },
        }
    }

    response = get_klaviyo_client().Reporting.query_flow_values(body)
    clean_result(response["data"])

    flow_ids = [
        result["groupings"]["flow_id"]
        for result in response["data"]["attributes"]["results"]
    ]

    try:
        flow_details = get_flow_details(flow_ids)
        for i, result in enumerate(response["data"]["attributes"]["results"]):
            result["flow_details"] = flow_details[i]

        return response
    except Exception:
        # If we can't get the flow details, just return the response without them
        return response
