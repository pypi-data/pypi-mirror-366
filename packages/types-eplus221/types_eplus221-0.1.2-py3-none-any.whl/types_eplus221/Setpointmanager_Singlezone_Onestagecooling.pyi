from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Singlezone_Onestagecooling(EpBunch):
    """This object can be used with CoilSystem:Cooling:DX to model on/off cycling control"""

    Name: Annotated[str, Field(default=...)]

    Cooling_Stage_On_Supply_Air_Setpoint_Temperature: Annotated[str, Field(default='-99')]
    """This is the setpoint value applied when cooling device is to cycle ON"""

    Cooling_Stage_Off_Supply_Air_Setpoint_Temperature: Annotated[str, Field(default='99')]
    """This is the setpoint value applied when cooling device is to cycle OFF"""

    Control_Zone_Name: Annotated[str, Field(default=...)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""