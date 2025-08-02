from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_System_Vrf(EpBunch):
    """Variable refrigerant flow (VRF) heat pump condensing unit. Serves one or more VRF zone"""

    Name: Annotated[str, Field(default=...)]

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Enter the total cooling capacity in watts at rated conditions or set to autosize."""

    Gross_Rated_Cooling_Cop: Annotated[float, Field(gt=0.0, default=3.3)]
    """Enter the coefficient of performance at rated conditions or leave blank to use default."""

    Minimum_Outdoor_Temperature_In_Cooling_Mode: Annotated[float, Field(default=-6.0)]
    """Enter the minimum outdoor temperature allowed for cooling operation."""

    Maximum_Outdoor_Temperature_In_Cooling_Mode: Annotated[float, Field(default=43.0)]
    """Enter the maximum outdoor temperature allowed for cooling operation."""

    Gross_Rated_Heating_Capacity: Annotated[float, Field(default=autosize)]
    """Enter the heating capacity in watts at rated conditions or set to autosize."""

    Rated_Heating_Capacity_Sizing_Ratio: Annotated[float, Field(ge=1.0, default=1.0)]
    """If the Gross Rated Heating Capacity is autosized, the heating capacity is sized"""

    Gross_Rated_Heating_Cop: Annotated[float, Field(default=3.4)]
    """COP includes compressor and condenser fan electrical energy input"""

    Minimum_Outdoor_Temperature_In_Heating_Mode: Annotated[float, Field(default=-20.0)]
    """Enter the minimum outdoor temperature allowed for heating operation."""

    Maximum_Outdoor_Temperature_In_Heating_Mode: Annotated[float, Field(default=16.0)]
    """Enter the maximum outdoor temperature allowed for heating operation."""

    Minimum_Heat_Pump_Part_Load_Ratio: Annotated[float, Field(default=0.15)]
    """Enter the minimum heat pump part-load ratio (PLR). When the cooling or heating PLR is"""

    Zone_Name_For_Master_Thermostat_Location: Annotated[str, Field()]
    """Enter the name of the zone where the master thermostat is located."""

    Master_Thermostat_Priority_Control_Type: Annotated[Literal['LoadPriority', 'ZonePriority', 'ThermostatOffsetPriority', 'MasterThermostatPriority', 'Scheduled'], Field(default='MasterThermostatPriority')]
    """Choose a thermostat control logic scheme. If these control types fail to control zone"""

    Thermostat_Priority_Schedule_Name: Annotated[str, Field()]
    """this field is required if Master Thermostat Priority Control Type is Scheduled."""

    Heat_Pump_Waste_Heat_Recovery: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """This field is reserved for future use. The only valid choice is No."""

    Equivalent_Piping_Length_Used_For_Piping_Correction_Factor_In_Cooling_Mode: Annotated[float, Field(default=30.0)]
    """Enter the equivalent length of the farthest terminal unit from the condenser"""

    Vertical_Height_Used_For_Piping_Correction_Factor: Annotated[float, Field(default=10.0)]
    """Enter the height difference between the highest and lowest terminal unit"""

    Equivalent_Piping_Length_Used_For_Piping_Correction_Factor_In_Heating_Mode: Annotated[float, Field(default=30.0)]
    """Enter the equivalent length of the farthest terminal unit from the condenser"""

    Crankcase_Heater_Power_Per_Compressor: Annotated[float, Field(default=33.0)]
    """Enter the value of the resistive heater located in the compressor(s). This heater"""

    Number_Of_Compressors: Annotated[int, Field(default=2)]
    """Enter the total number of compressor. This input is used only for crankcase"""

    Ratio_Of_Compressor_Size_To_Total_Compressor_Capacity: Annotated[float, Field(default=0.5)]
    """Enter the ratio of the first stage compressor to total compressor capacity."""

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Crankcase_Heater: Annotated[float, Field(default=5.0)]
    """Enter the maximum outdoor temperature above which the crankcase heaters are disabled."""

    Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='Resistive')]
    """Select a defrost strategy. Reverse cycle reverses the operating mode from heating to cooling"""

    Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]
    """Choose a defrost control type. Either use a fixed Timed defrost period or select"""

    Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode."""

    Resistive_Defrost_Heater_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the size of the resistive defrost heating element."""

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Defrost_Operation: Annotated[float, Field(default=5.0)]
    """Enter the maximum outdoor temperature above which defrost operation is disabled."""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled', 'WaterCooled'], Field(default='AirCooled')]
    """Select either an air cooled or evaporatively cooled condenser."""

    Water_Condenser_Volume_Flow_Rate: Annotated[float, Field(default=autosize)]
    """Only used when Condenser Type = WaterCooled."""

    Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]
    """Enter the effectiveness of the evaporatively cooled condenser."""

    Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Used to calculate evaporative condenser water use."""

    Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0, default=0.0)]
    """Rated power consumed by the evaporative condenser's water pump."""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'Diesel', 'Gasoline', 'FuelOil#1', 'FuelOil#2', 'OtherFuel1', 'OtherFuel2'], Field(default='Electricity')]

    Minimum_Outdoor_Temperature_In_Heat_Recovery_Mode: Annotated[float, Field(default=-15)]
    """The minimum outdoor temperature below which heat"""

    Maximum_Outdoor_Temperature_In_Heat_Recovery_Mode: Annotated[float, Field(default=45)]
    """The maximum outdoor temperature above which heat"""