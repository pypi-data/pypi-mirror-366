"""
FlowMotion Library
------------------
A lightweight animation framework built on top of Manim for visualizing algorithms and data flow.
"""

__version__ = "0.2.5"

import logging
from rich.logging import RichHandler
from .core import FlowGroup, FlowPointer
from .blocks import FlowBlock, FlowCode, FlowText
from .structs import FlowArray, FlowStack
from .scenes import FlowScene

__all__ = [
    "FlowGroup",
    "FlowArray",
    "FlowStack",
    "FlowPointer",
    "FlowScene",
    # Content Blocks
    "FlowBlock",
    "FlowCode",
    "FlowText",
]

try:
    from rich import print as rprint

    rprint(f"[bold cyan]FlowMotion[/] v{__version__}")
except ImportError:
    print(f"FlowMotion v{__version__}")

# Configure minimal Rich logger
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",  # Let RichHandler handle formatting
    handlers=[RichHandler()],
)

logger = logging.getLogger("flowmotion")
logger.setLevel(logging.INFO)
