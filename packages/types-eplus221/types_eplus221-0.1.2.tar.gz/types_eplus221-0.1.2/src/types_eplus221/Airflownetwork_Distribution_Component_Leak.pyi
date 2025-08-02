from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Leak(EpBunch):
    """This object defines the characteristics of a supply or return air leak."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Air_Mass_Flow_Coefficient: Annotated[float, Field(default=..., gt=0)]
    """Defined at 1 Pa pressure difference across this component."""

    Air_Mass_Flow_Exponent: Annotated[float, Field(ge=0.5, le=1.0, default=0.65)]
    """Enter the exponent used in the following equation:"""