from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_System_Dualduct(EpBunch):
    """Dual-duct constant volume or variable volume air loop"""

    Name: Annotated[str, Field(default=...)]

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on; Schedule is used in availability manager"""

    System_Configuration_Type: Annotated[Literal['SingleFanConstantVolume', 'DualFanConstantVolume', 'SingleFanVariableVolume', 'DualFanVariableVolume'], Field(default='SingleFanConstantVolume')]
    """SingleFan - a single supply fan before the split to dual ducts"""

    Main_Supply_Fan_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will *not* be"""

    Main_Supply_Fan_Minimum_Flow_Fraction: Annotated[str, Field(default='0.2')]

    Main_Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Main_Supply_Fan_Delta_Pressure: Annotated[str, Field(default='1000')]

    Main_Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Main_Supply_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Main_Supply_Fan_Part_Load_Power_Coefficients: Annotated[Literal['InletVaneDampers', 'OutletDampers', 'VariableSpeedMotor', 'ASHRAE90.1-2004AppendixG', 'VariableSpeedMotorPressureReset'], Field(default='InletVaneDampers')]
    """This field selects a predefined set of fan power coefficients."""

    Cold_Duct_Supply_Fan_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will *not* be"""

    Cold_Duct_Supply_Fan_Minimum_Flow_Fraction: Annotated[str, Field(default='0.2')]

    Cold_Duct_Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Cold_Duct_Supply_Fan_Delta_Pressure: Annotated[str, Field(default='1000')]

    Cold_Duct_Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Cold_Duct_Supply_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Cold_Duct_Supply_Fan_Part_Load_Power_Coefficients: Annotated[Literal['InletVaneDampers', 'OutletDampers', 'VariableSpeedMotor', 'ASHRAE90.1-2004AppendixG', 'VariableSpeedMotorPressureReset'], Field(default='InletVaneDampers')]
    """This field selects a predefined set of fan power coefficients."""

    Cold_Duct_Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]

    Hot_Duct_Supply_Fan_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will *not* be"""

    Hot_Duct_Supply_Fan_Minimum_Flow_Fraction: Annotated[str, Field(default='0.2')]

    Hot_Duct_Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Hot_Duct_Supply_Fan_Delta_Pressure: Annotated[str, Field(default='1000')]

    Hot_Duct_Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Hot_Duct_Supply_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Hot_Duct_Supply_Fan_Part_Load_Power_Coefficients: Annotated[Literal['InletVaneDampers', 'OutletDampers', 'VariableSpeedMotor', 'ASHRAE90.1-2004AppendixG', 'VariableSpeedMotorPressureReset'], Field(default='InletVaneDampers')]
    """This field selects a predefined set of fan power coefficients."""

    Hot_Duct_Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]

    Cooling_Coil_Type: Annotated[Literal['ChilledWater', 'ChilledWaterDetailedFlatModel', 'None'], Field(default='ChilledWater')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Coil_Setpoint_Control_Type: Annotated[Literal['FixedSetpoint', 'Scheduled', 'OutdoorAirTemperatureReset', 'Warmest'], Field(default='FixedSetpoint')]

    Cooling_Coil_Design_Setpoint_Temperature: Annotated[str, Field(default='12.8')]
    """Used for sizing and as constant setpoint if no Cooling Coil Setpoint Schedule Name is specified."""

    Cooling_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Cooling_Coil_Setpoint_At_Outdoor_Dry_Bulb_Low: Annotated[str, Field(default='15.6')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Cooling_Coil_Reset_Outdoor_Dry_Bulb_Low: Annotated[str, Field(default='15.6')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Cooling_Coil_Setpoint_At_Outdoor_Dry_Bulb_High: Annotated[str, Field(default='12.8')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Cooling_Coil_Reset_Outdoor_Dry_Bulb_High: Annotated[str, Field(default='23.3')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Type: Annotated[Literal['HotWater', 'Electric', 'Gas', 'None'], Field(default='HotWater')]

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Coil_Setpoint_Control_Type: Annotated[Literal['FixedSetpoint', 'Scheduled', 'OutdoorAirTemperatureReset', 'Coldest'], Field(default='FixedSetpoint')]

    Heating_Coil_Design_Setpoint: Annotated[str, Field(default='50.0')]
    """Used for sizing and as constant setpoint if no Heating Coil Setpoint Schedule Name is specified."""

    Heating_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Heating_Coil_Setpoint_At_Outdoor_Dry_Bulb_Low: Annotated[str, Field(default='50.0')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Reset_Outdoor_Dry_Bulb_Low: Annotated[str, Field(default='7.8')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Setpoint_At_Outdoor_Dry_Bulb_High: Annotated[str, Field(default='20.0')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Reset_Outdoor_Dry_Bulb_High: Annotated[str, Field(default='12.2')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Capacity: Annotated[str, Field(default='autosize')]

    Gas_Heating_Coil_Efficiency: Annotated[str, Field(default='0.8')]

    Gas_Heating_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]

    Preheat_Coil_Type: Annotated[Literal['HotWater', 'Electric', 'Gas', 'None'], Field()]

    Preheat_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Preheat_Coil_Design_Setpoint: Annotated[str, Field(default='7.2')]
    """Used for sizing and as constant setpoint if no Preheat Coil Setpoint Schedule Name specified."""

    Preheat_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Gas_Preheat_Coil_Efficiency: Annotated[str, Field(default='0.8')]

    Gas_Preheat_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]

    Maximum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Minimum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Minimum_Outdoor_Air_Control_Type: Annotated[Literal['FixedMinimum', 'ProportionalMinimum'], Field(default='ProportionalMinimum')]

    Minimum_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Schedule values multiply the Minimum Outdoor Air Flow Rate"""

    Economizer_Type: Annotated[Literal['FixedDryBulb', 'FixedEnthalpy', 'DifferentialDryBulb', 'DifferentialEnthalpy', 'FixedDewPointAndDryBulb', 'ElectronicEnthalpy', 'DifferentialDryBulbAndEnthalpy', 'NoEconomizer'], Field(default='NoEconomizer')]

    Economizer_Lockout: Annotated[Literal['NoLockout'], Field(default='NoLockout')]

    Economizer_Upper_Temperature_Limit: Annotated[str, Field()]
    """Outdoor temperature above which economizer is disabled and"""

    Economizer_Lower_Temperature_Limit: Annotated[str, Field()]
    """Outdoor temperature below which economizer is disabled and"""

    Economizer_Upper_Enthalpy_Limit: Annotated[str, Field()]
    """Outdoor enthalpy above which economizer is disabled and"""

    Economizer_Maximum_Limit_Dewpoint_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor dewpoint temperature limit for FixedDewPointAndDryBulb"""

    Cold_Supply_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Supply plenum serves the cold inlets of all zones on this system."""

    Hot_Supply_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Supply plenum serves the hot inlets of all zones on this system."""

    Return_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Supply plenum serves all zones on this system."""

    Night_Cycle_Control: Annotated[Literal['StayOff', 'CycleOnAny', 'CycleOnControlZone'], Field(default='StayOff')]

    Night_Cycle_Control_Zone_Name: Annotated[str, Field()]
    """Applicable only if Night Cycle Control is Cycle On Control Zone."""

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Sensible_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.70')]

    Latent_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.65')]

    Heat_Recovery_Heat_Exchanger_Type: Annotated[Literal['Plate', 'Rotary'], Field(default='Plate')]

    Heat_Recovery_Frost_Control_Type: Annotated[Literal['None', 'ExhaustAirRecirculation', 'ExhaustOnly', 'MinimumExhaustTemperature'], Field()]

    Dehumidification_Control_Type: Annotated[Literal['None', 'CoolReheat'], Field()]
    """None = meet sensible load only"""

    Dehumidification_Control_Zone_Name: Annotated[str, Field()]
    """Zone name where humidistat is located"""

    Dehumidification_Relative_Humidity_Setpoint: Annotated[float, Field(ge=0.0, le=100.0, default=60.0)]
    """Zone relative humidity setpoint in percent (0 to 100)"""

    Dehumidification_Relative_Humidity_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank to use constant setpoint specified in Dehumidification Relative Humidity"""

    Humidifier_Type: Annotated[Literal['None', 'ElectricSteam'], Field()]

    Humidifier_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always available"""

    Humidifier_Rated_Capacity: Annotated[float, Field(ge=0.0, default=0.000001)]
    """Moisture output rate at full rated power input."""

    Humidifier_Rated_Electric_Power: Annotated[float, Field(ge=0.0, default=autosize)]
    """Electric power input at rated capacity moisture output."""

    Humidifier_Control_Zone_Name: Annotated[str, Field()]
    """Zone name where humidistat is located"""

    Humidifier_Relative_Humidity_Setpoint: Annotated[float, Field(ge=0.0, le=100.0, default=30.0)]
    """Zone relative humidity setpoint in percent (0 to 100)."""

    Humidifier_Relative_Humidity_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank to use constant setpoint specified in Humidifier Relative Humidity"""

    Sizing_Option: Annotated[Literal['Coincident', 'NonCoincident'], Field(default='NonCoincident')]
    """Select whether autosized system supply flow rate is the sum of Coincident or NonCoincident"""

    Return_Fan: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Specifies if the system has a return fan."""

    Return_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Return_Fan_Delta_Pressure: Annotated[str, Field(default='500')]

    Return_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Return_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Return_Fan_Part_Load_Power_Coefficients: Annotated[Literal['InletVaneDampers', 'OutletDampers', 'VariableSpeedMotor', 'ASHRAE90.1-2004AppendixG', 'VariableSpeedMotorPressureReset'], Field(default='InletVaneDampers')]
    """This field selects a predefined set of fan power coefficients."""