# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["AutoGenerationConfig"]


class AutoGenerationConfig(BaseModel):
    crop_image: Optional[Literal["All", "Auto"]] = None
    """Controls the cropping strategy for an item (e.g. segment, chunk, etc.)

    - `All` crops all images in the item
    - `Auto` crops images only if required for post-processing
    """

    description: Optional[bool] = None
    """Generate LLM descriptions for this segment"""

    embed_sources: Optional[List[Literal["Content", "HTML", "Markdown", "LLM"]]] = None
    """**DEPRECATED**: `embed` field is auto populated"""

    extended_context: Optional[bool] = None
    """Use the full page image as context for LLM generation"""

    format: Optional[Literal["Html", "Markdown"]] = None

    html: Optional[Literal["LLM", "Auto", "Ignore"]] = None
    """**DEPRECATED**: Use `format: html` and `strategy` instead."""

    llm: Optional[str] = None
    """**DEPRECATED**: use description instead"""

    markdown: Optional[Literal["LLM", "Auto", "Ignore"]] = None
    """**DEPRECATED**: Use `format: markdown` and `strategy` instead."""

    strategy: Optional[Literal["LLM", "Auto", "Ignore"]] = None
