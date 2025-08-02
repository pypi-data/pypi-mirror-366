from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Multizone_Surface_Crack(EpBunch):
    """This object specifies the properties of airflow through a crack."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Air_Mass_Flow_Coefficient_At_Reference_Conditions: Annotated[float, Field(default=..., gt=0)]
    """Enter the air mass flow coefficient at the conditions defined"""

    Air_Mass_Flow_Exponent: Annotated[float, Field(ge=0.5, le=1.0, default=0.65)]
    """Enter the air mass flow exponent for the surface crack."""

    Reference_Crack_Conditions: Annotated[str, Field()]
    """Select a AirflowNetwork:MultiZone:ReferenceCrackConditions name associated with"""