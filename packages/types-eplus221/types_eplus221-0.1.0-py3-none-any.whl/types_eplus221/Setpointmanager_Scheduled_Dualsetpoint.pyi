from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Scheduled_Dualsetpoint(EpBunch):
    """This setpoint manager places a high and low schedule value"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    High_Setpoint_Schedule_Name: Annotated[str, Field(default=...)]

    Low_Setpoint_Schedule_Name: Annotated[str, Field(default=...)]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which temperature will be set"""