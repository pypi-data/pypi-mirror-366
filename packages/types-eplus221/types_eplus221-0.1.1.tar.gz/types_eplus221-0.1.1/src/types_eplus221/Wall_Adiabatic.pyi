from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Wall_Adiabatic(EpBunch):
    """Allows for simplified entry of interior walls."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone the surface is a part of"""

    Azimuth_Angle: Annotated[str, Field()]
    """Facing direction of outside of wall (S=180,N=0,E=90,W=270)"""

    Tilt_Angle: Annotated[str, Field(default='90')]
    """Walls are usually tilted 90 degrees"""

    Starting_X_Coordinate: Annotated[str, Field()]
    """Starting (x,y,z) coordinate is the Lower Left Corner of the Wall"""

    Starting_Y_Coordinate: Annotated[str, Field()]

    Starting_Z_Coordinate: Annotated[str, Field()]

    Length: Annotated[str, Field()]

    Height: Annotated[str, Field()]