from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneinfiltration_Effectiveleakagearea(EpBunch):
    """Infiltration is specified as effective leakage area at 4 Pa, schedule fraction, stack and wind coefficients, and"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Effective_Air_Leakage_Area: Annotated[float, Field(default=..., gt=0)]
    """"AL" in Equation"""

    Stack_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """"Cs" in Equation"""

    Wind_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """"Cw" in Equation"""