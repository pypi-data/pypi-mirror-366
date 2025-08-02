from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Thermostat(EpBunch):
    """Define the Thermostat settings for a zone or list of zones."""

    Name: Annotated[str, Field(default=...)]

    Zone_Or_Zonelist_Name: Annotated[str, Field(default=...)]

    Control_Type_Schedule_Name: Annotated[str, Field(default=...)]
    """This schedule contains appropriate control types for thermostat."""

    Control_1_Object_Type: Annotated[Literal['ThermostatSetpoint:SingleHeating', 'ThermostatSetpoint:SingleCooling', 'ThermostatSetpoint:SingleHeatingOrCooling', 'ThermostatSetpoint:DualSetpoint'], Field(default=...)]

    Control_1_Name: Annotated[str, Field(default=...)]
    """Control names are names of individual control objects (e.g. ThermostatSetpoint:SingleHeating)"""

    Control_2_Object_Type: Annotated[Literal['ThermostatSetpoint:SingleHeating', 'ThermostatSetpoint:SingleCooling', 'ThermostatSetpoint:SingleHeatingOrCooling', 'ThermostatSetpoint:DualSetpoint'], Field()]

    Control_2_Name: Annotated[str, Field()]
    """Control names are names of individual control objects (e.g. ThermostatSetpoint:SingleHeating)"""

    Control_3_Object_Type: Annotated[Literal['ThermostatSetpoint:SingleHeating', 'ThermostatSetpoint:SingleCooling', 'ThermostatSetpoint:SingleHeatingOrCooling', 'ThermostatSetpoint:DualSetpoint'], Field()]

    Control_3_Name: Annotated[str, Field()]
    """Control names are names of individual control objects (e.g. ThermostatSetpoint:SingleHeating)"""

    Control_4_Object_Type: Annotated[Literal['ThermostatSetpoint:SingleHeating', 'ThermostatSetpoint:SingleCooling', 'ThermostatSetpoint:SingleHeatingOrCooling', 'ThermostatSetpoint:DualSetpoint'], Field()]

    Control_4_Name: Annotated[str, Field()]
    """Control names are names of individual control objects (e.g. ThermostatSetpoint:SingleHeating)"""

    Temperature_Difference_Between_Cutout_And_Setpoint: Annotated[float, Field(ge=0.0, default=0.0)]
    """This optional choice field provides a temperature difference between cut-out temperature and"""