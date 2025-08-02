from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneinfiltration_Flowcoefficient(EpBunch):
    """Infiltration is specified as flow coefficient, schedule fraction, stack and wind coefficients, and"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Flow_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """"c" in Equation"""

    Stack_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """"Cs" in Equation"""

    Pressure_Exponent: Annotated[float, Field(gt=0, default=0.67)]
    """"n" in Equation"""

    Wind_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """"Cw" in Equation"""

    Shelter_Factor: Annotated[float, Field(default=..., gt=0)]
    """"s" in Equation"""