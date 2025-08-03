# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .bounding_box import BoundingBox
from .llm_processing import LlmProcessing
from .chunk_processing import ChunkProcessing
from .segment_processing import SegmentProcessing

__all__ = [
    "Task",
    "Configuration",
    "Output",
    "OutputChunk",
    "OutputChunkSegment",
    "OutputChunkSegmentOcr",
    "OutputChunkSegmentSSCell",
    "OutputChunkSegmentSSCellStyle",
    "OutputChunkSegmentSSHeaderOcr",
    "OutputPage",
]


class Configuration(BaseModel):
    chunk_processing: ChunkProcessing
    """Controls the setting for the chunking and post-processing of each chunk."""

    error_handling: Literal["Fail", "Continue"]
    """Controls how errors are handled during processing:

    - `Fail`: Stops processing and fails the task when any error occurs
    - `Continue`: Attempts to continue processing despite non-critical errors (eg.
      LLM refusals etc.)
    """

    llm_processing: LlmProcessing
    """Controls the LLM used for the task."""

    ocr_strategy: Literal["All", "Auto"]
    """Controls the Optical Character Recognition (OCR) strategy.

    - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
    - `Auto`: Selectively applies OCR only to pages with missing or low-quality
      text. When text layer is present the bounding boxes from the text layer are
      used.
    """

    segment_processing: SegmentProcessing
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

    segmentation_strategy: Literal["LayoutAnalysis", "Page"]
    """Controls the segmentation strategy:

    - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
      `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
      segmentation and better chunking. (Latency penalty: ~TBD seconds per page).
    - `Page`: Treats each page as a single segment. Faster processing, but without
      layout element detection and only simple chunking.
    """

    expires_in: Optional[int] = None
    """
    The number of seconds until task is deleted. Expired tasks can **not** be
    updated, polled or accessed via web interface.
    """

    high_resolution: Optional[bool] = None
    """Whether to use high-resolution images for cropping and post-processing."""

    input_file_url: Optional[str] = None
    """The presigned URL of the input file."""

    pipeline: Optional[Literal["Azure", "Chunkr"]] = None

    target_chunk_length: Optional[int] = None
    """The target number of words in each chunk.

    If 0, each chunk will contain a single segment.
    """


class OutputChunkSegmentOcr(BaseModel):
    bbox: BoundingBox
    """Bounding box for an item. It is used for chunks, segments and OCR results."""

    text: str
    """The recognized text of the OCR result."""

    confidence: Optional[float] = None
    """The confidence score of the recognized text."""


class OutputChunkSegmentSSCellStyle(BaseModel):
    align: Optional[Literal["Left", "Center", "Right", "Justify"]] = None
    """Alignment of the cell content."""

    bg_color: Optional[str] = None
    """Background color of the cell (e.g., "#FFFFFF" or "#DAE3F3")."""

    font_face: Optional[str] = None
    """Font face/family of the cell (e.g., "Arial", "Daytona")."""

    is_bold: Optional[bool] = None
    """Whether the cell content is bold."""

    text_color: Optional[str] = None
    """Text color of the cell (e.g., "#000000" or "red")."""

    valign: Optional[Literal["Top", "Middle", "Bottom", "Baseline"]] = None
    """Vertical alignment of the cell content."""


class OutputChunkSegmentSSCell(BaseModel):
    cell_id: str
    """The cell ID."""

    range: str
    """Range of the cell."""

    text: str
    """Text content of the cell."""

    formula: Optional[str] = None
    """Formula of the cell."""

    hyperlink: Optional[str] = None
    """Hyperlink URL if the cell contains a link (e.g., "https://www.chunkr.ai")."""

    style: Optional[OutputChunkSegmentSSCellStyle] = None
    """Styling information for the cell including colors, fonts, and formatting."""

    value: Optional[str] = None
    """The computed/evaluated value of the cell.

    This represents the actual result after evaluating any formulas, as opposed to
    the raw text content. For cells with formulas, this is the calculated result;
    for cells with static content, this is typically the same as the text field.

    Example: text might show "3.14" (formatted to 2 decimal places) while value
    could be "3.141592653589793" (full precision).
    """


class OutputChunkSegmentSSHeaderOcr(BaseModel):
    bbox: BoundingBox
    """Bounding box for an item. It is used for chunks, segments and OCR results."""

    text: str
    """The recognized text of the OCR result."""

    confidence: Optional[float] = None
    """The confidence score of the recognized text."""


