# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    db_execute_query_params,
    db_insert_record_params,
    db_delete_records_params,
    db_update_records_params,
    db_process_nl_query_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.db_execute_query_response import DBExecuteQueryResponse
from ..types.db_insert_record_response import DBInsertRecordResponse
from ..types.db_delete_records_response import DBDeleteRecordsResponse
from ..types.db_update_records_response import DBUpdateRecordsResponse
from ..types.db_process_nl_query_response import DBProcessNlQueryResponse

__all__ = ["DBResource", "AsyncDBResource"]


class DBResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DBResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return DBResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DBResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return DBResourceWithStreamingResponse(self)

    def delete_records(
        self,
        *,
        table: str,
        where: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBDeleteRecordsResponse:
        """
        Deletes records from the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          table: Table name to delete from

          where: Where conditions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._delete(
            "/db/delete",
            body=maybe_transform(
                {
                    "table": table,
                    "where": where,
                },
                db_delete_records_params.DBDeleteRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBDeleteRecordsResponse,
        )

    def execute_query(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBExecuteQueryResponse:
        """Executes a raw SQL query directly against ClickHouse (WorqDB).

        This endpoint
        provides direct SQL access with security guardrails to prevent destructive
        operations.

        Args:
          query: SQL query to execute

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/query",
            body=maybe_transform({"query": query}, db_execute_query_params.DBExecuteQueryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBExecuteQueryResponse,
        )

    def insert_record(
        self,
        *,
        data: object,
        table: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBInsertRecordResponse:
        """Inserts a new record into the specified table.

        Organization ID is automatically
        added for multi-tenant security.

        Args:
          data: Data to insert

          table: Table name to insert into

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/insert",
            body=maybe_transform(
                {
                    "data": data,
                    "table": table,
                },
                db_insert_record_params.DBInsertRecordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBInsertRecordResponse,
        )

    def process_nl_query(
        self,
        *,
        question: str,
        table: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBProcessNlQueryResponse:
        """
        Converts a natural language question into a SQL query and executes it.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          question: Natural language question

          table: Table name to query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/db/nl-query",
            body=maybe_transform(
                {
                    "question": question,
                    "table": table,
                },
                db_process_nl_query_params.DBProcessNlQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBProcessNlQueryResponse,
        )

    def update_records(
        self,
        *,
        data: object,
        table: str,
        where: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBUpdateRecordsResponse:
        """
        Updates records in the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          data: Data to update

          table: Table name to update

          where: Where conditions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            "/db/update",
            body=maybe_transform(
                {
                    "data": data,
                    "table": table,
                    "where": where,
                },
                db_update_records_params.DBUpdateRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBUpdateRecordsResponse,
        )


class AsyncDBResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDBResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDBResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDBResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/WorqHat/worqhat-python-sdk#with_streaming_response
        """
        return AsyncDBResourceWithStreamingResponse(self)

    async def delete_records(
        self,
        *,
        table: str,
        where: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBDeleteRecordsResponse:
        """
        Deletes records from the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          table: Table name to delete from

          where: Where conditions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._delete(
            "/db/delete",
            body=await async_maybe_transform(
                {
                    "table": table,
                    "where": where,
                },
                db_delete_records_params.DBDeleteRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBDeleteRecordsResponse,
        )

    async def execute_query(
        self,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBExecuteQueryResponse:
        """Executes a raw SQL query directly against ClickHouse (WorqDB).

        This endpoint
        provides direct SQL access with security guardrails to prevent destructive
        operations.

        Args:
          query: SQL query to execute

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/query",
            body=await async_maybe_transform({"query": query}, db_execute_query_params.DBExecuteQueryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBExecuteQueryResponse,
        )

    async def insert_record(
        self,
        *,
        data: object,
        table: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBInsertRecordResponse:
        """Inserts a new record into the specified table.

        Organization ID is automatically
        added for multi-tenant security.

        Args:
          data: Data to insert

          table: Table name to insert into

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/insert",
            body=await async_maybe_transform(
                {
                    "data": data,
                    "table": table,
                },
                db_insert_record_params.DBInsertRecordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBInsertRecordResponse,
        )

    async def process_nl_query(
        self,
        *,
        question: str,
        table: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBProcessNlQueryResponse:
        """
        Converts a natural language question into a SQL query and executes it.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          question: Natural language question

          table: Table name to query

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/db/nl-query",
            body=await async_maybe_transform(
                {
                    "question": question,
                    "table": table,
                },
                db_process_nl_query_params.DBProcessNlQueryParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBProcessNlQueryResponse,
        )

    async def update_records(
        self,
        *,
        data: object,
        table: str,
        where: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DBUpdateRecordsResponse:
        """
        Updates records in the specified table that match the where conditions.
        Organization ID filtering is automatically applied for multi-tenant security.

        Args:
          data: Data to update

          table: Table name to update

          where: Where conditions

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            "/db/update",
            body=await async_maybe_transform(
                {
                    "data": data,
                    "table": table,
                    "where": where,
                },
                db_update_records_params.DBUpdateRecordsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DBUpdateRecordsResponse,
        )


class DBResourceWithRawResponse:
    def __init__(self, db: DBResource) -> None:
        self._db = db

        self.delete_records = to_raw_response_wrapper(
            db.delete_records,
        )
        self.execute_query = to_raw_response_wrapper(
            db.execute_query,
        )
        self.insert_record = to_raw_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = to_raw_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = to_raw_response_wrapper(
            db.update_records,
        )


class AsyncDBResourceWithRawResponse:
    def __init__(self, db: AsyncDBResource) -> None:
        self._db = db

        self.delete_records = async_to_raw_response_wrapper(
            db.delete_records,
        )
        self.execute_query = async_to_raw_response_wrapper(
            db.execute_query,
        )
        self.insert_record = async_to_raw_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = async_to_raw_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = async_to_raw_response_wrapper(
            db.update_records,
        )


class DBResourceWithStreamingResponse:
    def __init__(self, db: DBResource) -> None:
        self._db = db

        self.delete_records = to_streamed_response_wrapper(
            db.delete_records,
        )
        self.execute_query = to_streamed_response_wrapper(
            db.execute_query,
        )
        self.insert_record = to_streamed_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = to_streamed_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = to_streamed_response_wrapper(
            db.update_records,
        )


class AsyncDBResourceWithStreamingResponse:
    def __init__(self, db: AsyncDBResource) -> None:
        self._db = db

        self.delete_records = async_to_streamed_response_wrapper(
            db.delete_records,
        )
        self.execute_query = async_to_streamed_response_wrapper(
            db.execute_query,
        )
        self.insert_record = async_to_streamed_response_wrapper(
            db.insert_record,
        )
        self.process_nl_query = async_to_streamed_response_wrapper(
            db.process_nl_query,
        )
        self.update_records = async_to_streamed_response_wrapper(
            db.update_records,
        )
