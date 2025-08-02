from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Controller_Watercoil(EpBunch):
    """Controller for a water coil which is located directly in an air loop branch or"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'HumidityRatio', 'TemperatureAndHumidityRatio'], Field(default=...)]
    """keys HumidityRatio or TemperatureAndHumidityRatio"""

    Action: Annotated[Literal['Normal', 'Reverse'], Field()]
    """Leave blank to have this automatically selected from coil type."""

    Actuator_Variable: Annotated[Literal['Flow'], Field(default=...)]

    Sensor_Node_Name: Annotated[str, Field(default=...)]

    Actuator_Node_Name: Annotated[str, Field(default=...)]

    Controller_Convergence_Tolerance: Annotated[float, Field(default=autosize)]

    Maximum_Actuated_Flow: Annotated[float, Field()]

    Minimum_Actuated_Flow: Annotated[float, Field(default=0.0000001)]