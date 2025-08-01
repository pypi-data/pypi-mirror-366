from manim import *
from ..core import FlowGroup
from ..utils import FlowUtils


class FlowArray(FlowGroup):
    def __init__(self, elements: list, direction=RIGHT, extend_scope=1):
        """
        Initializes a FlowArray object for animating array-like structures.

        Args:
            elements (list): The initial list of logical values to display.
            direction (Direction): The direction in which the array is laid out (e.g., RIGHT, DOWN).
            extend_scope (int): Number of invisible "virtual" nodes added on both ends of the array.
        """
        super().__init__()

        self.direction = direction
        self.extend_scope = extend_scope

        self.build_array(elements)

    def build_array(self, elements):
        """
        Constructs the visual representation of the array, including virtual edge nodes.

        Args:
            elements (list): Logical values to visualize as labeled squares.

        This method:
            - Clears previous content (if any).
            - Adds virtual (invisible) edge nodes.
            - Adds value-containing groups (label + square).
            - Arranges all groups in the specified direction.
        """

        def add_element(value, is_extension=False):
            group = FlowUtils.get_labelled_shape(value, Square, side_length=1)
            if is_extension:
                group.set_opacity(0)
            self.add(group)

        for _ in range(self.extend_scope):  # Left edge nodes
            add_element(-1, is_extension=True)

        for elem in elements:  # Main elements
            add_element(elem)

        for _ in range(self.extend_scope):  # Right edge nodes
            add_element(-1, is_extension=True)

        self.arrange(self.direction, buff=0.1)
        self.move_to(ORIGIN)

    def swap(self, i: int, j: int, mute: bool = False):
        """
        Swaps the labels (and logical values) at indices `i` and `j` in the array.

        Parameters:
            i (int): Index of the first element to swap (0-based, excluding edge nodes).
            j (int): Index of the second element to swap.
            mute (bool): If True, skip animation and instantly update label positions.

        Returns:
            tuple: (FlowAction, AnimationGroup or None)
                - FlowAction.SKIP if mute is True.
                - FlowAction.PLAY and corresponding animation if mute is False.

        Notes:
            - The actual visual group at each index is a VGroup: [label, square].
            - Logical values are stored in the `.value` attribute of each VGroup.
        """
        group_i, group_j = self.get_group(i), self.get_group(j)
        label_i, label_j = self.get_label(i), self.get_label(j)

        # Compute positions for animation or instant move
        pos_i, pos_j = group_i.get_center(), group_j.get_center()

        # Define action depending on mute flag
        if mute:
            label_i.move_to(pos_j)
            label_j.move_to(pos_i)
            action = (self.FlowAction.SKIP, None)
        else:
            anim_i = MoveAlongPath(
                label_i, ArcBetweenPoints(pos_i, pos_j, angle=-PI / 2)
            )
            anim_j = MoveAlongPath(
                label_j, ArcBetweenPoints(pos_j, pos_i, angle=-PI / 2)
            )
            action = (self.FlowAction.PLAY, AnimationGroup(anim_i, anim_j))

        # Swap label positions in the visual group
        group_i[0], group_j[0] = label_j, label_i

        # Store current values before swapping
        value_i = self.get_value(i)
        value_j = self.get_value(j)

        # Set swapped values
        self.set_value(i, value_j)
        self.set_value(j, value_i)

        return action

    def update_value(self, i, new_value, mute=False):
        """
        Updates the label and stored value of the element at the given index.

        Args:
            i (int): Logical index of the element to update (excluding virtual edges).
            new_value (Any): The new value to assign and display in the array.
            mute (bool, optional): If True, updates the state silently without animation.
                                If False (default), performs a Transform animation.

        Returns:
            Tuple[FlowAction, Optional[AnimationGroup]]:
                - A FlowAction enum indicating whether to PLAY or SKIP the animation.
                - An AnimationGroup containing the label transformation (or None if muted).

        Raises:
            IndexError: If the provided index is out of bounds.
        """
        group = self.get_group(i)
        old_label = self.get_label(i)
        new_label = FlowUtils.get_dynamic_text(new_value).move_to(group.get_center())

        action = None

        if mute:
            group[0] = new_label
            group.value = new_value
            action = (self.FlowAction.SKIP, None)
        else:
            action = (
                self.FlowAction.PLAY,
                AnimationGroup(Transform(old_label, new_label)),
            )

        return action

    def highlight(self, i, color=YELLOW, mute=False):
        label = self.get_label(i)
        if mute:
            return (self.FlowAction.SKIP, None)
        else:
            return (self.FlowAction.PLAY, Indicate(label))

    def get_group(self, index):
        """
        Retrieves the full VGroup (label + square) at the given logical index.

        Args:
            index (int): Logical index within the array (excluding edge padding).

        Returns:
            VGroup: A VGroup containing the label and square at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return self.submobjects[index + self.extend_scope]

    def get_label(self, index):
        """
        Retrieves the label Mobject from the specified logical index.

        Args:
            index (int): Logical index in the array.

        Returns:
            Mobject: The label at the specified index.
        """
        return self.get_group(index)[0]

    def get_square(self, index):
        """
        Retrieves the square Mobject (background box) from the specified index.

        Args:
            index (int): Logical index in the array.

        Returns:
            Square: The square representing the element's container.
        """
        return self.get_group(index)[1]

    def get_value(self, index):
        """
        Retrieves the logical value stored in the VGroup at the specified index.

        Args:
            index (int): Logical index in the array.

        Returns:
            Any: The value assigned to the group via the `value` attribute.
        """
        return self.get_group(index).value

    def get_values(self):
        """
        Returns a list of the logical values stored in the array.

        This excludes any values from the virtual edge nodes.

        Returns:
            List[Any]: List of values stored in the visual array.
        """
        return [self.get_value(i) for i in range(len(self))]

    def set_value(self, index: int, value):
        """
        Sets the logical value at the specified index.

        Parameters:
            index (int): Logical index (excluding edge nodes).
            value (Any): Value to assign to the group's `.value` attribute.
        """
        self.get_group(index).value = value

    def __str__(self):
        """
        Returns a readable string representation of the array's logical state.

        Returns:
            str: A string showing the list of stored values.
        """
        return f"FlowArray({self.get_values()})"

    def __len__(self):
        """
        Returns the number of actual (non-virtual) elements in the array.

        Returns:
            int: Logical length of the array.
        """
        return len(self.submobjects) - 2 * self.extend_scope

    def __iter__(self):
        """
        Allows iteration over the array's real elements, excluding virtual edge nodes.

        Returns:
            Iterator[VGroup]: Iterator over the core VGroups.
        """
        return iter(self.submobjects[self.extend_scope : -self.extend_scope])

    def __getitem__(self, index: int):
        """
        Enables direct access to the VGroup at a logical index using bracket notation.

        Args:
            index (int): Logical index.

        Returns:
            VGroup: The group at the specified logical index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return self.get_group(index)
