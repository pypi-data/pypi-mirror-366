from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneairbalance_Outdoorair(EpBunch):
    """Provide a combined zone outdoor air flow by including interactions between"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Air_Balance_Method: Annotated[Literal['Quadrature', 'None'], Field(default='Quadrature')]
    """None: Only perform simple calculations without using a combined zone outdoor air."""

    Induced_Outdoor_Air_Due_to_Unbalanced_Duct_Leakage: Annotated[float, Field(ge=0, default=0)]

    Induced_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """This schedule contains the fraction values applied to the Induced Outdoor Air given in the"""