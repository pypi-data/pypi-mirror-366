# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .llm_generation_config import LlmGenerationConfig
from .auto_generation_config import AutoGenerationConfig
from .table_generation_config import TableGenerationConfig
from .ignore_generation_config import IgnoreGenerationConfig
from .picture_generation_config import PictureGenerationConfig

__all__ = ["SegmentProcessing"]


class SegmentProcessing(BaseModel):
    caption: Optional[AutoGenerationConfig] = FieldInfo(alias="Caption", default=None)
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

    footnote: Optional[AutoGenerationConfig] = FieldInfo(alias="Footnote", default=None)
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

    formula: Optional[LlmGenerationConfig] = FieldInfo(alias="Formula", default=None)
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

    list_item: Optional[AutoGenerationConfig] = FieldInfo(alias="ListItem", default=None)
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

    page: Optional[LlmGenerationConfig] = FieldInfo(alias="Page", default=None)
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

    page_footer: Optional[IgnoreGenerationConfig] = FieldInfo(alias="PageFooter", default=None)
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

    page_header: Optional[IgnoreGenerationConfig] = FieldInfo(alias="PageHeader", default=None)
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

    picture: Optional[PictureGenerationConfig] = FieldInfo(alias="Picture", default=None)
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

    section_header: Optional[AutoGenerationConfig] = FieldInfo(alias="SectionHeader", default=None)
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

    table: Optional[TableGenerationConfig] = FieldInfo(alias="Table", default=None)
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

    text: Optional[AutoGenerationConfig] = FieldInfo(alias="Text", default=None)
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

    title: Optional[AutoGenerationConfig] = FieldInfo(alias="Title", default=None)
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
