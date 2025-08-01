from manim import *


class FlowUtils:
    @staticmethod
    def get_dynamic_text(data, **kwargs):
        """
        Return a Manim text object (Tex or Text) based on input data type.

        Args:
            data (int | float | str): The value to convert into a text object.
            **kwargs: Additional keyword arguments for the text object.

        Returns:
            Manim Tex or scaled Text object.
        """
        if isinstance(data, (int, float)):
            return Tex(str(data), **kwargs)  # For mathematical notation
        else:
            return Text(str(data), **kwargs).scale(0.7)  # Scaled regular text

    @staticmethod
    def get_labelled_shape(label, shape, **shape_properties):
        """
        Create a shape with a text label, grouped together.

        Args:
            label (str | int | float): The label to display on the shape.
            shape (Type[VMobject]): A Manim shape class (e.g., Circle, Square).
            **shape_properties: Properties passed to the shape constructor.

        Returns:
            VGroup: A group containing the label and the shape, with `.value` set to the label.
        """
        bounding_shape = shape(**shape_properties)
        label_text = FlowUtils.get_dynamic_text(label)

        group = VGroup(label_text, bounding_shape)
        group.value = label  # Optional property to track the label programmatically

        return group
