from manim import *

from ...core.flow_group import FlowGroup


class FlowMarkup(FlowGroup):
    """
    A flow-aware MarkupText wrapper that integrates with FlowGroup.

    Automatically positions and formats the text for consistent rendering.
    """

    def __init__(self, text, font="JetBrains Mono", font_size=18):
        """
        Initialize a FlowMarkup block.

        Args:
            text (str): The markup text to render.
            font (str): Font used for rendering (default: JetBrains Mono).
            font_size (int): Font size (default: 18).
        """
        super().__init__()

        self.text = text
        self.font = font
        self.font_size = font_size

        self.markup = (
            MarkupText(text=self.text, font=self.font, font_size=self.font_size)
            .to_corner(UL, buff=0.5)
            .shift(DOWN * 0.325 + LEFT * 0.2)
        )

        self.add(self.markup)

    def show(self, mute=False):
        """
        Return an animation to show the markup — letter-by-letter or instant.
        """
        if mute:
            return (self.FlowAction.ADD, self)
        else:
            return (
                self.FlowAction.PLAY,
                AddTextLetterByLetter(self.markup, time_per_char=0.01),
            )
