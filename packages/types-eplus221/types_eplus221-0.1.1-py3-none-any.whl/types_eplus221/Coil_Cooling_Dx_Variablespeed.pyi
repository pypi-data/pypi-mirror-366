from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Variablespeed(EpBunch):
    """Direct expansion (DX) cooling coil and condensing unit (includes electric compressor"""

    Name: Annotated[str, Field(default=...)]

    Indoor_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Indoor_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Number_Of_Speeds: Annotated[int, Field(ge=1, le=10, default=2)]

    Nominal_Speed_Level: Annotated[int, Field(default=2)]
    """must be lower than or equal to the highest speed number"""

    Gross_Rated_Total_Cooling_Capacity_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Rated_Air_Flow_Rate_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]

    Nominal_Time_For_Condensate_To_Begin_Leaving_The_Coil: Annotated[float, Field(ge=0, default=0)]

    Initial_Moisture_Evaporation_Rate_Divided_By_Steady_State_Ac_Latent_Capacity: Annotated[float, Field(ge=0, default=0)]

    Energy_Part_Load_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Condenser_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node. This node name is also specified in"""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0, default=0.0)]
    """Rated power consumed by the evaporative condenser's water pump"""

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Minimum_Outdoor_Dry_Bulb_Temperature_For_Compressor_Operation: Annotated[float, Field(default=-25.0)]

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Speed_1_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_1_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0, le=1.0)]

    Speed_1_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Rated_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """This field is only used for Condenser Type = EvaporativelyCooled"""

    Speed_1_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled"""

    Speed_1_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_1_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_1_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_1_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_2_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_2_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_2_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_2_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_2_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_2_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_2_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_3_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_3_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_3_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_3_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_3_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_3_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_3_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_4_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_4_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_4_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_4_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_4_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_4_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_4_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_5_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_5_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_5_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_5_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_5_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_5_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_5_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_6_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_6_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_6_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_6_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_6_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_6_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_6_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_7_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_7_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_7_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Condenser_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_7_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_7_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_7_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_7_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_8_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_8_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_8_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]

    Speed_8_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_8_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_8_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_8_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_9_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_9_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_9_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """optional"""

    Speed_9_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]
    """optional"""

    Speed_9_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_9_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_9_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_9_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_10_Reference_Unit_Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(ge=0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Speed_10_Reference_Unit_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0, le=1.0)]

    Speed_10_Reference_Unit_Gross_Rated_Cooling_Cop: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Condenser_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """optional"""

    Speed_10_Reference_Unit_Rated_Pad_Effectiveness_Of_Evap_Precooling: Annotated[float, Field(ge=0, le=1.0)]
    """optional"""

    Speed_10_Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_10_Total_Cooling_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*odb + e*odb**2 + f*wb*odb"""

    Speed_10_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""