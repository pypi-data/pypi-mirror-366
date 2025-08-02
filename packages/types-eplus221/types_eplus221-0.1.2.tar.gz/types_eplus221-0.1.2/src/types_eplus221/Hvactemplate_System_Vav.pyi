from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_System_Vav(EpBunch):
    """Variable Air Volume (VAV) air loop with optional heating coil"""

    Name: Annotated[str, Field(default=...)]

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on; VAV System always on. Schedule is used in availability manager"""

    Supply_Fan_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will *not* be"""

    Supply_Fan_Minimum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field is only used to set a minimum part load on the VAV fan power curve."""

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='1000')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Supply_Fan_Motor_in_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Cooling_Coil_Type: Annotated[Literal['ChilledWater', 'ChilledWaterDetailedFlatModel'], Field(default='ChilledWater')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Cooling_Coil_Design_Setpoint: Annotated[str, Field(default='12.8')]
    """Used for sizing and as constant setpoint if no Cooling Coil Setpoint Schedule Name is specified."""

    Heating_Coil_Type: Annotated[Literal['HotWater', 'Electric', 'Gas', 'None'], Field()]

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Heating_Coil_Design_Setpoint: Annotated[str, Field(default='10.0')]
    """Used for sizing and as constant setpoint if no Heating Coil Setpoint Schedule Name is specified."""

    Gas_Heating_Coil_Efficiency: Annotated[str, Field(default='0.8')]

    Gas_Heating_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]

    Preheat_Coil_Type: Annotated[Literal['HotWater', 'Electric', 'Gas', 'None'], Field()]

    Preheat_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Preheat_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Preheat_Coil_Design_Setpoint: Annotated[str, Field(default='7.2')]
    """Used for sizing and as constant setpoint if no Preheat Coil Setpoint Schedule Name specified."""

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

    Supply_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Supply plenum serves all zones on this system."""

    Return_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Supply plenum serves all zones on this system."""

    Supply_Fan_Placement: Annotated[Literal['DrawThrough', 'BlowThrough'], Field(default='DrawThrough')]

    Supply_Fan_PartLoad_Power_Coefficients: Annotated[Literal['InletVaneDampers', 'OutletDampers', 'VariableSpeedMotor', 'ASHRAE90.1-2004AppendixG', 'VariableSpeedMotorPressureReset'], Field(default='InletVaneDampers')]
    """This field selects a predefined set of fan power coefficients."""

    Night_Cycle_Control: Annotated[Literal['StayOff', 'CycleOnAny', 'CycleOnControlZone', 'CycleOnAnyZoneFansOnly'], Field(default='StayOff')]

    Night_Cycle_Control_Zone_Name: Annotated[str, Field()]
    """Applicable only if Night Cycle Control is Cycle On Control Zone."""

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Sensible_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.70')]

    Latent_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.65')]

    Cooling_Coil_Setpoint_Reset_Type: Annotated[Literal['None', 'Warmest', 'OutdoorAirTemperatureReset', 'WarmestTemperatureFirst'], Field()]
    """Overrides Cooling Coil Setpoint Schedule Name"""

    Heating_Coil_Setpoint_Reset_Type: Annotated[Literal['None', 'OutdoorAirTemperatureReset'], Field()]
    """Overrides Heating Coil Setpoint Schedule Name"""

    Dehumidification_Control_Type: Annotated[Literal['None', 'CoolReheat'], Field()]
    """None = meet sensible load only"""

    Dehumidification_Control_Zone_Name: Annotated[str, Field()]
    """Zone name where humidistat is located"""

    Dehumidification_Setpoint: Annotated[float, Field(ge=0.0, le=100.0, default=60.0)]
    """Zone relative humidity setpoint in percent (0 to 100)"""

    Humidifier_Type: Annotated[Literal['None', 'ElectricSteam'], Field()]

    Humidifier_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always available"""

    Humidifier_Rated_Capacity: Annotated[float, Field(ge=0.0, default=0.000001)]
    """Moisture output rate at full rated power input."""

    Humidifier_Rated_Electric_Power: Annotated[float, Field(ge=0.0, default=autosize)]
    """Electric power input at rated capacity moisture output."""

    Humidifier_Control_Zone_Name: Annotated[str, Field()]
    """Zone name where humidistat is located"""

    Humidifier_Setpoint: Annotated[float, Field(ge=0.0, le=100.0, default=30.0)]
    """Zone relative humidity setpoint in percent (0 to 100)"""

    Sizing_Option: Annotated[Literal['Coincident', 'NonCoincident'], Field(default='NonCoincident')]
    """Select whether autosized system supply flow rate is the sum of Coincident or NonCoincident"""

    Return_Fan: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Specifies if the system has a return fan."""

    Return_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Return_Fan_Delta_Pressure: Annotated[str, Field(default='500')]

    Return_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Return_Fan_Motor_in_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Return_Fan_PartLoad_Power_Coefficients: Annotated[Literal['InletVaneDampers', 'OutletDampers', 'VariableSpeedMotor', 'ASHRAE90.1-2004AppendixG', 'VariableSpeedMotorPressureReset'], Field(default='InletVaneDampers')]
    """This field selects a predefined set of fan power coefficients."""