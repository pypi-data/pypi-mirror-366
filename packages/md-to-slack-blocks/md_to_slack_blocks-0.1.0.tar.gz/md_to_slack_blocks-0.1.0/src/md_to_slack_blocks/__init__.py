"""Convert markdown text to Slack Block Kit JSON format."""

from .main import md_to_blocks, is_markdown

__version__ = "0.1.0"
__all__ = ["md_to_blocks", "is_markdown"] 