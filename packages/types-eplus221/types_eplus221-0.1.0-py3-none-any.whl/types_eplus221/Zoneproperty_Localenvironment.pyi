from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneproperty_Localenvironment(EpBunch):
    """This object defines the local environment properties of a zone object."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field()]
    """Enter the name of a zone object"""

    Outdoor_Air_Node_Name: Annotated[str, Field()]
    """Enter the name of an OutdoorAir:Node object"""