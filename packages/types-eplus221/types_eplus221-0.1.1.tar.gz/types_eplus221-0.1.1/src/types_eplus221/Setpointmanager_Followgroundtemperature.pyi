from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Followgroundtemperature(EpBunch):
    """This setpoint manager is used to place a temperature setpoint on a"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'MinimumTemperature', 'MaximumTemperature'], Field(default='Temperature')]

    Reference_Ground_Temperature_Object_Type: Annotated[Literal['Site:GroundTemperature:BuildingSurface', 'Site:GroundTemperature:Shallow', 'Site:GroundTemperature:Deep', 'Site:GroundTemperature:FCfactorMethod'], Field()]

    Offset_Temperature_Difference: Annotated[float, Field()]

    Maximum_Setpoint_Temperature: Annotated[float, Field()]

    Minimum_Setpoint_Temperature: Annotated[float, Field()]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which control variable will be set"""