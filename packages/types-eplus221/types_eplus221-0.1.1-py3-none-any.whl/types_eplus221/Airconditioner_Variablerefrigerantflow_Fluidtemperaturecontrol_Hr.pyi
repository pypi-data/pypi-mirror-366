from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airconditioner_Variablerefrigerantflow_Fluidtemperaturecontrol_Hr(EpBunch):
    """This is a key object in the new physics based VRF Heat Recovery (HR) model applicable for Fluid"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this variable refrigerant flow heat pump"""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that defines the availability of the unit"""

    Zone_Terminal_Unit_List_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneTerminalUnitList. This list connects zone terminal units to this"""

    Refrigerant_Type: Annotated[str, Field(default='R410A')]

    Rated_Evaporative_Capacity: Annotated[float, Field(gt=0.0, default=40000)]
    """Enter the total evaporative capacity in watts at rated conditions"""

    Rated_Compressor_Power_Per_Unit_Of_Rated_Evaporative_Capacity: Annotated[float, Field(gt=0.0, default=0.35)]
    """Enter the rated compressor power per Watt of rated evaporative capacity [W/W]"""

    Minimum_Outdoor_Air_Temperature_In_Cooling_Only_Mode: Annotated[float, Field(default=-6.0)]
    """Enter the minimum outdoor temperature allowed for cooling operation"""

    Maximum_Outdoor_Air_Temperature_In_Cooling_Only_Mode: Annotated[float, Field(default=43.0)]
    """Enter the maximum outdoor temperature allowed for cooling operation"""

    Minimum_Outdoor_Air_Temperature_In_Heating_Only_Mode: Annotated[float, Field(default=-20.0)]
    """Enter the minimum outdoor temperature allowed for heating operation"""

    Maximum_Outdoor_Air_Temperature_In_Heating_Only_Mode: Annotated[float, Field(default=16.0)]
    """Enter the maximum outdoor temperature allowed for heating operation"""

    Minimum_Outdoor_Temperature_In_Heat_Recovery_Mode: Annotated[float, Field(default=-20.0)]
    """The minimum outdoor temperature below which heat"""

    Maximum_Outdoor_Temperature_In_Heat_Recovery_Mode: Annotated[float, Field(default=43.0)]
    """The maximum outdoor temperature above which heat"""

    Refrigerant_Temperature_Control_Algorithm_For_Indoor_Unit: Annotated[Literal['ConstantTemp', 'VariableTemp'], Field(default='VariableTemp')]

    Reference_Evaporating_Temperature_For_Indoor_Unit: Annotated[float, Field(default=6.0)]
    """This field is used if Refrigerant Temperature Control Algorithm"""

    Reference_Condensing_Temperature_For_Indoor_Unit: Annotated[float, Field(default=44.0)]
    """This field is used if Refrigerant Temperature Control Algorithm"""

    Variable_Evaporating_Temperature_Minimum_For_Indoor_Unit: Annotated[float, Field(default=4.0)]
    """This field is used if Refrigerant Temperature Control Algorithm"""

    Variable_Evaporating_Temperature_Maximum_For_Indoor_Unit: Annotated[float, Field(default=13.0)]
    """This field is used if Refrigerant Temperature Control Algorithm"""

    Variable_Condensing_Temperature_Minimum_For_Indoor_Unit: Annotated[float, Field(default=42.0)]
    """This field is used if Refrigerant Temperature Control Algorithm"""

    Variable_Condensing_Temperature_Maximum_For_Indoor_Unit: Annotated[float, Field(default=46.0)]
    """This field is used if Refrigerant Temperature Control Algorithm"""

    Outdoor_Unit_Evaporator_Reference_Superheating: Annotated[float, Field(default=3)]

    Outdoor_Unit_Condenser_Reference_Subcooling: Annotated[float, Field(default=5)]

    Outdoor_Unit_Evaporator_Rated_Bypass_Factor: Annotated[float, Field(gt=0, default=0.4)]

    Outdoor_Unit_Condenser_Rated_Bypass_Factor: Annotated[float, Field(gt=0, default=0.2)]

    Difference_Between_Outdoor_Unit_Evaporating_Temperature_And_Outdoor_Air_Temperature_In_Heat_Recovery_Mode: Annotated[float, Field(default=5)]

    Outdoor_Unit_Heat_Exchanger_Capacity_Ratio: Annotated[float, Field(gt=0, default=0.3)]
    """Enter the rated capacity ratio between the main and supplementary outdoor unit heat exchangers [W/W]"""

    Outdoor_Unit_Fan_Power_Per_Unit_Of_Rated_Evaporative_Capacity: Annotated[float, Field(gt=0.0, default=4.25E-3)]
    """Enter the outdoor unit fan power per Watt of rated evaporative capacity [W/W]"""

    Outdoor_Unit_Fan_Flow_Rate_Per_Unit_Of_Rated_Evaporative_Capacity: Annotated[float, Field(gt=0.0, default=7.50E-5)]
    """Enter the outdoor unit fan flow rate per Watt of rated evaporative capacity [W/W]"""

    Outdoor_Unit_Evaporating_Temperature_Function_Of_Superheating_Curve_Name: Annotated[str, Field(default=...)]

    Outdoor_Unit_Condensing_Temperature_Function_Of_Subcooling_Curve_Name: Annotated[str, Field(default=...)]

    Diameter_Of_Main_Pipe_For_Suction_Gas: Annotated[float, Field(ge=0.0, default=0.0762)]
    """used to calculate the piping loss"""

    Diameter_Of_Main_Pipe_For_Discharge_Gas: Annotated[float, Field(ge=0.0, default=0.0762)]
    """used to calculate the piping loss"""

    Length_Of_Main_Pipe_Connecting_Outdoor_Unit_To_The_First_Branch_Joint: Annotated[float, Field(ge=0.0, default=30.0)]
    """used to calculate the heat loss of the main pipe"""

    Equivalent_Length_Of_Main_Pipe_Connecting_Outdoor_Unit_To_The_First_Branch_Joint: Annotated[float, Field(ge=0.0, default=36.0)]
    """used to calculate the refrigerant pressure drop of the main pipe"""

    Height_Difference_Between_Outdoor_Unit_And_Indoor_Units: Annotated[float, Field(default=5.0)]
    """Difference between outdoor unit height and indoor unit height"""

    Main_Pipe_Insulation_Thickness: Annotated[float, Field(ge=0.0, default=0.02)]

    Main_Pipe_Insulation_Thermal_Conductivity: Annotated[float, Field(ge=0.0, default=0.032)]

    Crankcase_Heater_Power_Per_Compressor: Annotated[float, Field(default=33.0)]
    """Enter the value of the resistive heater located in the compressor(s). This heater"""

    Number_Of_Compressors: Annotated[int, Field(default=2)]
    """Enter the total number of compressor. This input is used only for crankcase"""

    Ratio_Of_Compressor_Size_To_Total_Compressor_Capacity: Annotated[float, Field(default=0.5)]
    """Enter the ratio of the first stage compressor to total compressor capacity"""

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Crankcase_Heater: Annotated[float, Field(default=5.0)]
    """Enter the maximum outdoor temperature above which the crankcase heaters are disabled"""

    Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='Resistive')]
    """Select a defrost strategy."""

    Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]
    """Choose a defrost control type"""

    Defrost_Energy_Input_Ratio_Modifier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """A valid performance curve must be used if ReverseCycle defrost strategy is selected"""

    Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode"""

    Resistive_Defrost_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """Enter the size of the resistive defrost heating element"""

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Defrost_Operation: Annotated[float, Field(default=5.0)]
    """Enter the maximum outdoor temperature above which the defrost operation is disabled"""

    Initial_Heat_Recovery_Cooling_Capacity_Fraction: Annotated[float, Field(default=1)]
    """This is used to describe the transition from Cooling Only mode to Heat Recovery mode"""

    Heat_Recovery_Cooling_Capacity_Time_Constant: Annotated[float, Field(default=0)]
    """This is used to describe the transition from Cooling Only mode to Heat Recovery mode"""

    Initial_Heat_Recovery_Cooling_Energy_Fraction: Annotated[float, Field(default=1)]
    """This is used to describe the transition from Cooling Only mode to Heat Recovery mode"""

    Heat_Recovery_Cooling_Energy_Time_Constant: Annotated[float, Field(default=0)]
    """This is used to describe the transition from Cooling Only mode to Heat Recovery mode"""

    Initial_Heat_Recovery_Heating_Capacity_Fraction: Annotated[float, Field(default=1)]
    """This is used to describe the transition from Heating Only mode to Heat Recovery mode"""

    Heat_Recovery_Heating_Capacity_Time_Constant: Annotated[float, Field(default=0)]
    """This is used to describe the transition from Heating Only mode to Heat Recovery mode"""

    Initial_Heat_Recovery_Heating_Energy_Fraction: Annotated[float, Field(default=1)]
    """This is used to describe the transition from Heating Only mode to Heat Recovery mode"""

    Heat_Recovery_Heating_Energy_Time_Constant: Annotated[float, Field(default=0)]
    """This is used to describe the transition from Heating Only mode to Heat Recovery mode"""

    Compressor_Maximum_Delta_Pressure: Annotated[float, Field(ge=0.0, le=50000000.0, default=4500000.0)]

    Compressor_Inverter_Efficiency: Annotated[float, Field(gt=0, le=1.0, default=0.95)]
    """Efficiency of the compressor inverter"""

    Compressor_Evaporative_Capacity_Correction_Factor: Annotated[float, Field(gt=0, default=1.0)]
    """Describe the evaporative capacity difference because of system configuration"""

    Number_Of_Compressor_Loading_Index_Entries: Annotated[int, Field(ge=2, default=2)]
    """Load index describe the compressor operational state,"""

    Compressor_Speed_At_Loading_Index_1: Annotated[float, Field(default=..., gt=0)]
    """Minimum compressor speed"""

    Loading_Index_1_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Loading_Index_1_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Compressor_Speed_At_Loading_Index_2: Annotated[float, Field(default=..., gt=0)]

    Loading_Index_2_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Loading_Index_2_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]

    Compressor_Speed_At_Loading_Index_3: Annotated[float, Field(gt=0)]

    Loading_Index_3_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_3_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_4: Annotated[float, Field(gt=0)]

    Loading_Index_4_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_4_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_5: Annotated[float, Field(gt=0)]

    Loading_Index_5_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_5_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_6: Annotated[float, Field(gt=0)]

    Loading_Index_6_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_6_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_7: Annotated[float, Field(gt=0)]

    Loading_Index_7_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_7_List: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_8: Annotated[float, Field(gt=0)]

    Loading_Index_8_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_8_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_9: Annotated[float, Field(gt=0)]

    Loading_Index_9_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_9_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_10: Annotated[float, Field(gt=0)]

    Loading_Index_10_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_10_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Compressor_Speed_At_Loading_Index_11: Annotated[float, Field(gt=0)]

    Loading_Index_11_Evaporative_Capacity_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]

    Loading_Index_11_Compressor_Power_Multiplier_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]