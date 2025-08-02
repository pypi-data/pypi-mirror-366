from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylighting_Delight_Complexfenestration(EpBunch):
    """Used for DElight Complex Fenestration of all types"""

    Name: Annotated[str, Field(default=...)]
    """Only used for user reference"""

    Complex_Fenestration_Type: Annotated[str, Field(default=...)]
    """Used to select the appropriate Complex Fenestration BTDF data"""

    Building_Surface_Name: Annotated[str, Field(default=...)]
    """This is a reference to a valid surface object (such as BuildingSurface:Detailed) hosting"""

    Window_Name: Annotated[str, Field(default=...)]
    """This is a reference to a valid FenestrationSurface:Detailed window object"""

    Fenestration_Rotation: Annotated[float, Field(default=0.0)]
    """In-plane counter-clockwise rotation angle of the Complex Fenestration"""