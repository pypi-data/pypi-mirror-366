from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermostatsetpoint_Singleheating(EpBunch):
    """Used for a heating only thermostat. The setpoint can be scheduled and varied throughout"""

    Name: Annotated[str, Field(default=...)]

    Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]