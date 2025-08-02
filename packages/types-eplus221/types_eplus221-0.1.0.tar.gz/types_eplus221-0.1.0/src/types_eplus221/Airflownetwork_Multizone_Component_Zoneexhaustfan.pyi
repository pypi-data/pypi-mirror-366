from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Component_Zoneexhaustfan(EpBunch):
    """This object specifies the additional properties for a zone exhaust fan"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of a Fan:ZoneExhaust object."""

    Air_Mass_Flow_Coefficient_When_The_Zone_Exhaust_Fan_Is_Off_At_Reference_Conditions: Annotated[float, Field(default=..., gt=0)]
    """Enter the air mass flow coefficient at the conditions defined"""

    Air_Mass_Flow_Exponent_When_The_Zone_Exhaust_Fan_Is_Off: Annotated[float, Field(ge=0.5, le=1.0, default=0.65)]
    """Enter the exponent used in the following equation:"""

    Reference_Crack_Conditions: Annotated[str, Field()]
    """Select a AirflowNetwork:MultiZone:ReferenceCrackConditions name associated with"""