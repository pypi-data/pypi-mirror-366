from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Overhang_Projection(EpBunch):
    """Overhangs are typically flat shading surfaces that reference a window or door."""

    Name: Annotated[str, Field(default=...)]

    Window_or_Door_Name: Annotated[str, Field(default=...)]

    Height_above_Window_or_Door: Annotated[str, Field()]

    Tilt_Angle_from_WindowDoor: Annotated[str, Field(default='90')]

    Left_extension_from_WindowDoor_Width: Annotated[str, Field()]

    Right_extension_from_WindowDoor_Width: Annotated[str, Field()]
    """N3 + N4 + Window/Door Width is Overhang Length"""

    Depth_as_Fraction_of_WindowDoor_Height: Annotated[str, Field()]