from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowgap_Deflectionstate(EpBunch):
    """Used to enter data describing deflection state of the gap. It is referenced from"""

    Name: Annotated[str, Field(default=...)]

    Deflected_Thickness: Annotated[float, Field(ge=0.0, default=0.0)]
    """If left blank will be considered that gap has no deflection."""

    Initial_Temperature: Annotated[float, Field(ge=0.0, default=25)]

    Initial_Pressure: Annotated[float, Field(ge=0.0, default=101325)]