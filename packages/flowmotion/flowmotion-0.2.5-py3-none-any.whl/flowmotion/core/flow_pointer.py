from manim import *
from .flow_group import FlowGroup


class FlowPointer(FlowGroup):
    def __init__(self, label, direction=UP):
        super().__init__()
        self.logger.log(f"Direction: {direction}")
        self.logger.log(f"Label: {label}")

        self.direction = direction
        self.label = Tex(str(label))
        self.arrow = Vector(normalize(direction) * 0.8, color=YELLOW)

        self.group = VGroup(self.arrow, self.label)
        self.group.arrange(-1 * self.direction, buff=0.2)
        self.add(self.group)

        self.move_to(ORIGIN)

    def place(self, mobject: Mobject, buff=0.2):
        """
        Move the pointer to point to a specific mobject.
        """
        target_pos = (
            mobject.get_edge_center(-self.direction) - normalize(self.direction) * buff
        )
        pointer_pos = self.arrow.get_end()
        shift_vector = target_pos - pointer_pos
        self.logger.log(
            f"Shifting: {np.round(pointer_pos,1)} -> {np.round(target_pos,1)}"
        )
        return self.shift(shift_vector)

    def point_to(self, mobject: Mobject):
        """
        Animate the pointer to point to a specific mobject.
        """
        return AnimationGroup(self.animate.place(mobject))
