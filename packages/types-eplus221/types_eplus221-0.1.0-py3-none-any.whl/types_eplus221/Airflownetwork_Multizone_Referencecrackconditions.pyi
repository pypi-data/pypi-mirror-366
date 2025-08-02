from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Referencecrackconditions(EpBunch):
    """This object specifies the conditions under which the air mass flow coefficient was measured."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Reference_Temperature: Annotated[float, Field(default=20)]
    """Enter the reference temperature under which the surface crack data were obtained."""

    Reference_Barometric_Pressure: Annotated[float, Field(ge=31000, le=120000, default=101325)]
    """Enter the reference barometric pressure under which the surface crack data were obtained."""

    Reference_Humidity_Ratio: Annotated[float, Field(default=0)]
    """Enter the reference humidity ratio under which the surface crack data were obtained."""