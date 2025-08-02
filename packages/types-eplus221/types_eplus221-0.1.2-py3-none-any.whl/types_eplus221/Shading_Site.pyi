from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Shading_Site(EpBunch):
    """used for shading elements such as trees"""

    Name: Annotated[str, Field(default=...)]

    Azimuth_Angle: Annotated[str, Field()]
    """Facing direction of outside of shading device (S=180,N=0,E=90,W=270)"""

    Tilt_Angle: Annotated[str, Field(default='90')]

    Starting_X_Coordinate: Annotated[str, Field()]
    """Starting coordinate is the Lower Left Corner of the Shade"""

    Starting_Y_Coordinate: Annotated[str, Field()]

    Starting_Z_Coordinate: Annotated[str, Field()]

    Length: Annotated[str, Field()]

    Height: Annotated[str, Field()]