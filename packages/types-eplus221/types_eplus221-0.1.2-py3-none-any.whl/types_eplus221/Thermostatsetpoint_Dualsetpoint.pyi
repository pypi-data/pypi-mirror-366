from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermostatsetpoint_Dualsetpoint(EpBunch):
    """Used for a heating and cooling thermostat with dual setpoints. The setpoints can be"""

    Name: Annotated[str, Field(default=...)]

    Heating_Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]

    Cooling_Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]