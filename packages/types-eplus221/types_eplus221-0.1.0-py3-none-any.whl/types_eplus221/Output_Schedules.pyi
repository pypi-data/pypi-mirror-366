from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Schedules(EpBunch):
    """Produces a condensed reporting that illustrates the full range of schedule values in"""

    Key_Field: Annotated[Literal['Hourly', 'Timestep'], Field(default=...)]