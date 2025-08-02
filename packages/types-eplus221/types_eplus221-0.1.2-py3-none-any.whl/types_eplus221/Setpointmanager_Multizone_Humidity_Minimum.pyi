from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Multizone_Humidity_Minimum(EpBunch):
    """This setpoint manager sets the minimum supply air humidity ratio based on humidification"""

    Name: Annotated[str, Field(default=...)]

    HVAC_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object"""

    Minimum_Setpoint_Humidity_Ratio: Annotated[float, Field(gt=0.0, default=0.005)]

    Maximum_Setpoint_Humidity_Ratio: Annotated[float, Field(gt=0.0, default=0.012)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the humidity ratio will be set"""