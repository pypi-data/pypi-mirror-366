from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_System_Unitary(EpBunch):
    """Unitary furnace with air conditioner"""

    Name: Annotated[str, Field(default=...)]

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on; Unitary System always on. Schedule is used in availability manager"""

    Control_Zone_Or_Thermostat_Location_Name: Annotated[str, Field(default=...)]

    Supply_Fan_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will *not* be"""

    Supply_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Refers to a schedule to specify unitary supply fan operating mode."""

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='600')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Supply_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Cooling_Coil_Type: Annotated[Literal['SingleSpeedDX', 'None'], Field(default='SingleSpeedDX')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Design_Supply_Air_Temperature: Annotated[str, Field(default='12.8')]
    """Used for sizing."""

    Cooling_Coil_Gross_Rated_Total_Capacity: Annotated[str, Field(default='autosize')]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio: Annotated[str, Field(default='autosize')]
    """Gross SHR"""

    Cooling_Coil_Gross_Rated_Cop: Annotated[str, Field(default='3.0')]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Heating_Coil_Type: Annotated[Literal['Electric', 'Gas', 'HotWater'], Field(default=...)]

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Design_Supply_Air_Temperature: Annotated[str, Field(default='50.0')]
    """Used for sizing."""

    Heating_Coil_Capacity: Annotated[str, Field(default='autosize')]

    Gas_Heating_Coil_Efficiency: Annotated[str, Field(default='0.8')]

    Gas_Heating_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]

    Maximum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Minimum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Minimum_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Schedule values multiply the minimum outdoor air flow rate"""

    Economizer_Type: Annotated[Literal['FixedDryBulb', 'FixedEnthalpy', 'DifferentialDryBulb', 'DifferentialEnthalpy', 'FixedDewPointAndDryBulb', 'ElectronicEnthalpy', 'DifferentialDryBulbAndEnthalpy', 'NoEconomizer'], Field(default='NoEconomizer')]

    Economizer_Lockout: Annotated[Literal['NoLockout', 'LockoutWithHeating', 'LockoutWithCompressor'], Field(default='NoLockout')]

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
    """Plenum zone name. Return plenum serves all zones on this system."""

    Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Night_Cycle_Control: Annotated[Literal['StayOff', 'CycleOnAny', 'CycleOnControlZone'], Field(default='StayOff')]

    Night_Cycle_Control_Zone_Name: Annotated[str, Field()]
    """Applicable only if Night Cycle Control is Cycle On Control Zone."""

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Sensible_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.70')]

    Latent_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.65')]
    """Applicable only if Heat Recovery Type is Enthalpy."""

    Dehumidification_Control_Type: Annotated[Literal['None', 'CoolReheatHeatingCoil', 'CoolReheatDesuperheater'], Field()]
    """None = meet sensible cooling load only"""

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

    Return_Fan: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Specifies if the system has a return fan."""

    Return_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Return_Fan_Delta_Pressure: Annotated[str, Field(default='500')]

    Return_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Return_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]