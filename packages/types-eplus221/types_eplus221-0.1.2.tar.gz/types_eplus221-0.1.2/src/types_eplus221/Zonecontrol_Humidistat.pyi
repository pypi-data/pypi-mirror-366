from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Humidistat(EpBunch):
    """Specifies zone relative humidity setpoint schedules for humidifying and dehumidifying."""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Humidifying_Relative_Humidity_Setpoint_Schedule_Name: Annotated[str, Field(default=...)]
    """hourly schedule values should be in Relative Humidity (percent)"""

    Dehumidifying_Relative_Humidity_Setpoint_Schedule_Name: Annotated[str, Field()]
    """hourly schedule values should be in Relative Humidity (percent)"""