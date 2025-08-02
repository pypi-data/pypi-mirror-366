from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Humidifier_Steam_Electric(EpBunch):
    """Electrically heated steam humidifier with fan."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Rated_Capacity: Annotated[float, Field(ge=0.0)]
    """Capacity is m3/s of water at 5.05 C"""

    Rated_Power: Annotated[float, Field(ge=0.0)]
    """if autosized the rated power is calculated from the rated capacity"""

    Rated_Fan_Power: Annotated[float, Field(ge=0.0)]

    Standby_Power: Annotated[float, Field(ge=0.0)]

    Air_Inlet_Node_Name: Annotated[str, Field()]

    Air_Outlet_Node_Name: Annotated[str, Field()]

    Water_Storage_Tank_Name: Annotated[str, Field()]