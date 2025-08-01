from .flow_block import FlowBlock


class FlowText(FlowBlock):
    """
    Block for displaying plain text with line numbers.
    """

    def __init__(self, filepath, font="JetBrains Mono", font_size=18, max_lines=21):
        """
        Initialize a FlowText block.

        Args:
            filepath (str): Path to the text file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
            max_lines (int): Max lines per rendered chunk (default: 21).
        """
        super().__init__(filepath, font, font_size, max_lines, False)
