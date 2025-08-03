# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo
from .llm_generation_config_param import LlmGenerationConfigParam
from .auto_generation_config_param import AutoGenerationConfigParam
from .table_generation_config_param import TableGenerationConfigParam
from .ignore_generation_config_param import IgnoreGenerationConfigParam
from .picture_generation_config_param import PictureGenerationConfigParam

__all__ = ["SegmentProcessingParam"]


class SegmentProcessingParam(TypedDict, total=False):
    caption: Annotated[Optional[AutoGenerationConfigParam], PropertyInfo(alias="Caption")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    footnote: Annotated[Optional[AutoGenerationConfigParam], PropertyInfo(alias="Footnote")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    formula: Annotated[Optional[LlmGenerationConfigParam], PropertyInfo(alias="Formula")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    list_item: Annotated[Optional[AutoGenerationConfigParam], PropertyInfo(alias="ListItem")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    page: Annotated[Optional[LlmGenerationConfigParam], PropertyInfo(alias="Page")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    page_footer: Annotated[Optional[IgnoreGenerationConfigParam], PropertyInfo(alias="PageFooter")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    page_header: Annotated[Optional[IgnoreGenerationConfigParam], PropertyInfo(alias="PageHeader")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    picture: Annotated[Optional[PictureGenerationConfigParam], PropertyInfo(alias="Picture")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    section_header: Annotated[Optional[AutoGenerationConfigParam], PropertyInfo(alias="SectionHeader")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    table: Annotated[Optional[TableGenerationConfigParam], PropertyInfo(alias="Table")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    text: Annotated[Optional[AutoGenerationConfigParam], PropertyInfo(alias="Text")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """

    title: Annotated[Optional[AutoGenerationConfigParam], PropertyInfo(alias="Title")]
    """Controls the processing and generation for the segment.

    - `crop_image` controls whether to crop the file's images to the segment's
      bounding box. The cropped image will be stored in the segment's `image` field.
      Use `All` to always crop, or `Auto` to only crop when needed for
      post-processing.
    - `format` specifies the output format: `Html` or `Markdown`
    - `strategy` determines how the content is generated: `Auto`, `LLM`, or `Ignore`
      - `Auto`: Process content automatically
      - `LLM`: Use large language models for processing
      - `Ignore`: Exclude segments from final output
    - `description` enables LLM-generated descriptions for segments

    **Deprecated fields (for backwards compatibility):**

    - `llm` - **DEPRECATED**: Use `description` instead
    - `embed_sources` - **DEPRECATED**: Embed field is auto-populated
    - `html` - **DEPRECATED**: Use `format: Html` and `strategy` instead
    - `markdown` - **DEPRECATED**: Use `format: Markdown` and `strategy` instead
    """
