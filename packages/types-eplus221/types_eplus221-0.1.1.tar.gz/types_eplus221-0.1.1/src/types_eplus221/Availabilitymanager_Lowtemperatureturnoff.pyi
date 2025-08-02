from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Lowtemperatureturnoff(EpBunch):
    """Overrides fan/pump schedules depending on temperature at sensor node."""

    Name: Annotated[str, Field(default=...)]

    Sensor_Node_Name: Annotated[str, Field(default=...)]

    Temperature: Annotated[float, Field(default=...)]

    Applicability_Schedule_Name: Annotated[str, Field()]
    """If blank, defaults to always active"""