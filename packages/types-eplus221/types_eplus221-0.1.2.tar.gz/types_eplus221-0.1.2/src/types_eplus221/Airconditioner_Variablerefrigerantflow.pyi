from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airconditioner_Variablerefrigerantflow(EpBunch):
    """Variable refrigerant flow (VRF) air-to-air heat pump condensing unit (includes one"""

    Heat_Pump_Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this variable refrigerant flow heat pump."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(gt=0.0)]
    """Enter the total cooling capacity in watts at rated conditions or set to autosize."""

    Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.3)]
    """Enter the coefficient of performance at rated conditions or leave blank to use default."""

    Minimum_Outdoor_Temperature_in_Cooling_Mode: Annotated[float, Field(default=-6.0)]
    """Enter the minimum outdoor temperature allowed for cooling operation."""

    Maximum_Outdoor_Temperature_in_Cooling_Mode: Annotated[float, Field(default=43.0)]
    """Enter the maximum outdoor temperature allowed for cooling operation."""

    Cooling_Capacity_Ratio_Modifier_Function_of_Low_Temperature_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents full load cooling capacity ratio as a"""

    Cooling_Capacity_Ratio_Boundary_Curve_Name: Annotated[str, Field()]
    """This curve object is used to allow separate low and high cooling capacity ratio"""

    Cooling_Capacity_Ratio_Modifier_Function_of_High_Temperature_Curve_Name: Annotated[str, Field()]
    """This curve object is used to describe the high outdoor temperature"""

    Cooling_Energy_Input_Ratio_Modifier_Function_of_Low_Temperature_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents cooling energy ratio as a function of"""

    Cooling_Energy_Input_Ratio_Boundary_Curve_Name: Annotated[str, Field()]
    """This curve object is used to allow separate low and high cooling energy input ratio"""

    Cooling_Energy_Input_Ratio_Modifier_Function_of_High_Temperature_Curve_Name: Annotated[str, Field()]
    """This curve object is used to describe the high outdoor temperature"""

    Cooling_Energy_Input_Ratio_Modifier_Function_of_Low_PartLoad_Ratio_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents cooling energy ratio as a function of"""

    Cooling_Energy_Input_Ratio_Modifier_Function_of_High_PartLoad_Ratio_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents cooling energy ratio as a function of"""

    Cooling_Combination_Ratio_Correction_Factor_Curve_Name: Annotated[str, Field()]
    """This curve defines how rated capacity changes when the total indoor terminal unit cooling"""

    Cooling_PartLoad_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """This curve defines the cycling losses when the heat pump compressor cycles on and off"""

    Gross_Rated_Heating_Capacity: Annotated[float, Field()]
    """Enter the heating capacity in watts at rated conditions or set to autosize."""

    Rated_Heating_Capacity_Sizing_Ratio: Annotated[float, Field(ge=1.0, default=1.0)]
    """If the Gross Rated Heating Capacity is autosized, the heating capacity is sized"""

    Gross_Rated_Heating_COP: Annotated[float, Field(default=3.4)]
    """COP includes compressor and condenser fan electrical energy input"""

    Minimum_Outdoor_Temperature_in_Heating_Mode: Annotated[float, Field(default=-20.0)]
    """Enter the minimum outdoor temperature allowed for heating operation."""

    Maximum_Outdoor_Temperature_in_Heating_Mode: Annotated[float, Field(default=16.0)]
    """Enter the maximum outdoor temperature allowed for heating operation."""

    Heating_Capacity_Ratio_Modifier_Function_of_Low_Temperature_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents full load heating capacity ratio as a"""

    Heating_Capacity_Ratio_Boundary_Curve_Name: Annotated[str, Field()]
    """This curve object is used to allow separate low and high heating capacity ratio"""

    Heating_Capacity_Ratio_Modifier_Function_of_High_Temperature_Curve_Name: Annotated[str, Field()]
    """This curve object is used to describe the high outdoor temperature"""

    Heating_Energy_Input_Ratio_Modifier_Function_of_Low_Temperature_Curve_Name: Annotated[str, Field()]
    """Enter a curve name that represents heating energy ratio as a function of"""

    Heating_Energy_Input_Ratio_Boundary_Curve_Name: Annotated[str, Field()]
    """This curve object is used to allow separate low and high heating energy input ratio"""

    Heating_Energy_Input_Ratio_Modifier_Function_of_High_Temperature_Curve_Name: Annotated[str, Field()]
    """This curve object is used to allow separate performance curves for heating energy."""

    Heating_Performance_Curve_Outdoor_Temperature_Type: Annotated[Literal['DryBulbTemperature', 'WetBulbTemperature'], Field(default='WetBulbTemperature')]
    """Determines temperature type for heating capacity curves and heating energy curves."""

    Heating_Energy_Input_Ratio_Modifier_Function_of_Low_PartLoad_Ratio_Curve_Name: Annotated[str, Field()]
    """This curve represents the heating energy input ratio for part-load ratios less than 1."""

    Heating_Energy_Input_Ratio_Modifier_Function_of_High_PartLoad_Ratio_Curve_Name: Annotated[str, Field()]
    """This curve represents the heating energy input ratio for part-load ratios greater than 1."""

    Heating_Combination_Ratio_Correction_Factor_Curve_Name: Annotated[str, Field()]
    """This curve defines how rated capacity changes when the total indoor terminal unit heating"""

    Heating_PartLoad_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """This curve defines the cycling losses when the heat pump compressor cycles on and off"""

    Minimum_Heat_Pump_PartLoad_Ratio: Annotated[float, Field(default=0.15)]
    """Enter the minimum heat pump part-load ratio (PLR). When the cooling or heating PLR is"""

    Zone_Name_for_Master_Thermostat_Location: Annotated[str, Field()]
    """Enter the name of the zone where the master thermostat is located."""

    Master_Thermostat_Priority_Control_Type: Annotated[Literal['LoadPriority', 'ZonePriority', 'ThermostatOffsetPriority', 'MasterThermostatPriority', 'Scheduled'], Field(default='MasterThermostatPriority')]
    """Choose a thermostat control logic scheme. If these control types fail to control zone"""

    Thermostat_Priority_Schedule_Name: Annotated[str, Field()]
    """this field is required if Master Thermostat Priority Control Type is Scheduled."""

    Zone_Terminal_Unit_List_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneTerminalUnitList. This list connects zone terminal units to this"""

    Heat_Pump_Waste_Heat_Recovery: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """This field enables heat recovery operation within this VRF outdoor unit."""

    Equivalent_Piping_Length_used_for_Piping_Correction_Factor_in_Cooling_Mode: Annotated[float, Field()]
    """Enter the equivalent length of the farthest terminal unit from the condenser"""

    Vertical_Height_used_for_Piping_Correction_Factor: Annotated[float, Field()]
    """Enter the height difference between the highest and lowest terminal unit"""

    Piping_Correction_Factor_for_Length_in_Cooling_Mode_Curve_Name: Annotated[str, Field()]
    """PCF = a0 + a1*L + a2*L^2 + a3*L^3 + a4*H"""

    Piping_Correction_Factor_for_Height_in_Cooling_Mode_Coefficient: Annotated[float, Field(default=0)]
    """PCF = a0 + a1*L + a2*L^2 + a3*L^3 + a4*H"""

    Equivalent_Piping_Length_used_for_Piping_Correction_Factor_in_Heating_Mode: Annotated[float, Field()]
    """Enter the equivalent length of the farthest terminal unit from the condenser"""

    Piping_Correction_Factor_for_Length_in_Heating_Mode_Curve_Name: Annotated[str, Field()]
    """PCF = a0 + a1*L + a2*L^2 + a3*L^3 + a4*H"""

    Piping_Correction_Factor_for_Height_in_Heating_Mode_Coefficient: Annotated[float, Field(default=0)]
    """PCF = a0 + a1*L + a2*L^2 + a3*L^3 + a4*H"""

    Crankcase_Heater_Power_per_Compressor: Annotated[float, Field(default=33.0)]
    """Enter the value of the resistive heater located in the compressor(s). This heater"""

    Number_of_Compressors: Annotated[int, Field(default=2)]
    """Enter the total number of compressor. This input is used only for crankcase"""

    Ratio_of_Compressor_Size_to_Total_Compressor_Capacity: Annotated[float, Field(default=0.5)]
    """Enter the ratio of the first stage compressor to total compressor capacity."""

    Maximum_Outdoor_DryBulb_Temperature_for_Crankcase_Heater: Annotated[float, Field(default=5.0)]
    """Enter the maximum outdoor temperature above which the crankcase heaters are disabled."""

    Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='Resistive')]
    """Select a defrost strategy. Reverse cycle reverses the operating mode from heating to cooling"""

    Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]
    """Choose a defrost control type. Either use a fixed Timed defrost period or select"""

    Defrost_Energy_Input_Ratio_Modifier_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """A valid performance curve must be used if reversecycle defrost strategy is selected."""

    Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode."""

    Resistive_Defrost_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """Enter the size of the resistive defrost heating element."""

    Maximum_Outdoor_Drybulb_Temperature_for_Defrost_Operation: Annotated[float, Field(default=5.0)]
    """Enter the maximum outdoor temperature above which defrost operation is disabled."""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled', 'WaterCooled'], Field(default='AirCooled')]
    """Select either an air-cooled, evaporatively-cooled or water-cooled condenser."""

    Condenser_Inlet_Node_Name: Annotated[str, Field()]
    """Choose an outside air node name or leave this field blank to use weather data."""

    Condenser_Outlet_Node_Name: Annotated[str, Field()]
    """Enter a water outlet node name if Condenser Type = WaterCooled."""

    Water_Condenser_Volume_Flow_Rate: Annotated[float, Field()]
    """Only used when Condenser Type = WaterCooled."""

    Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]
    """Enter the effectiveness of the evaporatively cooled condenser."""

    Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use."""

    Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0, default=0.0)]
    """Rated power consumed by the evaporative condenser's water pump."""

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]
    """A separate storage tank may be used to supply an evaporatively cooled condenser."""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default='Electricity')]

    Minimum_Outdoor_Temperature_in_Heat_Recovery_Mode: Annotated[float, Field()]
    """The minimum outdoor temperature below which heat"""

    Maximum_Outdoor_Temperature_in_Heat_Recovery_Mode: Annotated[float, Field()]
    """The maximum outdoor temperature above which heat"""

    Heat_Recovery_Cooling_Capacity_Modifier_Curve_Name: Annotated[str, Field()]
    """Enter the name of a performance curve which represents"""

    Initial_Heat_Recovery_Cooling_Capacity_Fraction: Annotated[float, Field(default=0.5)]
    """Enter the fractional capacity available at the start"""

    Heat_Recovery_Cooling_Capacity_Time_Constant: Annotated[float, Field(default=0.15)]
    """Enter the time constant used to model the transition"""

    Heat_Recovery_Cooling_Energy_Modifier_Curve_Name: Annotated[str, Field()]
    """Enter the name of a performance curve which represents"""

    Initial_Heat_Recovery_Cooling_Energy_Fraction: Annotated[float, Field(default=1.0)]
    """Enter the fractional electric consumption rate at the start"""

    Heat_Recovery_Cooling_Energy_Time_Constant: Annotated[float, Field(default=0)]
    """Enter the time constant used to model the transition"""

    Heat_Recovery_Heating_Capacity_Modifier_Curve_Name: Annotated[str, Field()]
    """Enter the name of a performance curve which represents"""

    Initial_Heat_Recovery_Heating_Capacity_Fraction: Annotated[float, Field(default=1)]
    """Enter the fractional capacity available at the start"""

    Heat_Recovery_Heating_Capacity_Time_Constant: Annotated[float, Field(default=0.15)]
    """Enter the time constant used to model the transition"""

    Heat_Recovery_Heating_Energy_Modifier_Curve_Name: Annotated[str, Field()]
    """Enter the name of a performance curve which represents"""

    Initial_Heat_Recovery_Heating_Energy_Fraction: Annotated[float, Field(default=1)]
    """Enter the fractional electric consumption rate at the start"""

    Heat_Recovery_Heating_Energy_Time_Constant: Annotated[float, Field(default=0)]
    """Enter the time constant used to model the transition"""