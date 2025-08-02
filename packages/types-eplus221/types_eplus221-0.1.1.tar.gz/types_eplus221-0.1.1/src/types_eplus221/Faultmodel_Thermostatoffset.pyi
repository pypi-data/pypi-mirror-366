from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Thermostatoffset(EpBunch):
    """This object describes fault of thermostat offset"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Thermostat_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneControl:Thermostat object."""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Reference_Thermostat_Offset: Annotated[float, Field(gt=-10, lt=10, default=2)]