from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfacecontaminantsourceandsink_Generic_Pressuredriven(EpBunch):
    """Simulate generic contaminant source driven by the pressure difference across a surface."""

    Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Design_Generation_Rate_Coefficient: Annotated[float, Field(ge=0.0)]

    Generation_Schedule_Name: Annotated[str, Field(default=...)]
    """Value in this schedule should be a fraction (generally 0.0 - 1.0) applied to the"""

    Generation_Exponent: Annotated[float, Field(gt=0.0, le=1.0)]