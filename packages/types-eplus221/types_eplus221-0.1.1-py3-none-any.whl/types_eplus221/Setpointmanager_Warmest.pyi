from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Warmest(EpBunch):
    """This SetpointManager resets the cooling supply air temperature"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    Hvac_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object"""

    Minimum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=12.)]

    Maximum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=18.)]

    Strategy: Annotated[Literal['MaximumTemperature'], Field(default='MaximumTemperature')]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""