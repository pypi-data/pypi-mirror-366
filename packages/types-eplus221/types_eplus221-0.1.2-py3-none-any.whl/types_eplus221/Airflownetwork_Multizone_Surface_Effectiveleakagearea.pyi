from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Surface_Effectiveleakagearea(EpBunch):
    """This object is used to define surface air leakage."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Effective_Leakage_Area: Annotated[float, Field(default=..., gt=0)]
    """Enter the effective leakage area."""

    Discharge_Coefficient: Annotated[float, Field(gt=0, default=1.0)]
    """Enter the coefficient used in the air mass flow equation."""

    Reference_Pressure_Difference: Annotated[float, Field(gt=0, default=4.0)]
    """Enter the pressure difference used to define the air mass flow coefficient and exponent."""

    Air_Mass_Flow_Exponent: Annotated[float, Field(ge=0.5, le=1.0, default=.65)]
    """Enter the exponent used in the air mass flow equation."""