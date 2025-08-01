# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from worqhat import Worqhat, AsyncWorqhat
from tests.utils import assert_matches_type
from worqhat.types import (
    FlowGetMetricsResponse,
    FlowTriggerWithFileResponse,
    FlowTriggerWithPayloadResponse,
)
from worqhat._utils import parse_date

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFlows:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_metrics(self, client: Worqhat) -> None:
        flow = client.flows.get_metrics()
        assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_metrics_with_all_params(self, client: Worqhat) -> None:
        flow = client.flows.get_metrics(
            end_date=parse_date("2025-07-24"),
            start_date=parse_date("2025-07-01"),
            status="completed",
            user_id="member-test-2f9b9a4f-5898-4e7a-8f26-e60cea49ae31",
        )
        assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get_metrics(self, client: Worqhat) -> None:
        response = client.flows.with_raw_response.get_metrics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = response.parse()
        assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get_metrics(self, client: Worqhat) -> None:
        with client.flows.with_streaming_response.get_metrics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = response.parse()
            assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_trigger_with_file(self, client: Worqhat) -> None:
        flow = client.flows.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
        )
        assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_trigger_with_file_with_all_params(self, client: Worqhat) -> None:
        flow = client.flows.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            file=b"raw file contents",
            url="https://example.com/path/to/file.pdf",
        )
        assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_trigger_with_file(self, client: Worqhat) -> None:
        response = client.flows.with_raw_response.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = response.parse()
        assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_trigger_with_file(self, client: Worqhat) -> None:
        with client.flows.with_streaming_response.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = response.parse()
            assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_trigger_with_file(self, client: Worqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `flow_id` but received ''"):
            client.flows.with_raw_response.trigger_with_file(
                flow_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_trigger_with_payload(self, client: Worqhat) -> None:
        flow = client.flows.trigger_with_payload(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            body={
                "key1": "bar",
                "key2": "bar",
            },
        )
        assert_matches_type(FlowTriggerWithPayloadResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_trigger_with_payload(self, client: Worqhat) -> None:
        response = client.flows.with_raw_response.trigger_with_payload(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            body={
                "key1": "bar",
                "key2": "bar",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = response.parse()
        assert_matches_type(FlowTriggerWithPayloadResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_trigger_with_payload(self, client: Worqhat) -> None:
        with client.flows.with_streaming_response.trigger_with_payload(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            body={
                "key1": "bar",
                "key2": "bar",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = response.parse()
            assert_matches_type(FlowTriggerWithPayloadResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_trigger_with_payload(self, client: Worqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `flow_id` but received ''"):
            client.flows.with_raw_response.trigger_with_payload(
                flow_id="",
                body={
                    "key1": "bar",
                    "key2": "bar",
                },
            )


class TestAsyncFlows:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_metrics(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.get_metrics()
        assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_metrics_with_all_params(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.get_metrics(
            end_date=parse_date("2025-07-24"),
            start_date=parse_date("2025-07-01"),
            status="completed",
            user_id="member-test-2f9b9a4f-5898-4e7a-8f26-e60cea49ae31",
        )
        assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get_metrics(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.flows.with_raw_response.get_metrics()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = await response.parse()
        assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get_metrics(self, async_client: AsyncWorqhat) -> None:
        async with async_client.flows.with_streaming_response.get_metrics() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = await response.parse()
            assert_matches_type(FlowGetMetricsResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_trigger_with_file(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
        )
        assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_trigger_with_file_with_all_params(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            file=b"raw file contents",
            url="https://example.com/path/to/file.pdf",
        )
        assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_trigger_with_file(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.flows.with_raw_response.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = await response.parse()
        assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_trigger_with_file(self, async_client: AsyncWorqhat) -> None:
        async with async_client.flows.with_streaming_response.trigger_with_file(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = await response.parse()
            assert_matches_type(FlowTriggerWithFileResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_trigger_with_file(self, async_client: AsyncWorqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `flow_id` but received ''"):
            await async_client.flows.with_raw_response.trigger_with_file(
                flow_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_trigger_with_payload(self, async_client: AsyncWorqhat) -> None:
        flow = await async_client.flows.trigger_with_payload(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            body={
                "key1": "bar",
                "key2": "bar",
            },
        )
        assert_matches_type(FlowTriggerWithPayloadResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_trigger_with_payload(self, async_client: AsyncWorqhat) -> None:
        response = await async_client.flows.with_raw_response.trigger_with_payload(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            body={
                "key1": "bar",
                "key2": "bar",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        flow = await response.parse()
        assert_matches_type(FlowTriggerWithPayloadResponse, flow, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_trigger_with_payload(self, async_client: AsyncWorqhat) -> None:
        async with async_client.flows.with_streaming_response.trigger_with_payload(
            flow_id="f825ab82-371f-40cb-9bed-b325531ead4a",
            body={
                "key1": "bar",
                "key2": "bar",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            flow = await response.parse()
            assert_matches_type(FlowTriggerWithPayloadResponse, flow, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_trigger_with_payload(self, async_client: AsyncWorqhat) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `flow_id` but received ''"):
            await async_client.flows.with_raw_response.trigger_with_payload(
                flow_id="",
                body={
                    "key1": "bar",
                    "key2": "bar",
                },
            )
