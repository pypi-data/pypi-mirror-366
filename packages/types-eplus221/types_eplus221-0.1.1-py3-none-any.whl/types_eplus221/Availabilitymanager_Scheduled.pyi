from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Scheduled(EpBunch):
    """Determines the availability of a loop or system: whether it is on or off."""

    Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]