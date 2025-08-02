from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Coldest(EpBunch):
    """This SetpointManager is used in dual duct systems to reset"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    HVAC_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object."""

    Minimum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=20.)]

    Maximum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=50.)]

    Strategy: Annotated[Literal['MinimumTemperature'], Field(default='MinimumTemperature')]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""