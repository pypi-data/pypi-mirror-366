from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Singlezone_Heating(EpBunch):
    """This setpoint manager detects the control zone load to meet the current heating"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    Minimum_Supply_Air_Temperature: Annotated[str, Field(default='-99')]

    Maximum_Supply_Air_Temperature: Annotated[str, Field(default='99')]

    Control_Zone_Name: Annotated[str, Field(default=...)]

    Zone_Node_Name: Annotated[str, Field(default=...)]

    Zone_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""