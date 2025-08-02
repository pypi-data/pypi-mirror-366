from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Dx_Multispeed(EpBunch):
    """Direct expansion (DX) heating coil (air-to-air heat pump) and compressor unit"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Minimum_Outdoor_DryBulb_Temperature_for_Compressor_Operation: Annotated[float, Field(default=-8.0)]

    Outdoor_DryBulb_Temperature_to_Turn_On_Compressor: Annotated[float, Field()]
    """The outdoor temperature when the compressor is automatically turned back on following an"""

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_DryBulb_Temperature_for_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Defrost_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """biquadratic curve = a + b*wb + c*wb**2 + d*oat + e*oat**2 + f*wb*oat"""

    Maximum_Outdoor_DryBulb_Temperature_for_Defrost_Operation: Annotated[float, Field(ge=0.0, le=7.22, default=5.0)]

    Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='ReverseCycle')]

    Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]

    Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode"""

    Resistive_Defrost_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """only applicable if resistive defrost strategy is specified"""

    Apply_Part_Load_Fraction_to_Speeds_Greater_than_1: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'Propane', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default=...)]

    Region_number_for_Calculating_HSPF: Annotated[int, Field(ge=1, le=6, default=4)]
    """Standard Region number for which HSPF and other standard ratings are calculated"""

    Number_of_Speeds: Annotated[int, Field(default=..., ge=2, le=4)]
    """Enter the number of the following sets of data for coil capacity, COP,"""

    Speed_1_Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_1_Gross_Rated_Heating_COP: Annotated[float, Field(default=..., gt=0.0)]
    """Rated heating capacity divided by power input to the compressor and outdoor fan,"""

    Speed_1_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total capacity"""

    Speed_1_Rated_Supply_Air_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the supply air fan power per air volume flow rate at the rated speed 1 test conditions."""

    Speed_1_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_1_Heating_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_1_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_1_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_1_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_1_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """recoverable waste heat at full load and rated conditions"""

    Speed_1_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_2_Gross_Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_2_Gross_Rated_Heating_COP: Annotated[float, Field(default=..., gt=0.0)]
    """Rated heating capacity divided by power input to the compressor and outdoor fan,"""

    Speed_2_Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total capacity"""

    Speed_2_Rated_Supply_Air_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the supply air fan power per air volume flow rate at the rated speed 2 test conditions."""

    Speed_2_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_2_Heating_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_2_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_2_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_2_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_2_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """recoverable waste heat at full load and rated conditions"""

    Speed_2_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_3_Gross_Rated_Heating_Capacity: Annotated[float, Field(gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_3_Gross_Rated_Heating_COP: Annotated[float, Field(gt=0.0)]
    """Rated heating capacity divided by power input to the compressor and outdoor fan,"""

    Speed_3_Rated_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Flow rate corresponding to rated total capacity"""

    Speed_3_Rated_Supply_Air_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the supply air fan power per air volume flow rate at the rated speed 3 test conditions."""

    Speed_3_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_3_Heating_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_3_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_3_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_3_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_3_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """recoverable waste heat at full load and rated conditions"""

    Speed_3_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Speed_4_Gross_Rated_Heating_Capacity: Annotated[float, Field(gt=0.0)]
    """Heating capacity not accounting for the effect of supply air fan heat"""

    Speed_4_Gross_Rated_Heating_COP: Annotated[float, Field(gt=0.0)]
    """Rated heating capacity divided by power input to the compressor and outdoor fan,"""

    Speed_4_Rated_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Flow rate corresponding to rated total capacity"""

    Speed_4_Rated_Supply_Air_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the supply air fan power per air volume flow rate at the rated speed 4 test conditions."""

    Speed_4_Heating_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_4_Heating_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_4_Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*oat + c*oat**2"""

    Speed_4_Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_4_Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Speed_4_Rated_Waste_Heat_Fraction_of_Power_Input: Annotated[float, Field(gt=0.0, le=1.0, default=0.2)]
    """recoverable waste heat at full load and rated conditions"""

    Speed_4_Waste_Heat_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*odb + c*odb**2 + d*db + e*db**2 + f*odb*db"""

    Zone_Name_for_Evaporator_Placement: Annotated[str, Field()]
    """This input field is name of a conditioned or unconditioned zone where the secondary"""

    Speed_1_Secondary_Coil_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """This input value is the secondary coil (evaporator) air flow rate when the heat pump"""

    Speed_1_Secondary_Coil_Fan_Flow_Scaling_Factor: Annotated[float, Field(gt=0.0, default=1.25)]
    """This input field is scaling factor for autosizing the secondary DX coil fan flow rate."""

    Speed_1_Nominal_Sensible_Heat_Ratio_of_Secondary_Coil: Annotated[float, Field(gt=0.0, le=1.0)]
    """This input value is the nominal sensible heat ratio used to split the heat extracted by"""

    Speed_1_Sensible_Heat_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Speed_1_Sensible_Heat_Ratio_Modifier_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_2_Secondary_Coil_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """This input value is the secondary coil (evaporator) air flow rate when the heat pump"""

    Speed_2_Secondary_Coil_Fan_Flow_Scaling_Factor: Annotated[float, Field(gt=0.0, default=1.25)]
    """This input field is scaling factor for autosizing the secondary DX coil fan flow rate."""

    Speed_2_Nominal_Sensible_Heat_Ratio_of_Secondary_Coil: Annotated[float, Field(gt=0.0, le=1.0)]
    """This input value is the nominal sensible heat ratio used to split the heat extracted by"""

    Speed_2_Sensible_Heat_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Speed_2_Sensible_Heat_Ratio_Modifier_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_3_Secondary_Coil_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """This input value is the secondary coil (evaporator) air flow rate when the heat pump"""

    Speed_3_Secondary_Coil_Fan_Flow_Scaling_Factor: Annotated[float, Field(gt=0.0, default=1.25)]
    """This input field is scaling factor for autosizing the secondary DX coil fan flow rate."""

    Speed_3_Nominal_Sensible_Heat_Ratio_of_Secondary_Coil: Annotated[float, Field(gt=0.0, le=1.0)]
    """This input value is the nominal sensible heat ratio used to split the heat extracted by"""

    Speed_3_Sensible_Heat_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Speed_3_Sensible_Heat_Ratio_Modifier_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Speed_4_Secondary_Coil_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """This input value is the secondary coil (evaporator) air flow rate when the heat pump"""

    Speed_4_Secondary_Coil_Fan_Flow_Scaling_Factor: Annotated[float, Field(gt=0.0, default=1.25)]
    """This input field is scaling factor for autosizing the secondary DX coil fan flow rate."""

    Speed_4_Nominal_Sensible_Heat_Ratio_of_Secondary_Coil: Annotated[float, Field(gt=0.0, le=1.0)]
    """This input value is the nominal sensible heat ratio used to split the heat extracted by"""

    Speed_4_Sensible_Heat_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Speed_4_Sensible_Heat_Ratio_Modifier_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""