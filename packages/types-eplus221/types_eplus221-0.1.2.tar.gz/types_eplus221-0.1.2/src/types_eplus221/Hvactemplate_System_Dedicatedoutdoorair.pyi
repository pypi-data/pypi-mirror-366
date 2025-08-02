from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_System_Dedicatedoutdoorair(EpBunch):
    """This object creates a dedicated outdoor air system that must be used with"""

    Name: Annotated[str, Field()]

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on; DOAS System always on. Schedule is used in availability manager"""

    Air_Outlet_Type: Annotated[Literal['DirectIntoZone'], Field(default='DirectIntoZone')]

    Supply_Fan_Flow_Rate: Annotated[str, Field(default='autosize')]

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='1000')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Supply_Fan_Motor_in_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Supply_Fan_Placement: Annotated[Literal['DrawThrough', 'BlowThrough'], Field(default='DrawThrough')]

    Cooling_Coil_Type: Annotated[Literal['ChilledWater', 'ChilledWaterDetailedFlatModel', 'TwoSpeedDX', 'TwoStageDX', 'TwoStageHumidityControlDX', 'HeatExchangerAssistedChilledWater', 'HeatExchangerAssistedDX', 'None'], Field(default='ChilledWater')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Coil_Setpoint_Control_Type: Annotated[Literal['FixedSetpoint', 'Scheduled', 'OutdoorAirTemperatureReset'], Field(default='FixedSetpoint')]

    Cooling_Coil_Design_Setpoint: Annotated[str, Field(default='12.8')]
    """Used for sizing and as constant setpoint if no Cooling Coil Setpoint Schedule Name is specified."""

    Cooling_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Cooling_Coil_Setpoint_at_Outdoor_DryBulb_Low: Annotated[str, Field(default='15.6')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Cooling_Coil_Reset_Outdoor_DryBulb_Low: Annotated[str, Field(default='15.6')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Cooling_Coil_Setpoint_at_Outdoor_DryBulb_High: Annotated[str, Field(default='12.8')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Cooling_Coil_Reset_Outdoor_DryBulb_High: Annotated[str, Field(default='23.3')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    DX_Cooling_Coil_Gross_Rated_Total_Capacity: Annotated[str, Field(default='autosize')]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    DX_Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio: Annotated[str, Field(default='autosize')]
    """Gross SHR"""

    DX_Cooling_Coil_Gross_Rated_COP: Annotated[str, Field(default='3.0')]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Heating_Coil_Type: Annotated[Literal['HotWater', 'Electric', 'Gas', 'None'], Field(default='HotWater')]

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Coil_Setpoint_Control_Type: Annotated[Literal['FixedSetpoint', 'Scheduled', 'OutdoorAirTemperatureReset'], Field(default='FixedSetpoint')]
    """When selecting OutdoorAirTemperatureReset, the Heating Coil Design Setpoint may need to be changed"""

    Heating_Coil_Design_Setpoint: Annotated[str, Field(default='12.2')]
    """Used for sizing and as constant setpoint if no Heating Coil Setpoint Schedule Name is specified."""

    Heating_Coil_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank if constant setpoint"""

    Heating_Coil_Setpoint_at_Outdoor_DryBulb_Low: Annotated[str, Field(default='15.0')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Reset_Outdoor_DryBulb_Low: Annotated[str, Field(default='7.8')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Setpoint_at_Outdoor_DryBulb_High: Annotated[str, Field(default='12.2')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Heating_Coil_Reset_Outdoor_DryBulb_High: Annotated[str, Field(default='12.2')]
    """Applicable only for OutdoorAirTemperatureReset control."""

    Gas_Heating_Coil_Efficiency: Annotated[str, Field(default='0.8')]

    Gas_Heating_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Heat_Recovery_Sensible_Effectiveness: Annotated[str, Field(default='0.70')]

    Heat_Recovery_Latent_Effectiveness: Annotated[str, Field(default='0.65')]

    Heat_Recovery_Heat_Exchanger_Type: Annotated[Literal['Plate', 'Rotary'], Field(default='Plate')]

    Heat_Recovery_Frost_Control_Type: Annotated[Literal['None', 'ExhaustAirRecirculation', 'ExhaustOnly', 'MinimumExhaustTemperature'], Field()]

    Dehumidification_Control_Type: Annotated[Literal['None', 'CoolReheatHeatingCoil', 'CoolReheatDesuperheater', 'Multimode'], Field()]
    """None = meet sensible load only"""

    Dehumidification_Setpoint: Annotated[float, Field(ge=0.0, le=1.0, default=0.00924)]
    """The supply air humidity ratio for dehumidification control."""

    Humidifier_Type: Annotated[Literal['None', 'ElectricSteam'], Field()]

    Humidifier_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always available"""

    Humidifier_Rated_Capacity: Annotated[float, Field(ge=0.0, default=0.000001)]
    """Moisture output rate at full rated power input."""

    Humidifier_Rated_Electric_Power: Annotated[float, Field(ge=0.0, default=autosize)]
    """Electric power input at rated capacity moisture output."""

    Humidifier_Constant_Setpoint: Annotated[float, Field(ge=0.0, le=1.0, default=0.003)]
    """The supply air humidity ratio for humidification control."""

    Dehumidification_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank to use constant setpoint specified in Dehumidification Setpoint above."""

    Humidifier_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Leave blank to use constant setpoint specified in Humidifier Constant Setpoint above."""