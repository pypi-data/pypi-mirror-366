from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Multizone_Cooling_Average(EpBunch):
    """This setpoint manager sets the average supply air temperature based on the cooling load"""

    Name: Annotated[str, Field(default=...)]

    Hvac_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object"""

    Minimum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=12.)]

    Maximum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=18.)]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""