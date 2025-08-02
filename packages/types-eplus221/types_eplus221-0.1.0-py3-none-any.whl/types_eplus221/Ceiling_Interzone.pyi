from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Ceiling_Interzone(EpBunch):
    """Allows for simplified entry of ceilings using adjacent zone"""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone for the inside of the surface"""

    Outside_Boundary_Condition_Object: Annotated[str, Field(default=...)]
    """Specify a surface name in an adjacent zone for known interior floors"""

    Azimuth_Angle: Annotated[str, Field()]
    """Facing direction of outside of wall (S=180,N=0,E=90,W=270)"""

    Tilt_Angle: Annotated[str, Field(default='0')]
    """Ceilings are usually tilted 0 degrees"""

    Starting_X_Coordinate: Annotated[str, Field()]
    """If not Flat, should be Lower Left Corner (from outside)"""

    Starting_Y_Coordinate: Annotated[str, Field()]

    Starting_Z_Coordinate: Annotated[str, Field()]

    Length: Annotated[str, Field()]
    """Along X Axis"""

    Width: Annotated[str, Field()]
    """Along Y Axis"""