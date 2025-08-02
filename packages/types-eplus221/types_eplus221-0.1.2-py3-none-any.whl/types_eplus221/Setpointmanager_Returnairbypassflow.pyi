from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Returnairbypassflow(EpBunch):
    """This setpoint manager determines the required"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Flow'], Field(default='Flow')]

    HVAC_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object."""

    Temperature_Setpoint_Schedule_Name: Annotated[str, Field()]