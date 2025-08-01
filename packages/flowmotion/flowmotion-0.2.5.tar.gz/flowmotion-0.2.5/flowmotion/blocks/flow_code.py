from .flow_block import FlowBlock


class FlowCode(FlowBlock):
    """
    Code block with syntax highlighting using FlowBlock base.
    """

    def __init__(self, filepath, font="JetBrains Mono", font_size=18, max_lines=21):
        """
        Initialize a FlowCode block.

        Args:
            filepath (str): Path to the source code file.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size in px (default: 18).
            max_lines (int): Max lines per rendered chunk (default: 21).
        """
        super().__init__(filepath, font, font_size, max_lines, True)
