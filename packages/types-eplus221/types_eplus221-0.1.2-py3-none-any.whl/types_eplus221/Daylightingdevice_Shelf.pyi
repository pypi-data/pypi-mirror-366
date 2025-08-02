from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylightingdevice_Shelf(EpBunch):
    """Defines a daylighting which can have an inside shelf, an outside shelf, or both."""

    Name: Annotated[str, Field(default=...)]

    Window_Name: Annotated[str, Field(default=...)]

    Inside_Shelf_Name: Annotated[str, Field()]
    """This must refer to a BuildingSurface:Detailed or equivalent object"""

    Outside_Shelf_Name: Annotated[str, Field()]
    """This must refer to a Shading:Zone:Detailed object"""

    Outside_Shelf_Construction_Name: Annotated[str, Field()]
    """Required if outside shelf is specified"""

    View_Factor_to_Outside_Shelf: Annotated[float, Field(ge=0.0, le=1.0)]