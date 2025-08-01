import os
from manim import *

from ..core.flow_group import FlowGroup
from .formatter import FlowFormatter
from .markup import FlowMarkup


class FlowBlock(FlowGroup):
    """
    Base class for rendering file-based text or code blocks in flowmotion.

    Handles reading, formatting, line chunking, and Manim markup conversion.
    """

    def __init__(
        self, filepath, font="JetBrains Mono", font_size=18, max_lines=21, is_code=False
    ):
        """
        Initialize a FlowBlock.

        Args:
            filepath (str): Path to the text/code file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
            is_code (bool): Whether to apply syntax highlighting (default: False).
            max_lines (int): Max lines per chunk/block (default: 21).
        """
        super().__init__()
        self.filepath = filepath
        self.font = font
        self.font_size = font_size
        self.max_lines = max_lines
        self.is_code = is_code

        self.filename = os.path.basename(self.filepath)
        self.formatter = FlowFormatter(is_code)
        self.content = self.read(filepath)

        self.highlighted_lines = self.formatter.highlight_lines(self.content)

        self.chunks = self.break_lines(self.highlighted_lines, self.max_lines)
        self.markups = self.markup_list(self.chunks)

    def read(self, filepath):
        """
        Read the entire file content.

        Args:
            filepath (str): Path to the file.

        Returns:
            str: File content as a string.
        """
        self.logger.info(f"[{self.__class__.__name__}][READING] {self.filename}")
        with open(filepath, "r") as file:
            return file.read().strip()

    def break_lines(self, lines: list, max_lines=21):
        """
        Break lines into chunks of size max_lines.

        Args:
            lines (list): List of highlighted lines.
            max_lines (int): Max number of lines per chunk.

        Returns:
            list: List of line chunks.
        """
        self.logger.info(f"[{self.__class__.__name__}][BREAKING] {self.filename}")
        return [
            "\n".join(lines[i : i + max_lines]) for i in range(0, len(lines), max_lines)
        ]

    def markup(self, chunk):
        """
        Convert a line chunk to a Manim MarkupText object.

        Args:
            chunk (str): Chunked block of text.

        Returns:
            MarkupText: Positioned and styled Manim text object.
        """
        markup_chunk = FlowMarkup(chunk)
        self.add(markup_chunk)
        return markup_chunk

    def markup_list(self, chunks):
        """
        Convert all line chunks to MarkupText objects.

        Args:
            chunks (list): List of text chunks.

        Returns:
            list: List of MarkupText objects.
        """

        self.logger.info(
            f"[{self.__class__.__name__}][CHUNKS] {self.filename} = {len(chunks)}"
        )
        return [self.markup(chunk) for chunk in chunks]

    def __iter__(self):
        """Yield FlowMarkup objects directly (let external logic decide play/add)."""
        return iter(self.markups)

    def __len__(self):
        """Return number of markup chunks."""
        return len(self.markups)
