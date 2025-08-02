from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fan_Systemmodel(EpBunch):
    """Versatile simple fan that can be used in variable air volume, constant volume, on-off cycling, two-speed or multi-speed applications."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this fan. Schedule value > 0 means the fan is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Design_Maximum_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Speed_Control_Method: Annotated[Literal['Continuous', 'Discrete'], Field(default='Discrete')]

    Electric_Power_Minimum_Flow_Rate_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    Design_Pressure_Rise: Annotated[float, Field(default=..., gt=0.0)]

    Motor_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.9)]

    Motor_In_Air_Stream_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """0.0 means fan motor outside of air stream, 1.0 means motor inside of air stream"""

    Design_Electric_Power_Consumption: Annotated[float, Field()]
    """Fan power consumption at maximum air flow rate."""

    Design_Power_Sizing_Method: Annotated[Literal['PowerPerFlow', 'PowerPerFlowPerPressure', 'TotalEfficiencyAndPressure'], Field(default='PowerPerFlowPerPressure')]

    Electric_Power_Per_Unit_Flow_Rate: Annotated[float, Field()]

    Electric_Power_Per_Unit_Flow_Rate_Per_Unit_Pressure: Annotated[float, Field(default=1.66667)]

    Fan_Total_Efficiency: Annotated[float, Field(gt=0.0, le=1.0, default=0.7)]

    Electric_Power_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """independent variable is normalized flow rate, current flow divided by Design Maximum Air Flow Rate."""

    Night_Ventilation_Mode_Pressure_Rise: Annotated[float, Field()]
    """Total system fan pressure rise at the fan when in night mode using AvailabilityManager:NightVentilation"""

    Night_Ventilation_Mode_Flow_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """Fraction of Design Maximum Air Flow Rate to use when in night mode using AvailabilityManager:NightVentilation"""

    Motor_Loss_Zone_Name: Annotated[str, Field()]
    """optional, if used fan motor heat losses that not added to air stream are transferred to zone as internal gains"""

    Motor_Loss_Radiative_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """optional. If zone identified in previous field then this determines"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Number_of_Speeds: Annotated[int, Field(default=1)]
    """number of different speed levels available when Speed Control Method is set to Discrete"""

    Speed_1_Flow_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Speed_1_Electric_Power_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """if left blank then use Electric Power Function of Flow Fraction Curve"""

    Speed_2_Flow_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Speed_2_Electric_Power_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Speed_3_Flow_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Speed_3_Electric_Power_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Speed_n_Flow_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]

    Speed_n_Electric_Power_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]