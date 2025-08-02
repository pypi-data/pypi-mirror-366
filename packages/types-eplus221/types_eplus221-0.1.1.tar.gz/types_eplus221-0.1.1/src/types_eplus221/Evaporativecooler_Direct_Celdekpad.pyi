from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Evaporativecooler_Direct_Celdekpad(EpBunch):
    """Direct evaporative cooler with rigid media evaporative pad and recirculating water"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Direct_Pad_Area: Annotated[str, Field(default='autosize')]

    Direct_Pad_Depth: Annotated[str, Field(default='autosize')]

    Recirculating_Water_Pump_Power_Consumption: Annotated[str, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Control_Type: Annotated[str, Field()]
    """This field is not currently used and can be left blank"""

    Water_Supply_Storage_Tank_Name: Annotated[str, Field()]