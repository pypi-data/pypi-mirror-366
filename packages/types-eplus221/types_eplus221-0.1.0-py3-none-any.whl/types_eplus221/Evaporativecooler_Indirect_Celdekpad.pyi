from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Evaporativecooler_Indirect_Celdekpad(EpBunch):
    """Indirect evaporative cooler with rigid media evaporative pad, recirculating water"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Direct_Pad_Area: Annotated[float, Field(ge=0.0, default=autosize)]

    Direct_Pad_Depth: Annotated[float, Field(ge=0.0, default=autosize)]

    Recirculating_Water_Pump_Power_Consumption: Annotated[float, Field(default=...)]

    Secondary_Air_Fan_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Secondary_Air_Fan_Total_Efficiency: Annotated[float, Field(gt=0.0, le=1.0)]

    Secondary_Air_Fan_Delta_Pressure: Annotated[float, Field(default=..., ge=0.0)]

    Indirect_Heat_Exchanger_Effectiveness: Annotated[float, Field(default=..., ge=0.0)]

    Primary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Primary_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Control_Type: Annotated[str, Field()]
    """This field is not currently used and can be left blank"""

    Water_Supply_Storage_Tank_Name: Annotated[str, Field()]

    Secondary_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node"""