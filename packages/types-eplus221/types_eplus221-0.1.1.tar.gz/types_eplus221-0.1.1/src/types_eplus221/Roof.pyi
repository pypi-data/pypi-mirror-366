from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roof(EpBunch):
    """Allows for simplified entry of roofs (exterior)."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone the surface is a part of"""

    Azimuth_Angle: Annotated[str, Field()]
    """Facing direction of outside of Roof"""

    Tilt_Angle: Annotated[str, Field(default='0')]
    """Flat Roofs are tilted 0 degrees"""

    Starting_X_Coordinate: Annotated[str, Field()]
    """If not Flat, Starting coordinate is the Lower Left Corner of the Roof"""

    Starting_Y_Coordinate: Annotated[str, Field()]

    Starting_Z_Coordinate: Annotated[str, Field()]

    Length: Annotated[str, Field()]
    """Along X Axis"""

    Width: Annotated[str, Field()]
    """Along Y Axis"""