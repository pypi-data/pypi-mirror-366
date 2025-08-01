from pygments import lex
from pygments.formatter import Formatter
from pygments.lexers import guess_lexer
from pygments.styles import get_style_by_name
from pygments.lexers.special import TextLexer

from ...core.flow_motion import FlowMotion


class FlowFormatter(FlowMotion, Formatter):
    """
    Base formatter for rendering styled, line-numbered text using Pygments.

    Supports both code and plain text input, producing span-tagged output
    compatible with Manim rendering in flowmotion.
    """

    def __init__(self, is_code=False, line_no=0, style_name="monokai"):
        """
        Initialize the formatter with optional code styling.

        Args:
            is_code (bool): Whether to apply syntax highlighting (default: False).
            line_no (int): Starting line number (default: 0).
            style_name (str): Pygments style to use (default: "monokai").
        """
        FlowMotion.__init__(self)
        Formatter.__init__(self, style=style_name)

        self.is_code = is_code
        self.line_num = line_no
        self.style_name = style_name
        self.styles = {}

        self.rjust_len = len(str(self.line_num)) + 1
        self.line_num_color = "#666666"

        style = get_style_by_name(style_name)

        for token, style_def in style:
            markup_style = {}
            if style_def["color"]:
                markup_style["foreground"] = f"#{style_def['color']}"
            if style_def["bold"]:
                markup_style["weight"] = "bold"
            if style_def["italic"]:
                markup_style["style"] = "italic"
            self.styles[token] = markup_style

    def get_line_num(self):
        """
        Increment and return the next line number.

        Returns:
            int: Current line number after increment.
        """
        self.line_num += 1
        return self.line_num

    def escape_xml(self, value):
        """
        Escape &, <, > for XML-safe rendering.

        Args:
            value (str): Text to escape.

        Returns:
            str: Escaped text.
        """
        return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def format_line(self, line):
        """
        Add line number and wrap line content in styled spans.

        Args:
            line (str): A single line of escaped content.

        Returns:
            str: Line with left-padded number and span wrapper.
        """
        line_str = (
            f'<span foreground="{self.line_num_color}">{str(self.get_line_num()).rjust(self.rjust_len)}</span>'
            f"<span> {line}</span>"
        )
        return line_str

    def highlight_lines(self, content):
        """
        Highlight and format all lines in a code/text block.

        Args:
            content (str): Full source content (code or plain text).

        Returns:
            list[str]: List of formatted lines with span-tagged styles.
        """
        if self.is_code:
            lexer = guess_lexer(content)
        else:
            lexer = TextLexer()

        tokens = lex(content, lexer)

        current_line = ""
        markup_lines = []

        for ttype, value in tokens:
            style_attrs = self.styles.get(ttype, {})
            attrs = " ".join(f'{key}="{val}"' for key, val in style_attrs.items())

            escaped = self.escape_xml(value)

            parts = escaped.split("\n")
            for i, part in enumerate(parts):
                if part:
                    if attrs:
                        current_line += f"<span {attrs}>{part}</span>"
                    else:
                        current_line += part

                if i < len(parts) - 1:
                    markup_lines.append(self.format_line(current_line))
                    current_line = ""

        if current_line:
            markup_lines.append(self.format_line(current_line))

        return markup_lines
