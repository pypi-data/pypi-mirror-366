# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Mapping, cast
from datetime import date
from typing_extensions import Literal

import httpx

from ..types import flow_get_metrics_params, flow_trigger_with_file_params, flow_trigger_with_payload_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.flow_get_metrics_response import FlowGetMetricsResponse
from ..types.flow_trigger_with_file_response import FlowTriggerWithFileResponse
from ..types.flow_trigger_with_payload_response import FlowTriggerWithPayloadResponse

__all__ = ["FlowsResource", "AsyncFlowsResource"]


class FlowsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FlowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return FlowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FlowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return FlowsResourceWithStreamingResponse(self)

    def get_metrics(
        self,
        *,
        end_date: Union[str, date] | NotGiven = NOT_GIVEN,
        start_date: Union[str, date] | NotGiven = NOT_GIVEN,
        status: Literal["completed", "failed", "in_progress"] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowGetMetricsResponse:
        """Get metrics for workflows within a specified date range.

        This endpoint provides
        aggregated statistics about workflow execution and detailed information about
        individual workflows.

        The response includes metrics aggregated by user and a list of all workflows
        matching the specified criteria.

        Args:
          end_date: End date for filtering (YYYY-MM-DD format)

          start_date: Start date for filtering (YYYY-MM-DD format)

          status: Filter by workflow status

          user_id: Filter by specific user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/flows/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "start_date": start_date,
                        "status": status,
                        "user_id": user_id,
                    },
                    flow_get_metrics_params.FlowGetMetricsParams,
                ),
            ),
            cast_to=FlowGetMetricsResponse,
        )

    def trigger_with_file(
        self,
        flow_id: str,
        *,
        file: FileTypes | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowTriggerWithFileResponse:
        """Trigger a workflow by its ID with either a file upload or a URL to a file.

        This
        endpoint accepts multipart/form-data with either a file field or a URL field.
        When a URL is provided, the server will download the file and process it as if
        it were directly uploaded. The workflow ID must be specified in the URL path.

        Args:
          file: File to upload and process

          url: URL to a file to download and process

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not flow_id:
            raise ValueError(f"Expected a non-empty value for `flow_id` but received {flow_id!r}")
        body = deepcopy_minimal(
            {
                "file": file,
                "url": url,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            f"/flows/file/{flow_id}",
            body=maybe_transform(body, flow_trigger_with_file_params.FlowTriggerWithFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlowTriggerWithFileResponse,
        )

    def trigger_with_payload(
        self,
        flow_id: str,
        *,
        body: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowTriggerWithPayloadResponse:
        """Trigger a workflow by its ID with a JSON payload.

        This endpoint accepts any
        valid JSON object as the request body and forwards it to the workflow. The
        workflow ID must be specified in the URL path.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not flow_id:
            raise ValueError(f"Expected a non-empty value for `flow_id` but received {flow_id!r}")
        return self._post(
            f"/flows/trigger/{flow_id}",
            body=maybe_transform(body, flow_trigger_with_payload_params.FlowTriggerWithPayloadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlowTriggerWithPayloadResponse,
        )


class AsyncFlowsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFlowsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncFlowsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFlowsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return AsyncFlowsResourceWithStreamingResponse(self)

    async def get_metrics(
        self,
        *,
        end_date: Union[str, date] | NotGiven = NOT_GIVEN,
        start_date: Union[str, date] | NotGiven = NOT_GIVEN,
        status: Literal["completed", "failed", "in_progress"] | NotGiven = NOT_GIVEN,
        user_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowGetMetricsResponse:
        """Get metrics for workflows within a specified date range.

        This endpoint provides
        aggregated statistics about workflow execution and detailed information about
        individual workflows.

        The response includes metrics aggregated by user and a list of all workflows
        matching the specified criteria.

        Args:
          end_date: End date for filtering (YYYY-MM-DD format)

          start_date: Start date for filtering (YYYY-MM-DD format)

          status: Filter by workflow status

          user_id: Filter by specific user ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/flows/metrics",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "start_date": start_date,
                        "status": status,
                        "user_id": user_id,
                    },
                    flow_get_metrics_params.FlowGetMetricsParams,
                ),
            ),
            cast_to=FlowGetMetricsResponse,
        )

    async def trigger_with_file(
        self,
        flow_id: str,
        *,
        file: FileTypes | NotGiven = NOT_GIVEN,
        url: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowTriggerWithFileResponse:
        """Trigger a workflow by its ID with either a file upload or a URL to a file.

        This
        endpoint accepts multipart/form-data with either a file field or a URL field.
        When a URL is provided, the server will download the file and process it as if
        it were directly uploaded. The workflow ID must be specified in the URL path.

        Args:
          file: File to upload and process

          url: URL to a file to download and process

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not flow_id:
            raise ValueError(f"Expected a non-empty value for `flow_id` but received {flow_id!r}")
        body = deepcopy_minimal(
            {
                "file": file,
                "url": url,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            f"/flows/file/{flow_id}",
            body=await async_maybe_transform(body, flow_trigger_with_file_params.FlowTriggerWithFileParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlowTriggerWithFileResponse,
        )

    async def trigger_with_payload(
        self,
        flow_id: str,
        *,
        body: Dict[str, object],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FlowTriggerWithPayloadResponse:
        """Trigger a workflow by its ID with a JSON payload.

        This endpoint accepts any
        valid JSON object as the request body and forwards it to the workflow. The
        workflow ID must be specified in the URL path.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not flow_id:
            raise ValueError(f"Expected a non-empty value for `flow_id` but received {flow_id!r}")
        return await self._post(
            f"/flows/trigger/{flow_id}",
            body=await async_maybe_transform(body, flow_trigger_with_payload_params.FlowTriggerWithPayloadParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FlowTriggerWithPayloadResponse,
        )


class FlowsResourceWithRawResponse:
    def __init__(self, flows: FlowsResource) -> None:
        self._flows = flows

        self.get_metrics = to_raw_response_wrapper(
            flows.get_metrics,
        )
        self.trigger_with_file = to_raw_response_wrapper(
            flows.trigger_with_file,
        )
        self.trigger_with_payload = to_raw_response_wrapper(
            flows.trigger_with_payload,
        )


class AsyncFlowsResourceWithRawResponse:
    def __init__(self, flows: AsyncFlowsResource) -> None:
        self._flows = flows

        self.get_metrics = async_to_raw_response_wrapper(
            flows.get_metrics,
        )
        self.trigger_with_file = async_to_raw_response_wrapper(
            flows.trigger_with_file,
        )
        self.trigger_with_payload = async_to_raw_response_wrapper(
            flows.trigger_with_payload,
        )


class FlowsResourceWithStreamingResponse:
    def __init__(self, flows: FlowsResource) -> None:
        self._flows = flows

        self.get_metrics = to_streamed_response_wrapper(
            flows.get_metrics,
        )
        self.trigger_with_file = to_streamed_response_wrapper(
            flows.trigger_with_file,
        )
        self.trigger_with_payload = to_streamed_response_wrapper(
            flows.trigger_with_payload,
        )


class AsyncFlowsResourceWithStreamingResponse:
    def __init__(self, flows: AsyncFlowsResource) -> None:
        self._flows = flows

        self.get_metrics = async_to_streamed_response_wrapper(
            flows.get_metrics,
        )
        self.trigger_with_file = async_to_streamed_response_wrapper(
            flows.trigger_with_file,
        )
        self.trigger_with_payload = async_to_streamed_response_wrapper(
            flows.trigger_with_payload,
        )
