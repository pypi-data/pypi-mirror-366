from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Daylightingdevice_Lightwell(EpBunch):
    """Applies only to exterior windows in daylighting-controlled zones or"""

    Exterior_Window_Name: Annotated[str, Field(default=...)]

    Height_of_Well: Annotated[float, Field(default=..., ge=0.0)]
    """Distance from Bottom of Window to Bottom of Well"""

    Perimeter_of_Bottom_of_Well: Annotated[float, Field(default=..., gt=0.0)]

    Area_of_Bottom_of_Well: Annotated[float, Field(default=..., gt=0.0)]

    Visible_Reflectance_of_Well_Walls: Annotated[float, Field(default=..., ge=0.0, le=1.0)]