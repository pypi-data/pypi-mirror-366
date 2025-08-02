from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontaminantsourceandsink_Carbondioxide(EpBunch):
    """Represents internal CO2 gains and sinks in the zone."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Design_Generation_Rate: Annotated[float, Field()]
    """Positive values represent sources and negative values represent sinks."""

    Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the Design Generation Rate"""