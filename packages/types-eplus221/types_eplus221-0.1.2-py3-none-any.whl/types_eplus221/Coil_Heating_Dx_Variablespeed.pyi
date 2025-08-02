from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Dx_Variablespeed(EpBunch):
    """Direct expansion (DX) heating coil (air-to-air heat pump) and compressor unit"""

    Name: Annotated[str, Field(default=...)]

    Indoor_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Indoor_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Number_of_Speeds: Annotated[int, Field(ge=1, le=10, default=2)]

    Nominal_Speed_Level: Annotated[int, Field(default=2)]
    """must be lower than or equal to the highest speed number"""

    Rated_Heating_Capacity_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]

    Rated_Air_Flow_Rate_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]

    Energy_Part_Load_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Defrost_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """biquadratic curve = a + b*wb + c*wb**2 + d*oat + e*oat**2 + f*wb*oat"""

    Minimum_Outdoor_DryBulb_Temperature_for_Compressor_Operation: Annotated[float, Field(default=-8.0)]

    Outdoor_DryBulb_Temperature_to_Turn_On_Compressor: Annotated[float, Field()]
    """The outdoor temperature when the compressor is automatically turned back on following an"""

    Maximum_Outdoor_DryBulb_Temperature_for_Defrost_Operation: Annotated[float, Field(ge=0.0, le=7.22, default=5.0)]

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_DryBulb_Temperature_for_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='ReverseCycle')]

    Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]

    Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode"""

    Resistive_Defrost_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """only applicable if resistive defrost strategy is specified"""

    Speed_1_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_1_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_1_Total_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_1_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_1_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_2_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_2_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_2_Total_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_2_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_2_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_3_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_3_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_3_Total_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_3_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_3_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_4_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_4_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_4_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_4_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_4_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_5_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_5_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_5_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_5_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_5_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_6_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_6_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_6_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_6_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_6_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_7_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_7_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_7_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_7_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_7_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_8_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_8_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_8_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_8_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_8_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_9_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_9_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_9_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_9_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_9_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_9_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_10_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_10_Reference_Unit_Gross_Rated_Heating_COP: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_10_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_10_Heating_Capacity_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_10_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*oat + e*oat**2 + f*db*oat"""

    Speed_10_Energy_Input_Ratio_Function_of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""