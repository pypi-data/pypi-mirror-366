from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylightingdevice_Lightwell(EpBunch):
    """Applies only to exterior windows in daylighting-controlled zones or"""

    Exterior_Window_Name: Annotated[str, Field(default=...)]

    Height_Of_Well: Annotated[float, Field(default=..., ge=0.0)]
    """Distance from Bottom of Window to Bottom of Well"""

    Perimeter_Of_Bottom_Of_Well: Annotated[float, Field(default=..., gt=0.0)]

    Area_Of_Bottom_Of_Well: Annotated[float, Field(default=..., gt=0.0)]

    Visible_Reflectance_Of_Well_Walls: Annotated[float, Field(default=..., ge=0.0, le=1.0)]