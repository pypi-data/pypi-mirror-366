from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Followsystemnodetemperature(EpBunch):
    """This setpoint manager is used to place a temperature setpoint on a"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'MinimumTemperature', 'MaximumTemperature'], Field(default='Temperature')]

    Reference_Node_Name: Annotated[str, Field()]

    Reference_Temperature_Type: Annotated[Literal['NodeWetBulb', 'NodeDryBulb'], Field(default='NodeDryBulb')]

    Offset_Temperature_Difference: Annotated[float, Field()]

    Maximum_Limit_Setpoint_Temperature: Annotated[float, Field()]

    Minimum_Limit_Setpoint_Temperature: Annotated[float, Field()]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which control variable will be set"""