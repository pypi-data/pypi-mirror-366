from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Followoutdoorairtemperature(EpBunch):
    """This setpoint manager is used to place a temperature setpoint on a system node"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'MinimumTemperature', 'MaximumTemperature'], Field(default='Temperature')]

    Reference_Temperature_Type: Annotated[Literal['OutdoorAirWetBulb', 'OutdoorAirDryBulb'], Field(default='OutdoorAirWetBulb')]

    Offset_Temperature_Difference: Annotated[float, Field()]

    Maximum_Setpoint_Temperature: Annotated[float, Field()]

    Minimum_Setpoint_Temperature: Annotated[float, Field()]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which control variable will be set"""