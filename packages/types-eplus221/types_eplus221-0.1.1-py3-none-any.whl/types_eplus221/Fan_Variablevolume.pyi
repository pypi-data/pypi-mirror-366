from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fan_Variablevolume(EpBunch):
    """Variable air volume fan where the electric power input varies according to a"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Fan_Total_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.7)]

    Pressure_Rise: Annotated[str, Field(default=...)]

    Maximum_Flow_Rate: Annotated[str, Field()]

    Fan_Power_Minimum_Flow_Rate_Input_Method: Annotated[Literal['Fraction', 'FixedFlowRate'], Field(default='Fraction')]

    Fan_Power_Minimum_Flow_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0.25)]

    Fan_Power_Minimum_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]

    Motor_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.9)]

    Motor_In_Airstream_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """0.0 means fan motor outside of air stream, 1.0 means motor inside of air stream"""

    Fan_Power_Coefficient_1: Annotated[str, Field()]
    """all Fan Power Coefficients should not be 0.0 or no fan power will be consumed."""

    Fan_Power_Coefficient_2: Annotated[str, Field()]

    Fan_Power_Coefficient_3: Annotated[str, Field()]

    Fan_Power_Coefficient_4: Annotated[str, Field()]

    Fan_Power_Coefficient_5: Annotated[str, Field()]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""