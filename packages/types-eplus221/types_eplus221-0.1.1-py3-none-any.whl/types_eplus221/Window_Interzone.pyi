from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Window_Interzone(EpBunch):
    """Allows for simplified entry of interzone windows (adjacent to"""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Building_Surface_Name: Annotated[str, Field(default=...)]
    """Name of Surface (Wall, usually) the Window is on (i.e., Base Surface)"""

    Outside_Boundary_Condition_Object: Annotated[str, Field()]
    """Specify a surface name in an adjacent zone for known interior windows."""

    Multiplier: Annotated[str, Field(default='1.0')]
    """Used only for Surface Type = WINDOW, GLASSDOOR or DOOR"""

    Starting_X_Coordinate: Annotated[str, Field()]
    """Window starting coordinate is specified relative to the Base Surface origin."""

    Starting_Z_Coordinate: Annotated[str, Field()]
    """How far up the wall the Window starts. (in 2-d, this would be a Y Coordinate)"""

    Length: Annotated[str, Field()]

    Height: Annotated[str, Field()]