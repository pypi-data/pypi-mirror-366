from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Component_Simpleopening(EpBunch):
    """This object specifies the properties of air flow through windows and doors (window, door and"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Air_Mass_Flow_Coefficient_When_Opening_is_Closed: Annotated[float, Field(default=..., gt=0)]
    """Defined at 1 Pa pressure difference. Enter the coefficient used in the following equation:"""

    Air_Mass_Flow_Exponent_When_Opening_is_Closed: Annotated[float, Field(ge=0.5, le=1.0, default=.65)]
    """Enter the exponent used in the following equation:"""

    Minimum_Density_Difference_for_TwoWay_Flow: Annotated[float, Field(default=..., gt=0)]
    """Enter the minimum density difference above which two-way flow may occur due to stack effect."""

    Discharge_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """The Discharge Coefficient indicates the fractional effectiveness"""