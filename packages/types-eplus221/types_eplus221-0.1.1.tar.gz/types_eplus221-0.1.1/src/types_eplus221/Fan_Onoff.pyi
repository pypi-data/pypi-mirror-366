from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fan_Onoff(EpBunch):
    """Constant volume fan that is intended to cycle on and off based on cooling/heating load"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Fan_Total_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.6)]

    Pressure_Rise: Annotated[str, Field(default=...)]

    Maximum_Flow_Rate: Annotated[str, Field()]

    Motor_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.8)]

    Motor_In_Airstream_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """0.0 means fan motor outside of air stream, 1.0 means motor inside of air stream"""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Fan_Power_Ratio_Function_Of_Speed_Ratio_Curve_Name: Annotated[str, Field()]

    Fan_Efficiency_Ratio_Function_Of_Speed_Ratio_Curve_Name: Annotated[str, Field()]

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""