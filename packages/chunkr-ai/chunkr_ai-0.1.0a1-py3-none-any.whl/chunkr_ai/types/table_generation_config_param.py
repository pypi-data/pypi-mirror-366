# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Optional
from typing_extensions import Literal, TypedDict

__all__ = ["TableGenerationConfigParam"]


class TableGenerationConfigParam(TypedDict, total=False):
    crop_image: Literal["All", "Auto"]
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: bool
    """Generate LLM descriptions for this segment"""

    embed_sources: List[Literal["Content", "HTML", "Markdown", "LLM"]]
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: bool
    """Use the full page image as context for LLM generation"""

    format: Literal["Html", "Markdown"]

    html: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str]
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]]
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Literal["LLM", "Auto", "Ignore"]
