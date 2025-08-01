import logging
from enum import Enum


class FlowMotion:
    """
    Base class for flowmotion objects providing action types and logging.
    """

    class FlowAction(Enum):
        ADD = "ADD"
        PLAY = "PLAY"
        SKIP = "SKIP"
        REMOVE = "REMOVE"

    def __init__(self):
        self.logger = logging.getLogger(f"flowmotion.{self.__class__.__name__}")
