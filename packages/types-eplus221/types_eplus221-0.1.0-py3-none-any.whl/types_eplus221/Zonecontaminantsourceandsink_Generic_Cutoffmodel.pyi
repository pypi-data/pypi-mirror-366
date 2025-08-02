from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontaminantsourceandsink_Generic_Cutoffmodel(EpBunch):
    """Simulate generic contaminant source driven by the cutoff concentration model."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Design_Generation_Rate_Coefficient: Annotated[float, Field(ge=0.0)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the"""

    Cutoff_Generic_Contaminant_At_Which_Emission_Ceases: Annotated[float, Field(gt=0.0)]
    """When the zone concentration level is greater than the cutoff level, emission stops,"""