class OutputChunkSegment(BaseModel):
    bbox: BoundingBox
    """Bounding box for an item. It is used for chunks, segments and OCR results."""

    page_height: float
    """Height of the page/sheet containing the segment."""

    page_number: int
    """Page number/Sheet number of the segment."""

    page_width: float
    """Width of the page/sheet containing the segment."""

    segment_id: str
    """Unique identifier for the segment."""

    segment_type: Literal[
        "Caption",
        "Footnote",
        "Formula",
        "ListItem",
        "Page",
        "PageFooter",
        "PageHeader",
        "Picture",
        "SectionHeader",
        "Table",
        "Text",
        "Title",
    ]
    """
    All the possible types for a segment. Note: Different configurations will
    produce different types. Please refer to the documentation for more information.
    """

    confidence: Optional[float] = None
    """Confidence score of the layout analysis model"""

    content: Optional[str] = None
    """
    Content of the segment, will be either HTML or Markdown, depending on format
    chosen.
    """

    description: Optional[str] = None
    """Description of the segment, generated by the LLM."""

    embed: Optional[str] = None
    """Embeddable content of the segment."""

    html: Optional[str] = None
    """HTML representation of the segment."""

    image: Optional[str] = None
    """Presigned URL to the image of the segment."""

    llm: Optional[str] = None
    """LLM representation of the segment."""

    markdown: Optional[str] = None
    """Markdown representation of the segment."""

    ocr: Optional[List[OutputChunkSegmentOcr]] = None
    """OCR results for the segment."""

    segment_length: Optional[int] = None
    """Length of the segment in tokens."""

    ss_cells: Optional[List[OutputChunkSegmentSSCell]] = None
    """Cells of the segment. Only used for Spreadsheets."""

    ss_header_bbox: Optional[BoundingBox] = None
    """Bounding box of the header of the segment, if found.

    Only used for Spreadsheets.
    """

    ss_header_ocr: Optional[List[OutputChunkSegmentSSHeaderOcr]] = None
    """OCR results of the header of the segment, if found. Only used for Spreadsheets."""

    ss_header_range: Optional[str] = None
    """
    Header range of the segment, if found. The header can have overlap with the
    `segment.range` if the table contains the header, if the header is located in a
    different sheet, the header range will have no overlap with the `segment.range`.
    Only used for Spreadsheets.
    """

    ss_header_text: Optional[str] = None
    """Text content of the header of the segment, if found.

    Only used for Spreadsheets.
    """

    ss_range: Optional[str] = None
    """Range of the segment in Excel notation (e.g., A1:B5).

    Only used for Spreadsheets.
    """

    ss_sheet_name: Optional[str] = None
    """Name of the sheet containing the segment. Only used for Spreadsheets."""

    text: Optional[str] = None
    """Text content of the segment. Calculated by the OCR results."""


class OutputChunk(BaseModel):
    chunk_length: int
    """The total number of tokens in the chunk. Calculated by the `tokenizer`."""

    segments: List[OutputChunkSegment]
    """
    Collection of document segments that form this chunk. When
    `target_chunk_length` > 0, contains the maximum number of segments that fit
    within that length (segments remain intact). Otherwise, contains exactly one
    segment.
    """

    chunk_id: Optional[str] = None
    """The unique identifier for the chunk."""

    embed: Optional[str] = None
    """Suggested text to be embedded for the chunk.

    This text is generated by combining the embed content from each segment
    according to the configured embed sources (HTML, Markdown, LLM, or Content). Can
    be configured using `embed_sources` in the `SegmentProcessing` configuration.
    """


class OutputPage(BaseModel):
    image: str
    """The presigned URL of the page/sheet image."""

    page_height: float
    """The number of pages in the file."""

    page_number: int
    """The number of pages in the file."""

    page_width: float
    """The number of pages in the file."""

    dpi: Optional[float] = None
    """DPI of the page/sheet. All cropped images are scaled to this DPI."""

    ss_sheet_name: Optional[str] = None
    """The name of the sheet containing the page. Only used for Spreadsheets."""


class Output(BaseModel):
    chunks: List[OutputChunk]
    """Collection of document chunks, where each chunk contains one or more segments"""

    file_name: Optional[str] = None
    """The name of the file."""

    mime_type: Optional[str] = None
    """The MIME type of the file."""

    page_count: Optional[int] = None
    """The number of pages in the file."""

    pages: Optional[List[OutputPage]] = None
    """The pages of the file. Includes the image and metadata for each page."""

    pdf_url: Optional[str] = None
    """The presigned URL of the PDF file."""


class Task(BaseModel):
    configuration: Configuration

    created_at: datetime
    """The date and time when the task was created and queued."""

    message: str
    """A message describing the task's status or any errors that occurred."""

    status: Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]
    """The status of the task."""

    task_id: str
    """The unique identifier for the task."""

    expires_at: Optional[datetime] = None
    """The date and time when the task will expire."""

    finished_at: Optional[datetime] = None
    """The date and time when the task was finished."""

    output: Optional[Output] = None
    """The processed results of a document analysis task"""

    started_at: Optional[datetime] = None
    """The date and time when the task was started."""

    task_url: Optional[str] = None
    """The presigned URL of the task."""
