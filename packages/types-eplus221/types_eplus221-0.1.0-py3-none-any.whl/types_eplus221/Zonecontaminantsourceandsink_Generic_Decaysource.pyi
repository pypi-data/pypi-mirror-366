from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontaminantsourceandsink_Generic_Decaysource(EpBunch):
    """Simulate generic contaminant source driven by the cutoff concentration model."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Initial_Emission_Rate: Annotated[float, Field(ge=0.0)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the"""

    Delay_Time_Constant: Annotated[float, Field(gt=0.0)]