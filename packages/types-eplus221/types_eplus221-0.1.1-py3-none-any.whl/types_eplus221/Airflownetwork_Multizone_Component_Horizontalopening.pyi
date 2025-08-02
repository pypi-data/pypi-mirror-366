from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Component_Horizontalopening(EpBunch):
    """This object specifies the properties of air flow through a horizontal opening"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Air_Mass_Flow_Coefficient_When_Opening_Is_Closed: Annotated[float, Field(default=..., gt=0)]
    """Defined at 1 Pa pressure difference. Enter the coefficient used in the following equation:"""

    Air_Mass_Flow_Exponent_When_Opening_Is_Closed: Annotated[float, Field(ge=0.5, le=1.0, default=.65)]
    """Enter the exponent used in the following equation:"""

    Sloping_Plane_Angle: Annotated[float, Field(gt=0, le=90, default=90)]
    """Sloping plane angle = 90 is equivalent to fully open."""

    Discharge_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """The Discharge Coefficient indicates the fractional effectiveness"""