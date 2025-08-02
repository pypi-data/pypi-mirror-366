from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Fin(EpBunch):
    """Fins are usually shading surfaces that are perpendicular to a window or door."""

    Name: Annotated[str, Field(default=...)]

    Window_or_Door_Name: Annotated[str, Field(default=...)]

    Left_Extension_from_WindowDoor: Annotated[str, Field()]

    Left_Distance_Above_Top_of_Window: Annotated[str, Field()]

    Left_Distance_Below_Bottom_of_Window: Annotated[str, Field()]
    """N2 + N3 + height of Window/Door is height of Fin"""

    Left_Tilt_Angle_from_WindowDoor: Annotated[str, Field(default='90')]

    Left_Depth: Annotated[str, Field()]

    Right_Extension_from_WindowDoor: Annotated[str, Field()]

    Right_Distance_Above_Top_of_Window: Annotated[str, Field()]

    Right_Distance_Below_Bottom_of_Window: Annotated[str, Field()]
    """N7 + N8 + height of Window/Door is height of Fin"""

    Right_Tilt_Angle_from_WindowDoor: Annotated[str, Field(default='90')]

    Right_Depth: Annotated[str, Field()]