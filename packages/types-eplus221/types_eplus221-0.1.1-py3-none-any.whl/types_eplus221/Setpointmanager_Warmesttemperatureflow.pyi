from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Warmesttemperatureflow(EpBunch):
    """This setpoint manager sets both the supply air temperature"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field()]

    Hvac_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object."""

    Minimum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=12.)]

    Maximum_Setpoint_Temperature: Annotated[float, Field(gt=0.0, default=18.)]

    Strategy: Annotated[Literal['TemperatureFirst', 'FlowFirst'], Field(default='TemperatureFirst')]
    """For TemperatureFirst the manager tries to find the highest setpoint temperature"""

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""

    Minimum_Turndown_Ratio: Annotated[float, Field(gt=0.0, default=0.2)]
    """Fraction of the maximum supply air flow rate."""