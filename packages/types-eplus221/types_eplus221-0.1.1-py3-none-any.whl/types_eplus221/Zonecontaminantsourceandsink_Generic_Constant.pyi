from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontaminantsourceandsink_Generic_Constant(EpBunch):
    """Sets internal generic contaminant gains and sinks in a zone with constant values."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Design_Generation_Rate: Annotated[float, Field(ge=0.0)]
    """The values represent source."""

    Generation_Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the Design Generation Rate"""

    Design_Removal_Coefficient: Annotated[float, Field(ge=0.0)]
    """The value represent sink."""

    Removal_Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the"""