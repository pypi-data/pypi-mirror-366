from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Watertoairheatpump_Variablespeedequationfit(EpBunch):
    """Direct expansion (DX) heating coil for water-to-air heat pump (includes electric"""

    Name: Annotated[str, Field(default=...)]

    Water_To_Refrigerant_Hx_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Water_To_Refrigerant_Hx_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Indoor_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Indoor_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Number_Of_Speeds: Annotated[int, Field(ge=1, le=10, default=2)]

    Nominal_Speed_Level: Annotated[int, Field(default=2)]
    """must be lower than or equal to the highest speed number"""

    Rated_Heating_Capacity_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]

    Rated_Air_Flow_Rate_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]

    Rated_Water_Flow_Rate_At_Selected_Nominal_Speed_Level: Annotated[float, Field(default=autosize)]

    Energy_Part_Load_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_1_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_1_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Rated_Air_Flow: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*db + c*db**2 + d*ewt + e*ewt**2 + f*db*ewt"""

    Speed_1_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_1_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffw + c*ffw**2"""

    Speed_1_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*db + c*db**2 + d*ewt + e*ewt**2 + f*db*ewt"""

    Speed_1_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_1_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ffw + c*ffw**2"""

    Speed_1_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(default=..., ge=0)]

    Speed_1_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*db + c*db**2 + d*ewt + e*ewt**2 + f*db*ewt"""

    Speed_2_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_2_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_2_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*ewt + e*ewt**2 + f*db*ewt"""

    Speed_2_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_2_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffw + c*ffw**2"""

    Speed_2_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*ewt + e*ewt**2 + f*db*ewt"""

    Speed_2_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ffa + c*ffa**2"""

    Speed_2_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_2_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_2_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*db + c*db**2 + d*ewt + e*ewt**2 + f*db*ewt"""

    Speed_3_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_3_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_3_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_3_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_3_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_3_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_3_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_3_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_3_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_3_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_4_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_4_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_4_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_4_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_5_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_5_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_5_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_5_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_6_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_6_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_6_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_6_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_7_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_7_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_7_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_7_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_8_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_8_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_8_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_8_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_9_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_9_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_9_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_9_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_9_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Reference_Unit_Gross_Rated_Heating_Capacity: Annotated[float, Field(ge=0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_10_Reference_Unit_Gross_Rated_Heating_Cop: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Rated_Air_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_10_Reference_Unit_Rated_Water_Flow_Rate: Annotated[float, Field(ge=0)]

    Speed_10_Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Total_Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Energy_Input_Ratio_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Energy_Input_Ratio_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """optional"""

    Speed_10_Reference_Unit_Waste_Heat_Fraction_Of_Input_Power_At_Rated_Conditions: Annotated[float, Field(ge=0)]

    Speed_10_Waste_Heat_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """optional"""