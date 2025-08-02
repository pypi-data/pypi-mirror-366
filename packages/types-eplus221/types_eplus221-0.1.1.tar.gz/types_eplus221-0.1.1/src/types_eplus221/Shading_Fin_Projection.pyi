from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Fin_Projection(EpBunch):
    """Fins are usually shading surfaces that are perpendicular to a window or door."""

    Name: Annotated[str, Field(default=...)]

    Window_Or_Door_Name: Annotated[str, Field(default=...)]

    Left_Extension_From_Window_Door: Annotated[str, Field()]

    Left_Distance_Above_Top_Of_Window: Annotated[str, Field()]

    Left_Distance_Below_Bottom_Of_Window: Annotated[str, Field()]
    """N2 + N3 + height of Window/Door is height of Fin"""

    Left_Tilt_Angle_From_Window_Door: Annotated[str, Field(default='90')]

    Left_Depth_As_Fraction_Of_Window_Door_Width: Annotated[str, Field()]

    Right_Extension_From_Window_Door: Annotated[str, Field()]

    Right_Distance_Above_Top_Of_Window: Annotated[str, Field()]

    Right_Distance_Below_Bottom_Of_Window: Annotated[str, Field()]
    """N7 + N8 + height of Window/Door is height of Fin"""

    Right_Tilt_Angle_From_Window_Door: Annotated[str, Field(default='90')]

    Right_Depth_As_Fraction_Of_Window_Door_Width: Annotated[str, Field()]