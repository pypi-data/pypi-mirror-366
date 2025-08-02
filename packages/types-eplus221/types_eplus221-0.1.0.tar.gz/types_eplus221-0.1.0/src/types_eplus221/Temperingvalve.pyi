from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Temperingvalve(EpBunch):
    """Temperature-controlled diversion valve used to divert flow around one or more plant"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of a Node"""

    Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of a Node"""

    Stream_2_Source_Node_Name: Annotated[str, Field(default=...)]
    """Name of a Node"""

    Temperature_Setpoint_Node_Name: Annotated[str, Field(default=...)]
    """Name of a Node"""

    Pump_Outlet_Node_Name: Annotated[str, Field(default=...)]