from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Scheduled(EpBunch):
    """The simplest Setpoint Manager simply uses a schedule to determine one"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'MaximumTemperature', 'MinimumTemperature', 'HumidityRatio', 'MaximumHumidityRatio', 'MinimumHumidityRatio', 'MassFlowRate', 'MaximumMassFlowRate', 'MinimumMassFlowRate'], Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which control variable will be set"""