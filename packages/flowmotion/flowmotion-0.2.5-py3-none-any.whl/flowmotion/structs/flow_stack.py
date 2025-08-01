from manim import *
from ..core import FlowGroup


class FlowStack(FlowGroup):
    def __init__(self, stack_height, stack_width, direction=UP, elem_height=None):
        """
        Initializes the FlowArray with virtual edge nodes and animatable content.
        """
        super().__init__()
        self.stack_height, self.stack_width = stack_height, stack_width
        self.direction = direction
        self.left = None
        self.right = None
        self.bottom = None
        self.stack = []
        self.values = []
        self.offset = self.direction * 0.3
        self.elem_height = elem_height
        self._initialize_stack_mobjects()

    def _initialize_stack_mobjects(self):
        self.logger.log(f"Width: {self.stack_width}, Height: {self.stack_height}")
        # Left and right walls
        left = Line(ORIGIN, UP * self.stack_height, stroke_width=3).shift(
            LEFT * self.stack_width / 2
        )
        right = Line(ORIGIN, UP * self.stack_height, stroke_width=3).shift(
            RIGHT * self.stack_width / 2
        )
        # Bottom connector
        bottom = Line(left.get_start(), right.get_start(), stroke_width=3)
        group = VGroup(left, right, bottom)

        angle = angle_between_vectors(UP, self.direction)
        if np.cross(UP, self.direction)[2] < 0:
            angle = TAU - angle
        group.rotate(angle)
        self.add(group)

        self.left, self.right, self.bottom = left, right, bottom
        self.move_to(ORIGIN)

    def push(self, value):
        """
        Animates pushing a new value onto the stack:
        - Creates a 16:9 rectangle with width equal to the stack's inner width.
        - Labels it with the provided value.
        - Animates the box sliding into its position in the stack.
        """
        self.logger.log(f"Pushing value: {value}")
        self.values.append(value)

        # Compute 16:9 dimensions based on stack width
        elem_width = self.stack_width
        elem_height = (
            self.elem_height if self.elem_height else self.stack_width * 9 / 16
        )

        # Create visual node (rectangle + label)
        rect = Rectangle(width=elem_width, height=elem_height, stroke_width=3)
        rect.rotate(angle_between_vectors(UP, self.direction))

        label = self.choose_text_type(value).scale(0.6).move_to(rect.get_center())

        # Add Node
        node = VGroup(rect, label)
        self.add(node)

        if self.stack:
            top_node = self.stack[-1]
            target = top_node.get_center() + self.direction * elem_height
        else:
            target = self.bottom.get_center() + self.direction * (elem_height / 2)

        # Start off-screen and animate in
        self.stack.append(node)
        start = target + self.offset
        node.move_to(start)

        # Returning order matters here
        return AnimationGroup(FadeIn(node), node.animate.shift(-self.offset))

    def empty(self):
        return len(self.stack) == 0

    def top(self):
        if self.stack:
            self.logger.log("Accessing top value")
            return Circumscribe(self.stack[-1])
        else:
            self.logger.log("Accessing top value when empty")
            return None

    def pop(self):
        if self.stack:
            self.logger.log("Popping Element")
            top_node = self.stack.pop()
            offset = self.direction * top_node.height
            anim = AnimationGroup(top_node.animate.shift(offset).set_opacity(0))
            self.remove(top_node)
            self.values.pop()
            return anim
        else:
            self.logger.log("Popping Element when none exists")
            return None

    def top_val(self):
        return self.values[-1]
