from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonethermalchimney(EpBunch):
    """A thermal chimney is a vertical shaft utilizing solar radiation to enhance natural"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of zone that is the thermal chimney"""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Width_Of_The_Absorber_Wall: Annotated[float, Field(default=..., ge=0)]

    Cross_Sectional_Area_Of_Air_Channel_Outlet: Annotated[float, Field(default=..., ge=0)]

    Discharge_Coefficient: Annotated[float, Field(ge=0, le=1, default=0.8)]

    Zone_1_Name: Annotated[str, Field(default=...)]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_1: Annotated[float, Field(default=..., ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_1: Annotated[float, Field(ge=0, le=1, default=1.0)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_1: Annotated[float, Field(default=..., ge=0)]

    Zone_2_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_2: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_2: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_2: Annotated[float, Field(ge=0)]

    Zone_3_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_3: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_3: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_3: Annotated[float, Field(ge=0)]

    Zone_4_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_4: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_4: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_4: Annotated[float, Field(ge=0)]

    Zone_5_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_5: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_5: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_5: Annotated[float, Field(ge=0)]

    Zone_6_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_6: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_6: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_6: Annotated[float, Field(ge=0)]

    Zone_7_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_7: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_7: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_7: Annotated[float, Field(ge=0)]

    Zone_8_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_8: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_8: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_8: Annotated[float, Field(ge=0)]

    Zone_9_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_9: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_9: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_9: Annotated[float, Field(ge=0)]

    Zone_10_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_10: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_10: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_10: Annotated[float, Field(ge=0)]

    Zone_11_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_11: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_11: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_11: Annotated[float, Field(ge=0)]

    Zone_12_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_12: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_12: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_12: Annotated[float, Field(ge=0)]

    Zone_13_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_13: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_13: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_13: Annotated[float, Field(ge=0)]

    Zone_14_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_14: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_14: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_14: Annotated[float, Field(ge=0)]

    Zone_15_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_15: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_15: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_15: Annotated[float, Field(ge=0)]

    Zone_16_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_16: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_16: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_16: Annotated[float, Field(ge=0)]

    Zone_17_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_17: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_17: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_17: Annotated[float, Field(ge=0)]

    Zone_18_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_18: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_18: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_18: Annotated[float, Field(ge=0)]

    Zone_19_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_19: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_19: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_19: Annotated[float, Field(ge=0)]

    Zone_20_Name: Annotated[str, Field()]

    Distance_From_Top_Of_Thermal_Chimney_To_Inlet_20: Annotated[float, Field(ge=0)]

    Relative_Ratios_Of_Air_Flow_Rates_Passing_Through_Zone_20: Annotated[float, Field(ge=0, le=1)]

    Cross_Sectional_Areas_Of_Air_Channel_Inlet_20: Annotated[float, Field(ge=0)]