from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Steam(EpBunch):
    """Steam heating coil. Condenses and sub-cools steam at loop pressure and discharges"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Steam_Flow_Rate: Annotated[str, Field()]

    Degree_Of_Subcooling: Annotated[str, Field()]

    Degree_Of_Loop_Subcooling: Annotated[str, Field(default='20.0')]

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Coil_Control_Type: Annotated[Literal['TemperatureSetpointControl', 'ZoneLoadControl'], Field()]
    """Use ZoneLoadControl if the coil is contained within another component such as an air"""

    Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """Required if Coil Control Type is TemperatureSetpointControl"""