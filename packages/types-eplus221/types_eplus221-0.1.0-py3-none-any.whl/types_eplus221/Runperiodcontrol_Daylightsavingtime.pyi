from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Runperiodcontrol_Daylightsavingtime(EpBunch):
    """This object sets up the daylight saving time period for any RunPeriod."""

    Start_Date: Annotated[str, Field(default=...)]

    End_Date: Annotated[str, Field(default=...)]
    """Dates can be several formats:"""