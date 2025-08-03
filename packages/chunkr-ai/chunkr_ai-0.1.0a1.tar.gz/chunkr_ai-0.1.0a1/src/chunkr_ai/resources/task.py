# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import (
    task_get_params,
    task_list_params,
    task_parse_params,
    task_update_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..pagination import SyncTasksPage, AsyncTasksPage
from ..types.task import Task
from .._base_client import AsyncPaginator, make_request_options
from ..types.llm_processing_param import LlmProcessingParam
from ..types.chunk_processing_param import ChunkProcessingParam
from ..types.segment_processing_param import SegmentProcessingParam

__all__ = ["TaskResource", "AsyncTaskResource"]


class TaskResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return TaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return TaskResourceWithStreamingResponse(self)

    def update(
        self,
        task_id: str,
        *,
        chunk_processing: Optional[ChunkProcessingParam] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        high_resolution: Optional[bool] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[LlmProcessingParam] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[SegmentProcessingParam] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """Updates an existing task's configuration and reprocesses the document.

        The
        original configuration will be used for all values that are not provided in the
        update.

        Requirements:

        - Task must have status `Succeeded` or `Failed`
        - New configuration must be different from the current one

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /task/{task_id}` endpoint to poll for completion.

        Args:
          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          high_resolution: Whether to use high-resolution images for cropping and post-processing. (Latency
              penalty: ~7 seconds per page)

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and **LLM
              descriptions** further refine behaviour.

              ---

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown) • `Table` → **LLM** (HTML,
              description on) • `Picture` → **LLM** (Markdown, description on, cropping _All_)
              • `Formula`, `Page` → **LLM** (Markdown) • `PageHeader`, `PageFooter` →
              **Ignore** (removed from output)

              ---

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._patch(
            f"/task/{task_id}/parse",
            body=maybe_transform(
                {
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "high_resolution": high_resolution,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                task_update_params.TaskUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def list(
        self,
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        cursor: Union[str, datetime] | NotGiven = NOT_GIVEN,
        end: Union[str, datetime] | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        start: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncTasksPage[Task]:
        """Retrieves a list of tasks with cursor-based pagination.

        By default, tasks are
        returned in descending order (newest first).

        ## Default Behaviors:

        - **limit**: Returns all tasks if not specified
        - **start**: No start date filter (returns from beginning of time)
        - **end**: No end date filter (returns up to current time)
        - **cursor**: Starts from most recent tasks (no pagination offset)
        - **sort**: 'desc' (descending order, newest first)
        - **include_chunks**: false (excludes chunks for better performance)
        - **base64_urls**: false (returns presigned URLs instead of base64)

        ## Common Usage Patterns:

        **Basic usage (get all tasks):** `GET /api/v1/tasks`

        **Get first 10 tasks:** `GET /api/v1/tasks?limit=10`

        **Paginate through results:**

        1. First request: `GET /api/v1/tasks?limit=10`
        2. Use next_cursor from response for subsequent pages:
           `GET /api/v1/tasks?limit=10&cursor=<timestamp>`

        **Filter by date range:**
        `GET /api/v1/tasks?start=2025-01-01T00:00:00Z&end=2025-12-31T23:59:59Z`

        **Get detailed results with chunks:** `GET /api/v1/tasks?include_chunks=true`

        **Get base64 encoded content:** `GET /api/v1/tasks?base64_urls=true`

        **Get tasks in ascending order (oldest first):** `GET /api/v1/tasks?sort=asc`

        **Get tasks in descending order (newest first, default):**
        `GET /api/v1/tasks?sort=desc`

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          cursor: Cursor for pagination (timestamp)

          end: End date

          include_chunks: Whether to include chunks in the output response

          limit: Number of tasks per page

          sort: Sort order: 'asc' for ascending, 'desc' for descending (default)

          start: Start date

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/tasks",
            page=SyncTasksPage[Task],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "cursor": cursor,
                        "end": end,
                        "include_chunks": include_chunks,
                        "limit": limit,
                        "sort": sort,
                        "start": start,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            model=Task,
        )

    def delete(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a task by its ID.

        Requirements:

        - Task must have status `Succeeded` or `Failed`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def cancel(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Cancel a task that hasn't started processing yet:

        - For new tasks: Status will be updated to `Cancelled`
        - For updating tasks: Task will revert to the previous state

        Requirements:

        - Task must have status `Starting`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/task/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get(
        self,
        task_id: Optional[str],
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Retrieves detailed information about a task by its ID, including:

        - Processing status
        - Task configuration
        - Output data (if processing is complete)
        - File metadata (name, page count)
        - Timestamps (created, started, finished)
        - Presigned URLs for accessing files

        This endpoint can be used to:

        1. Poll the task status during processing
        2. Retrieve the final output once processing is complete
        3. Access task metadata and configuration

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          include_chunks: Whether to include chunks in the output response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "include_chunks": include_chunks,
                    },
                    task_get_params.TaskGetParams,
                ),
            ),
            cast_to=Task,
        )

    def parse(
        self,
        *,
        file: str,
        chunk_processing: Optional[ChunkProcessingParam] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[LlmProcessingParam] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[SegmentProcessingParam] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Queues a document for processing and returns a TaskResponse containing:

        - Task ID for status polling
        - Initial configuration
        - File metadata
        - Processing status
        - Creation timestamp
        - Presigned URLs for file access

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /task/{task_id}` endpoint to poll for completion.

        Args:
          file: The file to be uploaded. Can be a URL or a base64 encoded file.

          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be uploaded. If not set a name will be generated.

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and **LLM
              descriptions** further refine behaviour.

              ---

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown) • `Table` → **LLM** (HTML,
              description on) • `Picture` → **LLM** (Markdown, description on, cropping _All_)
              • `Formula`, `Page` → **LLM** (Markdown) • `PageHeader`, `PageFooter` →
              **Ignore** (removed from output)

              ---

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/task/parse",
            body=maybe_transform(
                {
                    "file": file,
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                task_parse_params.TaskParseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )


class AsyncTaskResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTaskResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTaskResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTaskResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return AsyncTaskResourceWithStreamingResponse(self)

    async def update(
        self,
        task_id: str,
        *,
        chunk_processing: Optional[ChunkProcessingParam] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        high_resolution: Optional[bool] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[LlmProcessingParam] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[SegmentProcessingParam] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """Updates an existing task's configuration and reprocesses the document.

        The
        original configuration will be used for all values that are not provided in the
        update.

        Requirements:

        - Task must have status `Succeeded` or `Failed`
        - New configuration must be different from the current one

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /task/{task_id}` endpoint to poll for completion.

        Args:
          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          high_resolution: Whether to use high-resolution images for cropping and post-processing. (Latency
              penalty: ~7 seconds per page)

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and **LLM
              descriptions** further refine behaviour.

              ---

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown) • `Table` → **LLM** (HTML,
              description on) • `Picture` → **LLM** (Markdown, description on, cropping _All_)
              • `Formula`, `Page` → **LLM** (Markdown) • `PageHeader`, `PageFooter` →
              **Ignore** (removed from output)

              ---

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._patch(
            f"/task/{task_id}/parse",
            body=await async_maybe_transform(
                {
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "high_resolution": high_resolution,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                task_update_params.TaskUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )

    def list(
        self,
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        cursor: Union[str, datetime] | NotGiven = NOT_GIVEN,
        end: Union[str, datetime] | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        start: Union[str, datetime] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[Task, AsyncTasksPage[Task]]:
        """Retrieves a list of tasks with cursor-based pagination.

        By default, tasks are
        returned in descending order (newest first).

        ## Default Behaviors:

        - **limit**: Returns all tasks if not specified
        - **start**: No start date filter (returns from beginning of time)
        - **end**: No end date filter (returns up to current time)
        - **cursor**: Starts from most recent tasks (no pagination offset)
        - **sort**: 'desc' (descending order, newest first)
        - **include_chunks**: false (excludes chunks for better performance)
        - **base64_urls**: false (returns presigned URLs instead of base64)

        ## Common Usage Patterns:

        **Basic usage (get all tasks):** `GET /api/v1/tasks`

        **Get first 10 tasks:** `GET /api/v1/tasks?limit=10`

        **Paginate through results:**

        1. First request: `GET /api/v1/tasks?limit=10`
        2. Use next_cursor from response for subsequent pages:
           `GET /api/v1/tasks?limit=10&cursor=<timestamp>`

        **Filter by date range:**
        `GET /api/v1/tasks?start=2025-01-01T00:00:00Z&end=2025-12-31T23:59:59Z`

        **Get detailed results with chunks:** `GET /api/v1/tasks?include_chunks=true`

        **Get base64 encoded content:** `GET /api/v1/tasks?base64_urls=true`

        **Get tasks in ascending order (oldest first):** `GET /api/v1/tasks?sort=asc`

        **Get tasks in descending order (newest first, default):**
        `GET /api/v1/tasks?sort=desc`

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          cursor: Cursor for pagination (timestamp)

          end: End date

          include_chunks: Whether to include chunks in the output response

          limit: Number of tasks per page

          sort: Sort order: 'asc' for ascending, 'desc' for descending (default)

          start: Start date

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/tasks",
            page=AsyncTasksPage[Task],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "cursor": cursor,
                        "end": end,
                        "include_chunks": include_chunks,
                        "limit": limit,
                        "sort": sort,
                        "start": start,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            model=Task,
        )

    async def delete(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete a task by its ID.

        Requirements:

        - Task must have status `Succeeded` or `Failed`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def cancel(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Cancel a task that hasn't started processing yet:

        - For new tasks: Status will be updated to `Cancelled`
        - For updating tasks: Task will revert to the previous state

        Requirements:

        - Task must have status `Starting`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/task/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get(
        self,
        task_id: Optional[str],
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Retrieves detailed information about a task by its ID, including:

        - Processing status
        - Task configuration
        - Output data (if processing is complete)
        - File metadata (name, page count)
        - Timestamps (created, started, finished)
        - Presigned URLs for accessing files

        This endpoint can be used to:

        1. Poll the task status during processing
        2. Retrieve the final output once processing is complete
        3. Access task metadata and configuration

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          include_chunks: Whether to include chunks in the output response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/task/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "include_chunks": include_chunks,
                    },
                    task_get_params.TaskGetParams,
                ),
            ),
            cast_to=Task,
        )

    async def parse(
        self,
        *,
        file: str,
        chunk_processing: Optional[ChunkProcessingParam] | NotGiven = NOT_GIVEN,
        error_handling: Optional[Literal["Fail", "Continue"]] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        llm_processing: Optional[LlmProcessingParam] | NotGiven = NOT_GIVEN,
        ocr_strategy: Optional[Literal["All", "Auto"]] | NotGiven = NOT_GIVEN,
        pipeline: Optional[Literal["Azure", "Chunkr"]] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[SegmentProcessingParam] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Task:
        """
        Queues a document for processing and returns a TaskResponse containing:

        - Task ID for status polling
        - Initial configuration
        - File metadata
        - Processing status
        - Creation timestamp
        - Presigned URLs for file access

        The returned task will typically be in a `Starting` or `Processing` state. Use
        the `GET /task/{task_id}` endpoint to poll for completion.

        Args:
          file: The file to be uploaded. Can be a URL or a base64 encoded file.

          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be uploaded. If not set a name will be generated.

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          pipeline: Choose the provider whose models will be used for segmentation and OCR. The
              output will be unified to the Chunkr `output` format.

          segment_processing: Defines how each segment type is handled when generating the final output.

              Each segment uses one of three strategies. The chosen strategy controls: •
              Whether the segment is kept (`Auto`, `LLM`) or skipped (`Ignore`). • How the
              content is produced (rule-based vs. LLM). • The output format (`Html` or
              `Markdown`).

              Optional flags such as image **cropping**, **extended context**, and **LLM
              descriptions** further refine behaviour.

              ---

              **Default strategy per segment** • `Title`, `SectionHeader`, `Text`, `ListItem`,
              `Caption`, `Footnote` → **Auto** (Markdown) • `Table` → **LLM** (HTML,
              description on) • `Picture` → **LLM** (Markdown, description on, cropping _All_)
              • `Formula`, `Page` → **LLM** (Markdown) • `PageHeader`, `PageFooter` →
              **Ignore** (removed from output)

              ---

              **Strategy reference** • **Auto** – rule-based content generation. • **LLM** –
              generate content with an LLM. • **Ignore** – exclude the segment entirely.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/task/parse",
            body=await async_maybe_transform(
                {
                    "file": file,
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                task_parse_params.TaskParseParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Task,
        )


class TaskResourceWithRawResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.update = to_raw_response_wrapper(
            task.update,
        )
        self.list = to_raw_response_wrapper(
            task.list,
        )
        self.delete = to_raw_response_wrapper(
            task.delete,
        )
        self.cancel = to_raw_response_wrapper(
            task.cancel,
        )
        self.get = to_raw_response_wrapper(
            task.get,
        )
        self.parse = to_raw_response_wrapper(
            task.parse,
        )


class AsyncTaskResourceWithRawResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.update = async_to_raw_response_wrapper(
            task.update,
        )
        self.list = async_to_raw_response_wrapper(
            task.list,
        )
        self.delete = async_to_raw_response_wrapper(
            task.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            task.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            task.get,
        )
        self.parse = async_to_raw_response_wrapper(
            task.parse,
        )


class TaskResourceWithStreamingResponse:
    def __init__(self, task: TaskResource) -> None:
        self._task = task

        self.update = to_streamed_response_wrapper(
            task.update,
        )
        self.list = to_streamed_response_wrapper(
            task.list,
        )
        self.delete = to_streamed_response_wrapper(
            task.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            task.cancel,
        )
        self.get = to_streamed_response_wrapper(
            task.get,
        )
        self.parse = to_streamed_response_wrapper(
            task.parse,
        )


class AsyncTaskResourceWithStreamingResponse:
    def __init__(self, task: AsyncTaskResource) -> None:
        self._task = task

        self.update = async_to_streamed_response_wrapper(
            task.update,
        )
        self.list = async_to_streamed_response_wrapper(
            task.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            task.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            task.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            task.get,
        )
        self.parse = async_to_streamed_response_wrapper(
            task.parse,
        )
