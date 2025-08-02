from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Floor_Adiabatic(EpBunch):
    """Allows for simplified entry of exterior floors"""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone the surface is a part of"""

    Azimuth_Angle: Annotated[str, Field()]

    Tilt_Angle: Annotated[str, Field(default='180')]
    """Floors are usually tilted 180 degrees"""

    Starting_X_Coordinate: Annotated[str, Field()]
    """if not flat, should be lower left corner (from outside)"""

    Starting_Y_Coordinate: Annotated[str, Field()]

    Starting_Z_Coordinate: Annotated[str, Field()]

    Length: Annotated[str, Field()]
    """Along X Axis"""

    Width: Annotated[str, Field()]
    """Along Y Axis"""