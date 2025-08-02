from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Scheduledon(EpBunch):
    """Determines the availability of a loop or system: only controls the turn on action."""

    Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]