from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Underwater(EpBunch):
    """This object sets up a convective water boundary condition for a surface"""

    Name: Annotated[str, Field(default=...)]

    Distance_from_Surface_Centroid_to_Leading_Edge_of_Boundary_Layer: Annotated[float, Field(default=...)]
    """This is the distance from the leading edge of the boundary layer development"""

    Free_Stream_Water_Temperature_Schedule: Annotated[str, Field(default=...)]

    Free_Stream_Water_Velocity_Schedule: Annotated[str, Field()]