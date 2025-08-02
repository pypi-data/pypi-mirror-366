from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Airboundary(EpBunch):
    """Indicates an open boundary between two zones. It may be used for base surfaces and fenestration surfaces."""

    Name: Annotated[str, Field(default=...)]

    Solar_And_Daylighting_Method: Annotated[Literal['GroupedZones', 'InteriorWindow'], Field(default='GroupedZones')]
    """This field controls how the surface is modeled for solar distribution and daylighting calculations."""

    Radiant_Exchange_Method: Annotated[Literal['GroupedZones', 'IRTSurface'], Field(default='GroupedZones')]
    """This field controls how the surface is modeled for radiant exchange calculations."""

    Air_Exchange_Method: Annotated[Literal['None', 'SimpleMixing'], Field()]
    """This field controls how air exchange is modeled across this boundary."""

    Simple_Mixing_Air_Changes_Per_Hour: Annotated[float, Field(ge=0, default=0.5)]
    """If the Air Exchange Method is SimpleMixing then this field specifies the air changes per hour"""

    Simple_Mixing_Schedule_Name: Annotated[str, Field()]
    """If the Air Exchange Method is SimpleMixing then this field specifies the air exchange schedule."""