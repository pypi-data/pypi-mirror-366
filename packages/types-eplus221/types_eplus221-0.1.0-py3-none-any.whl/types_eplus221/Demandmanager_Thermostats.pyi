from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Demandmanager_Thermostats(EpBunch):
    """used for demand limiting ZoneControl:Thermostat objects."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Reset_Control: Annotated[Literal['Off', 'Fixed'], Field(default=...)]

    Minimum_Reset_Duration: Annotated[int, Field(gt=0)]
    """If blank, duration defaults to the timestep"""

    Maximum_Heating_Setpoint_Reset: Annotated[float, Field(default=...)]

    Maximum_Cooling_Setpoint_Reset: Annotated[float, Field(default=...)]

    Reset_Step_Change: Annotated[float, Field()]
    """Not yet implemented"""

    Selection_Control: Annotated[Literal['All', 'RotateMany', 'RotateOne'], Field(default=...)]

    Rotation_Duration: Annotated[int, Field(ge=0)]
    """If blank, duration defaults to the timestep"""

    Thermostat_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_2_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_3_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_4_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_5_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_6_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_7_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_8_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_9_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""

    Thermostat_10_Name: Annotated[str, Field()]
    """Enter the name of a ZoneControl:Thermostat object."""