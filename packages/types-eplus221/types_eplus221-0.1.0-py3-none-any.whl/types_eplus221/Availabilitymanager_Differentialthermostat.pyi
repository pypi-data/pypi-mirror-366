from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Differentialthermostat(EpBunch):
    """Overrides fan/pump schedules depending on temperature difference between two nodes."""

    Name: Annotated[str, Field(default=...)]

    Hot_Node_Name: Annotated[str, Field(default=...)]

    Cold_Node_Name: Annotated[str, Field(default=...)]

    Temperature_Difference_On_Limit: Annotated[float, Field(default=...)]

    Temperature_Difference_Off_Limit: Annotated[float, Field()]
    """Defaults to Temperature Difference On Limit."""