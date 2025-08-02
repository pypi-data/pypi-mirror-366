from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Reliefairflow(EpBunch):
    """This object allows variation of air flow rate to perform pressure."""

    Name: Annotated[str, Field(default=...)]

    Outdoor_Air_Mixer_Name: Annotated[str, Field(default=...)]

    Air_Mass_Flow_Coefficient_When_No_Outdoor_Air_Flow_at_Reference_Conditions: Annotated[float, Field(default=..., gt=0)]
    """Enter the air mass flow coefficient at the conditions defined"""

    Air_Mass_Flow_Exponent_When_No_Outdoor_Air_Flow: Annotated[float, Field(ge=0.5, le=1.0, default=0.65)]
    """Enter the exponent used in the following equation:"""

    Reference_Crack_Conditions: Annotated[str, Field()]
    """Select a AirflowNetwork:MultiZone:ReferenceCrackConditions name associated with"""