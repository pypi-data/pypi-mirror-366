from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_System_Unitarysystem(EpBunch):
    """Unitary HVAC system with optional cooling and heating. Supports DX and chilled water,"""

    Name: Annotated[str, Field(default=...)]

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always available. Also see Supply Fan Operating Mode Schedule Name field."""

    Control_Type: Annotated[Literal['Load', 'SetPoint'], Field(default='Load')]
    """Load control requires a Controlling Zone name."""

    Control_Zone_Or_Thermostat_Location_Name: Annotated[str, Field()]
    """This field is required if Control Type is Load."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Supply air flow rate during cooling operation"""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Supply air flow rate during heating operation"""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0, default=autosize)]
    """Supply air flow rate when no cooling or heating is needed"""

    Supply_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Refers to a schedule to specify unitary supply fan operating mode."""

    Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='600')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Supply_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Cooling_Coil_Type: Annotated[Literal['SingleSpeedDX', 'TwoSpeedDX', 'MultiSpeedDX', 'TwoStageDX', 'TwoStageHumidityControlDX', 'HeatExchangerAssistedDX', 'SingleSpeedDXWaterCooled', 'ChilledWater', 'ChilledWaterDetailedFlatModel', 'HeatExchangerAssistedChilledWater', 'None'], Field(default='SingleSpeedDX')]

    Number_Of_Speeds_For_Cooling: Annotated[int, Field(ge=0, le=4, default=1)]
    """Used only for Cooling Coil Type = MultiSpeedDX."""

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Design_Supply_Air_Temperature: Annotated[str, Field(default='12.8')]
    """Used for sizing."""

    Dx_Cooling_Coil_Gross_Rated_Total_Capacity: Annotated[str, Field(default='autosize')]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Dx_Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio: Annotated[str, Field(default='autosize')]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    Dx_Cooling_Coil_Gross_Rated_Cop: Annotated[str, Field(default='3.0')]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Heating_Coil_Type: Annotated[Literal['Electric', 'Gas', 'HotWater', 'SingleSpeedDXHeatPumpAirSource', 'MultiSpeedDXHeatPumpAirSource', 'SingleSpeedDXHeatPumpWaterSource', 'MultiStageElectric', 'MultiStageGas', 'None'], Field(default='Gas')]

    Number_Of_Speeds_Or_Stages_For_Heating: Annotated[int, Field(ge=0, le=4, default=1)]
    """Used only for Heating Coil Type = MultiSpeedDXHeatPumpAirSource),"""

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Design_Supply_Air_Temperature: Annotated[str, Field(default='50.0')]
    """Used for sizing."""

    Heating_Coil_Gross_Rated_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Rated heating capacity excluding the effect of supply air fan heat"""

    Gas_Heating_Coil_Efficiency: Annotated[str, Field(default='0.8')]

    Gas_Heating_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]

    Heat_Pump_Heating_Coil_Gross_Rated_Cop: Annotated[str, Field(default='2.75')]
    """Heating Coil Rated Capacity divided by power input to the compressor and outdoor fan,"""

    Heat_Pump_Heating_Minimum_Outdoor_Dry_Bulb_Temperature: Annotated[float, Field(ge=-20.0, default=-8.0)]

    Heat_Pump_Defrost_Maximum_Outdoor_Dry_Bulb_Temperature: Annotated[float, Field(ge=0.0, le=7.22, default=5.0)]

    Heat_Pump_Defrost_Strategy: Annotated[Literal['ReverseCycle', 'Resistive'], Field(default='ReverseCycle')]

    Heat_Pump_Defrost_Control: Annotated[Literal['Timed', 'OnDemand'], Field(default='Timed')]

    Heat_Pump_Defrost_Time_Period_Fraction: Annotated[float, Field(ge=0.0, default=0.058333)]
    """Fraction of time in defrost mode"""

    Supplemental_Heating_Or_Reheat_Coil_Type: Annotated[Literal['Electric', 'Gas', 'HotWater', 'DesuperHeater', 'None'], Field()]

    Supplemental_Heating_Or_Reheat_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Supplemental_Heating_Or_Reheat_Coil_Capacity: Annotated[str, Field(default='autosize')]

    Supplemental_Heating_Or_Reheat_Coil_Maximum_Outdoor_Dry_Bulb_Temperature: Annotated[float, Field(le=21.0, default=21.0)]
    """Supplemental heater will not operate when outdoor temperature exceeds this value."""

    Supplemental_Gas_Heating_Or_Reheat_Coil_Efficiency: Annotated[str, Field(default='0.8')]
    """Applies only if Supplemental Heating Coil Type is Gas"""

    Supplemental_Gas_Heating_Or_Reheat_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]
    """Applies only if Supplemental Heating Coil Type is Gas"""

    Maximum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Minimum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default='autosize')]

    Minimum_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Schedule values multiply the minimum outdoor air flow rate"""

    Economizer_Type: Annotated[Literal['FixedDryBulb', 'FixedEnthalpy', 'DifferentialDryBulb', 'DifferentialEnthalpy', 'FixedDewPointAndDryBulb', 'ElectronicEnthalpy', 'DifferentialDryBulbAndEnthalpy', 'NoEconomizer'], Field(default='NoEconomizer')]

    Economizer_Lockout: Annotated[Literal['NoLockout', 'LockoutWithHeating', 'LockoutWithCompressor'], Field(default='NoLockout')]

    Economizer_Maximum_Limit_Dry_Bulb_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor dry-bulb temperature limit for FixedDryBulb"""

    Economizer_Maximum_Limit_Enthalpy: Annotated[float, Field()]
    """Enter the maximum outdoor enthalpy limit for FixedEnthalpy economizer control type."""

    Economizer_Maximum_Limit_Dewpoint_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor dewpoint temperature limit for FixedDewPointAndDryBulb"""

    Economizer_Minimum_Limit_Dry_Bulb_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor dry-bulb temperature limit for economizer control."""

    Supply_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Supply plenum serves all zones on this system."""

    Return_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Return plenum serves all zones on this system."""

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Sensible_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.70')]

    Latent_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.65')]
    """Applicable only if Heat Recovery Type is Enthalpy."""

    Heat_Recovery_Heat_Exchanger_Type: Annotated[Literal['Plate', 'Rotary'], Field(default='Plate')]

    Heat_Recovery_Frost_Control_Type: Annotated[Literal['None', 'ExhaustAirRecirculation', 'ExhaustOnly', 'MinimumExhaustTemperature'], Field()]

    Dehumidification_Control_Type: Annotated[Literal['None', 'CoolReheat', 'Multimode'], Field()]
    """None = meet sensible load only"""

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

    Return_Fan_Delta_Pressure: Annotated[str, Field(default='300')]

    Return_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Return_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]