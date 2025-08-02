from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Outdoorairreset(EpBunch):
    """This Setpoint Manager is used to place a setpoint temperature on system node"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'MaximumTemperature', 'MinimumTemperature'], Field(default='Temperature')]

    Setpoint_At_Outdoor_Low_Temperature: Annotated[str, Field(default=...)]

    Outdoor_Low_Temperature: Annotated[str, Field(default=...)]

    Setpoint_At_Outdoor_High_Temperature: Annotated[str, Field(default=...)]

    Outdoor_High_Temperature: Annotated[str, Field(default=...)]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which temperature will be set"""

    Schedule_Name: Annotated[str, Field()]
    """Optional input."""

    Setpoint_At_Outdoor_Low_Temperature_2: Annotated[str, Field()]
    """2nd outdoor air temperature reset rule"""

    Outdoor_Low_Temperature_2: Annotated[str, Field()]
    """2nd outdoor air temperature reset rule"""

    Setpoint_At_Outdoor_High_Temperature_2: Annotated[str, Field()]
    """2nd outdoor air temperature reset rule"""

    Outdoor_High_Temperature_2: Annotated[str, Field()]
    """2nd outdoor air temperature reset rule"""