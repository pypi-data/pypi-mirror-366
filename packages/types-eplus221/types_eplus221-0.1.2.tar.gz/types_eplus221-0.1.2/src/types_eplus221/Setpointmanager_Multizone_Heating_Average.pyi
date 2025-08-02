from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Multizone_Heating_Average(EpBunch):
    """This setpoint manager sets the average supply air temperature based on the heating load"""

    Name: Annotated[str, Field(default=...)]

    HVAC_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object"""

    Minimum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=20.)]

    Maximum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=50.)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""