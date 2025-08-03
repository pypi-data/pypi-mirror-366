# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from chunkr_ai import Chunkr, AsyncChunkr
from tests.utils import assert_matches_type
from chunkr_ai.types import (
    Task,
)
from chunkr_ai._utils import parse_datetime
from chunkr_ai.pagination import SyncTasksPage, AsyncTasksPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTask:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update(self, client: Chunkr) -> None:
        task = client.task.update(
            task_id="task_id",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_update_with_all_params(self, client: Chunkr) -> None:
        task = client.task.update(
            task_id="task_id",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            high_resolution=True,
            llm_processing={
                "fallback_strategy": "None",
                "max_completion_tokens": 0,
                "model_id": "model_id",
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_update(self, client: Chunkr) -> None:
        response = client.task.with_raw_response.update(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_update(self, client: Chunkr) -> None:
        with client.task.with_streaming_response.update(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_update(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.task.with_raw_response.update(
                task_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_list(self, client: Chunkr) -> None:
        task = client.task.list()
        assert_matches_type(SyncTasksPage[Task], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_list_with_all_params(self, client: Chunkr) -> None:
        task = client.task.list(
            base64_urls=True,
            cursor=parse_datetime("2019-12-27T18:11:19.117Z"),
            end=parse_datetime("2019-12-27T18:11:19.117Z"),
            include_chunks=True,
            limit=0,
            sort="asc",
            start=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(SyncTasksPage[Task], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_list(self, client: Chunkr) -> None:
        response = client.task.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(SyncTasksPage[Task], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_list(self, client: Chunkr) -> None:
        with client.task.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(SyncTasksPage[Task], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_method_delete(self, client: Chunkr) -> None:
        task = client.task.delete(
            "task_id",
        )
        assert task is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_delete(self, client: Chunkr) -> None:
        response = client.task.with_raw_response.delete(
            "task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert task is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_delete(self, client: Chunkr) -> None:
        with client.task.with_streaming_response.delete(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_delete(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.task.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_cancel(self, client: Chunkr) -> None:
        task = client.task.cancel(
            "task_id",
        )
        assert task is None

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_cancel(self, client: Chunkr) -> None:
        response = client.task.with_raw_response.cancel(
            "task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert task is None

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_cancel(self, client: Chunkr) -> None:
        with client.task.with_streaming_response.cancel(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_cancel(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.task.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_get(self, client: Chunkr) -> None:
        task = client.task.get(
            task_id="task_id",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_get_with_all_params(self, client: Chunkr) -> None:
        task = client.task.get(
            task_id="task_id",
            base64_urls=True,
            include_chunks=True,
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_get(self, client: Chunkr) -> None:
        response = client.task.with_raw_response.get(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_get(self, client: Chunkr) -> None:
        with client.task.with_streaming_response.get(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_get(self, client: Chunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            client.task.with_raw_response.get(
                task_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_parse(self, client: Chunkr) -> None:
        task = client.task.parse(
            file="file",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_parse_with_all_params(self, client: Chunkr) -> None:
        task = client.task.parse(
            file="file",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            file_name="file_name",
            llm_processing={
                "fallback_strategy": "None",
                "max_completion_tokens": 0,
                "model_id": "model_id",
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_parse(self, client: Chunkr) -> None:
        response = client.task.with_raw_response.parse(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_parse(self, client: Chunkr) -> None:
        with client.task.with_streaming_response.parse(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncTask:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_update(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.update(
            task_id="task_id",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.update(
            task_id="task_id",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            high_resolution=True,
            llm_processing={
                "fallback_strategy": "None",
                "max_completion_tokens": 0,
                "model_id": "model_id",
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncChunkr) -> None:
        response = await async_client.task.with_raw_response.update(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncChunkr) -> None:
        async with async_client.task.with_streaming_response.update(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_update(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.task.with_raw_response.update(
                task_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_list(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.list()
        assert_matches_type(AsyncTasksPage[Task], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.list(
            base64_urls=True,
            cursor=parse_datetime("2019-12-27T18:11:19.117Z"),
            end=parse_datetime("2019-12-27T18:11:19.117Z"),
            include_chunks=True,
            limit=0,
            sort="asc",
            start=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AsyncTasksPage[Task], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncChunkr) -> None:
        response = await async_client.task.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(AsyncTasksPage[Task], task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncChunkr) -> None:
        async with async_client.task.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(AsyncTasksPage[Task], task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_method_delete(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.delete(
            "task_id",
        )
        assert task is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncChunkr) -> None:
        response = await async_client.task.with_raw_response.delete(
            "task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert task is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncChunkr) -> None:
        async with async_client.task.with_streaming_response.delete(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.task.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_cancel(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.cancel(
            "task_id",
        )
        assert task is None

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncChunkr) -> None:
        response = await async_client.task.with_raw_response.cancel(
            "task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert task is None

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncChunkr) -> None:
        async with async_client.task.with_streaming_response.cancel(
            "task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert task is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.task.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_get(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.get(
            task_id="task_id",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_get_with_all_params(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.get(
            task_id="task_id",
            base64_urls=True,
            include_chunks=True,
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_get(self, async_client: AsyncChunkr) -> None:
        response = await async_client.task.with_raw_response.get(
            task_id="task_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncChunkr) -> None:
        async with async_client.task.with_streaming_response.get(
            task_id="task_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_get(self, async_client: AsyncChunkr) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `task_id` but received ''"):
            await async_client.task.with_raw_response.get(
                task_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_parse(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.parse(
            file="file",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_parse_with_all_params(self, async_client: AsyncChunkr) -> None:
        task = await async_client.task.parse(
            file="file",
            chunk_processing={
                "ignore_headers_and_footers": True,
                "target_length": 0,
                "tokenizer": {"enum": "Word"},
            },
            error_handling="Fail",
            expires_in=0,
            file_name="file_name",
            llm_processing={
                "fallback_strategy": "None",
                "max_completion_tokens": 0,
                "model_id": "model_id",
                "temperature": 0,
            },
            ocr_strategy="All",
            pipeline="Azure",
            segment_processing={
                "caption": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "footnote": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "formula": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "list_item": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_footer": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "page_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "picture": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "section_header": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "table": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "text": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
                "title": {
                    "crop_image": "All",
                    "description": True,
                    "embed_sources": ["Content"],
                    "extended_context": True,
                    "format": "Html",
                    "html": "LLM",
                    "llm": "llm",
                    "markdown": "LLM",
                    "strategy": "LLM",
                },
            },
            segmentation_strategy="LayoutAnalysis",
        )
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_parse(self, async_client: AsyncChunkr) -> None:
        response = await async_client.task.with_raw_response.parse(
            file="file",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        task = await response.parse()
        assert_matches_type(Task, task, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_parse(self, async_client: AsyncChunkr) -> None:
        async with async_client.task.with_streaming_response.parse(
            file="file",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            task = await response.parse()
            assert_matches_type(Task, task, path=["response"])

        assert cast(Any, response.is_closed) is True
