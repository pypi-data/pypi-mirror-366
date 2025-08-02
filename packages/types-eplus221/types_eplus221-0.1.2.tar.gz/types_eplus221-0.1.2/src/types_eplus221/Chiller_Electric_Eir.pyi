from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chiller_Electric_Eir(EpBunch):
    """This chiller model is the empirical model from the DOE-2 building Energy"""

    Name: Annotated[str, Field(default=...)]

    Reference_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Reference_COP: Annotated[float, Field(default=..., gt=0.0)]
    """Efficiency of the chiller compressor (cooling output/compressor energy input)."""

    Reference_Leaving_Chilled_Water_Temperature: Annotated[float, Field(default=6.67)]

    Reference_Entering_Condenser_Fluid_Temperature: Annotated[float, Field(default=29.4)]

    Reference_Chilled_Water_Flow_Rate: Annotated[float, Field(gt=0)]

    Reference_Condenser_Fluid_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """This field is only used for Condenser Type = AirCooled or EvaporativelyCooled"""

    Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Cooling capacity as a function of CW supply temp and entering condenser temp"""

    Electric_Input_to_Cooling_Output_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) as a function of temperature"""

    Electric_Input_to_Cooling_Output_Ratio_Function_of_Part_Load_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """Electric Input Ratio (EIR) as a function of Part Load Ratio (PLR)"""

    Minimum_Part_Load_Ratio: Annotated[float, Field(ge=0.0, default=0.1)]
    """Part load ratio below which the chiller starts cycling on/off to meet the load."""

    Maximum_Part_Load_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Maximum allowable part load ratio. Must be greater than or equal to Minimum Part Load Ratio."""

    Optimum_Part_Load_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Optimum part load ratio where the chiller is most efficient."""

    Minimum_Unloading_Ratio: Annotated[float, Field(ge=0.0, default=0.2)]
    """Part load ratio where the chiller can no longer unload and false loading begins."""

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field()]
    """Not required if air-cooled or evaporatively-cooled"""

    Condenser_Outlet_Node_Name: Annotated[str, Field()]
    """Not required if air-cooled or evaporatively-cooled"""

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled', 'EvaporativelyCooled'], Field(default='WaterCooled')]

    Condenser_Fan_Power_Ratio: Annotated[float, Field(ge=0.0, default=0.0)]
    """Use for air-cooled or evaporatively-cooled condensers."""

    Fraction_of_Compressor_Electric_Consumption_Rejected_by_Condenser: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]
    """Fraction of compressor electrical energy that must be rejected by the condenser."""

    Leaving_Chilled_Water_Lower_Temperature_Limit: Annotated[float, Field(default=2.0)]

    Chiller_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the chiller. "NotModulated" is for"""

    Design_Heat_Recovery_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """If non-zero, then the heat recovery inlet and outlet node names must be entered."""

    Heat_Recovery_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Outlet_Node_Name: Annotated[str, Field()]

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Condenser_Heat_Recovery_Relative_Capacity_Fraction: Annotated[float, Field(ge=0.0, le=1.0)]
    """This optional field is the fraction of total rejected heat that can be recovered at full load"""

    Heat_Recovery_Inlet_High_Temperature_Limit_Schedule_Name: Annotated[str, Field()]
    """This optional schedule of temperatures will turn off heat recovery if inlet exceeds the value"""

    Heat_Recovery_Leaving_Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """This optional field provides control over the heat recovery"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""