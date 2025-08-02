from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Multizone_Maximumhumidity_Average(EpBunch):
    """This setpoint manager sets the average supply air maximum humidity ratio based on moisture"""

    Name: Annotated[str, Field(default=...)]

    HVAC_Air_Loop_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirLoopHVAC object"""

    Minimum_Setpoint_Humidity_Ratio: Annotated[float, Field(gt=0.0, default=0.008)]

    Maximum_Setpoint_Humidity_Ratio: Annotated[float, Field(gt=0.0, default=0.015)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the humidity ratio will be set"""