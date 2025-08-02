from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Localenvironment(EpBunch):
    """This object defines the local environment properties of an exterior surface."""

    Name: Annotated[str, Field(default=...)]

    Exterior_Surface_Name: Annotated[str, Field()]
    """Enter the name of an exterior surface object"""

    External_Shading_Fraction_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a Schedule object"""

    Surrounding_Surfaces_Object_Name: Annotated[str, Field()]
    """Enter the name of a SurfaceProperty:SurroundingSurfaces object"""

    Outdoor_Air_Node_Name: Annotated[str, Field()]
    """Enter the name of an OutdoorAir:Node object"""