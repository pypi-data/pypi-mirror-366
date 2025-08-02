from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Electric(EpBunch):
    """Electric heating coil. If the coil is located directly in an air loop branch or"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Efficiency: Annotated[str, Field(default='1.0')]

    Nominal_Capacity: Annotated[str, Field()]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """Required if coil is temperature controlled."""