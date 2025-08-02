from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonebaseboard_Outdoortemperaturecontrolled(EpBunch):
    """Specifies outside temperature-controlled electric baseboard heating."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in Schedule should be fraction applied to capacity of the baseboard heat equipment, generally (0.0 - 1.0)"""

    Capacity_at_Low_Temperature: Annotated[float, Field(default=..., gt=0)]

    Low_Temperature: Annotated[float, Field(default=...)]

    Capacity_at_High_Temperature: Annotated[float, Field(default=..., ge=0)]

    High_Temperature: Annotated[float, Field(default=...)]

    Fraction_Radiant: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""