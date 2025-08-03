"""Core functionality for converting markdown to Slack Block Kit format."""

import re
from typing import Any, Dict, List


def md_to_blocks(markdown_text: str) -> List[Dict[str, Any]]:
    """Convert markdown text to Slack Block Kit JSON format.
    
    Args:
        markdown_text: The markdown text to convert
        
    Returns:
        List of Slack block objects
    """
    if not markdown_text or not markdown_text.strip():
        return []

    blocks = []
    lines = markdown_text.strip().split("\n")
    current_section_text: List[str] = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            if current_section_text:
                blocks.append(_create_section_block("\n".join(current_section_text)))
                current_section_text = []
            i += 1
            continue

        if line.startswith("#"):
            if current_section_text:
                blocks.append(_create_section_block("\n".join(current_section_text)))
                current_section_text = []

            header_text = re.sub(r"^#+\s*", "", line)
            blocks.append(_create_header_block(header_text))
            i += 1
            continue

        if re.match(r"^(-{3,}|\*{3,})$", line):
            if current_section_text:
                blocks.append(_create_section_block("\n".join(current_section_text)))
                current_section_text = []

            blocks.append(_create_divider_block())
            i += 1
            continue

        if line.startswith("```"):
            if current_section_text:
                blocks.append(_create_section_block("\n".join(current_section_text)))
                current_section_text = []

            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1

            code_text = "\n".join(code_lines)
            blocks.append(_create_section_block(f"```\n{code_text}\n```"))
            i += 1
            continue

        if line.startswith(">"):
            if current_section_text:
                blocks.append(_create_section_block("\n".join(current_section_text)))
                current_section_text = []

            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_line = re.sub(r"^>\s*", "", lines[i].strip())
                quote_lines.append(quote_line)
                i += 1

            quote_text = "\n".join(quote_lines)
            blocks.append(_create_section_block(f">{quote_text}"))
            continue

        current_section_text.append(line)
        i += 1

    if current_section_text:
        blocks.append(_create_section_block("\n".join(current_section_text)))

    return blocks


def is_markdown(text: str) -> bool:
    """Check if text contains markdown formatting.
    
    Args:
        text: Text to check
        
    Returns:
        True if text contains markdown formatting
    """
    if not text:
        return False

    patterns = [
        r"^\s*#+\s",                    # Headers
        r"\*\*.*?\*\*",                 # Bold **
        r"__.*?__",                     # Bold __
        r"(?<!\*)\*[^*]+?\*(?!\*)",     # Italic *
        r"(?<!_)_[^_]+?_(?!_)",         # Italic _
        r"~~.*?~~",                     # Strikethrough
        r"`.*?`",                       # Inline code
        r"```[\s\S]*?```",              # Code blocks
        r"^\s*>",                       # Block quotes
        r"^\s*[-*+]\s",                 # Lists
        r"^\s*\d+\.\s",                 # Numbered lists
        r"\[.*?\]\(.*?\)",              # Links
        r"^-{3,}$|^\*{3,}$",           # Horizontal rules
    ]

    return any(re.search(pattern, text, re.MULTILINE) for pattern in patterns)


def _create_section_block(text: str) -> Dict[str, Any]:
    """Create a section block with markdown text."""
    slack_text = _convert_markdown_to_slack(text)
    return {"type": "section", "text": {"type": "mrkdwn", "text": slack_text}}


def _create_header_block(text: str) -> Dict[str, Any]:
    """Create a header block with plain text."""
    header_text = text[:150] if len(text) > 150 else text
    return {"type": "header", "text": {"type": "plain_text", "text": header_text}}


def _create_divider_block() -> Dict[str, Any]:
    """Create a divider block."""
    return {"type": "divider"}


def _convert_markdown_to_slack(text: str) -> str:
    """Convert standard markdown formatting to Slack's mrkdwn format.
    
    Conversions:
    - **bold** or __bold__ -> *bold*
    - *italic* or _italic_ -> _italic_
    - ~~strikethrough~~ -> ~strikethrough~
    - `code` -> `code`
    - [link](url) -> <url|link>
    """
    result = text

    # Handle italic first to avoid conflicts with bold
    result = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"_\1_", result)
    result = re.sub(r"(?<!_)_([^_]+?)_(?!_)", r"_\1_", result)

    # Handle bold
    result = re.sub(r"\*\*(.*?)\*\*", r"*\1*", result)
    result = re.sub(r"__(.*?)__", r"*\1*", result)

    # Handle strikethrough
    result = re.sub(r"~~(.*?)~~", r"~\1~", result)

    # Handle links
    result = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"<\2|\1>", result)

    return result 