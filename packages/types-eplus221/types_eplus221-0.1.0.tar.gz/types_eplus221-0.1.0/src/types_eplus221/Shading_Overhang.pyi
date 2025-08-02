from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Overhang(EpBunch):
    """Overhangs are usually flat shading surfaces that reference a window or door."""

    Name: Annotated[str, Field(default=...)]

    Window_Or_Door_Name: Annotated[str, Field(default=...)]

    Height_Above_Window_Or_Door: Annotated[str, Field()]

    Tilt_Angle_From_Window_Door: Annotated[str, Field(default='90')]

    Left_Extension_From_Window_Door_Width: Annotated[str, Field()]

    Right_Extension_From_Window_Door_Width: Annotated[str, Field()]
    """N3 + N4 + Window/Door Width is Overhang Length"""

    Depth: Annotated[str, Field()]