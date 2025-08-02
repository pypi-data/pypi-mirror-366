from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Chiller_Electric(EpBunch):
    """This chiller model is the empirical model from the Building Loads"""

    Name: Annotated[str, Field(default=...)]

    Condenser_Type: Annotated[Literal['AirCooled', 'WaterCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Nominal_Capacity: Annotated[str, Field(default=...)]

    Nominal_COP: Annotated[str, Field(default=...)]

    Chilled_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Chilled_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Inlet_Node_Name: Annotated[str, Field()]

    Condenser_Outlet_Node_Name: Annotated[str, Field()]

    Minimum_Part_Load_Ratio: Annotated[str, Field()]

    Maximum_Part_Load_Ratio: Annotated[str, Field()]

    Optimum_Part_Load_Ratio: Annotated[str, Field()]

    Design_Condenser_Inlet_Temperature: Annotated[str, Field()]

    Temperature_Rise_Coefficient: Annotated[str, Field(default=...)]

    Design_Chilled_Water_Outlet_Temperature: Annotated[str, Field()]

    Design_Chilled_Water_Flow_Rate: Annotated[str, Field()]
    """For variable volume this is the maximum flow & for constant flow this is the flow."""

    Design_Condenser_Fluid_Flow_Rate: Annotated[str, Field()]
    """This field is only used for Condenser Type = AirCooled or EvaporativelyCooled"""

    Coefficient_1_of_Capacity_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_of_Capacity_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_of_Capacity_Ratio_Curve: Annotated[str, Field()]

    Coefficient_1_of_Power_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_of_Power_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_of_Power_Ratio_Curve: Annotated[str, Field()]

    Coefficient_1_of_Full_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_2_of_Full_Load_Ratio_Curve: Annotated[str, Field()]

    Coefficient_3_of_Full_Load_Ratio_Curve: Annotated[str, Field()]

    Chilled_Water_Outlet_Temperature_Lower_Limit: Annotated[str, Field()]

    Chiller_Flow_Mode: Annotated[Literal['ConstantFlow', 'LeavingSetpointModulated', 'NotModulated'], Field(default='NotModulated')]
    """Select operating mode for fluid flow through the chiller. "NotModulated" is for"""

    Design_Heat_Recovery_Water_Flow_Rate: Annotated[str, Field(default='0.0')]
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