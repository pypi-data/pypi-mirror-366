from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Thermostat_Thermalcomfort(EpBunch):
    """If you use a ZoneList in the Zone or ZoneList name field then this definition applies"""

    Name: Annotated[str, Field(default=...)]

    Zone_Or_Zonelist_Name: Annotated[str, Field(default=...)]

    Averaging_Method: Annotated[Literal['SpecificObject', 'ObjectAverage', 'PeopleAverage'], Field(default='PeopleAverage')]
    """The method used to calculate thermal comfort dry-bulb temperature setpoint"""

    Specific_People_Name: Annotated[str, Field()]
    """Used only when Averaging Method = SpecificObject in the previous field."""

    Minimum_Dry_Bulb_Temperature_Setpoint: Annotated[float, Field(ge=0, le=50, default=0)]

    Maximum_Dry_Bulb_Temperature_Setpoint: Annotated[float, Field(ge=0, le=50, default=50)]

    Thermal_Comfort_Control_Type_Schedule_Name: Annotated[str, Field(default=...)]
    """The Thermal Comfort Control Type Schedule contains values that are appropriate control types."""

    Thermal_Comfort_Control_1_Object_Type: Annotated[Literal['ThermostatSetpoint:ThermalComfort:Fanger:SingleHeating', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleHeatingOrCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:DualSetpoint'], Field(default=...)]

    Thermal_Comfort_Control_1_Name: Annotated[str, Field(default=...)]
    """Control type names are names for individual control type objects."""

    Thermal_Comfort_Control_2_Object_Type: Annotated[Literal['ThermostatSetpoint:ThermalComfort:Fanger:SingleHeating', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleHeatingOrCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:DualSetpoint'], Field()]

    Thermal_Comfort_Control_2_Name: Annotated[str, Field()]
    """Control Type names are names for individual control type objects."""

    Thermal_Comfort_Control_3_Object_Type: Annotated[Literal['ThermostatSetpoint:ThermalComfort:Fanger:SingleHeating', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleHeatingOrCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:DualSetpoint'], Field()]

    Thermal_Comfort_Control_3_Name: Annotated[str, Field()]
    """Control type names are names for individual control type objects."""

    Thermal_Comfort_Control_4_Object_Type: Annotated[Literal['ThermostatSetpoint:ThermalComfort:Fanger:SingleHeating', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:SingleHeatingOrCooling', 'ThermostatSetpoint:ThermalComfort:Fanger:DualSetpoint'], Field()]

    Thermal_Comfort_Control_4_Name: Annotated[str, Field()]
    """Control type names are names for individual control type objects."""