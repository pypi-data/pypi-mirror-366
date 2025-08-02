from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Singlezone_Onestageheating(EpBunch):
    """This object can be used with CoilSystem:Heating:DX, Coil:Heating:Fuel,"""

    Name: Annotated[str, Field(default=...)]

    Heating_Stage_On_Supply_Air_Setpoint_Temperature: Annotated[str, Field(default='99')]
    """This is the setpoint value applied when heating device is to cycle ON"""

    Heating_Stage_Off_Supply_Air_Setpoint_Temperature: Annotated[str, Field(default='-99')]
    """This is the setpoint value applied when heating device is to cycle OFF"""

    Control_Zone_Name: Annotated[str, Field(default=...)]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""