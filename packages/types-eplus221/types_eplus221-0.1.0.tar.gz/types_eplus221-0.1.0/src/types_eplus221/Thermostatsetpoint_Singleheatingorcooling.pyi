from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermostatsetpoint_Singleheatingorcooling(EpBunch):
    """Used for a heating and cooling thermostat with a single setpoint. The setpoint can be"""

    Name: Annotated[str, Field(default=...)]

    Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]