# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal, TypedDict

from .llm_processing_param import LlmProcessingParam
from .chunk_processing_param import ChunkProcessingParam
from .segment_processing_param import SegmentProcessingParam

__all__ = ["TaskUpdateParams"]


class TaskUpdateParams(TypedDict, total=False):
    chunk_processing: Optional[ChunkProcessingParam]
    """Controls the setting for the chunking and post-processing of each chunk."""

    error_handling: Optional[Literal["Fail", "Continue"]]
    """Controls how errors are handled during processing:

    - `Fail`: Stops processing and fails the task when any error occurs
    - `Continue`: Attempts to continue processing despite non-critical errors (eg.
      LLM refusals etc.)
    """

    expires_in: Optional[int]
    """
    The number of seconds until task is deleted. Expired tasks can **not** be
    updated, polled or accessed via web interface.
    """

    high_resolution: Optional[bool]
    """Whether to use high-resolution images for cropping and post-processing.

    (Latency penalty: ~7 seconds per page)
    """

    llm_processing: Optional[LlmProcessingParam]
    """Controls the LLM used for the task."""

    ocr_strategy: Optional[Literal["All", "Auto"]]
    """Controls the Optical Character Recognition (OCR) strategy.

    - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
    - `Auto`: Selectively applies OCR only to pages with missing or low-quality
      text. When text layer is present the bounding boxes from the text layer are
      used.
    """

    pipeline: Optional[Literal["Azure", "Chunkr"]]
    """
    Choose the provider whose models will be used for segmentation and OCR. The
    output will be unified to the Chunkr `output` format.
    """

    segment_processing: Optional[SegmentProcessingParam]
    """Defines how each segment type is handled when generating the final output.

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
    """

    segmentation_strategy: Optional[Literal["LayoutAnalysis", "Page"]]
    """Controls the segmentation strategy:

    - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
      `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
      segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
    - `Page`: Treats each page as a single segment. Faster processing, but without
      layout element detection and only simple chunking.
    """
