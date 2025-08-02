from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Runperiodcontrol_Specialdays(EpBunch):
    """This object sets up holidays/special days to be used during weather file"""

    Name: Annotated[str, Field(default=...)]

    Start_Date: Annotated[str, Field(default=...)]
    """Dates can be several formats:"""

    Duration: Annotated[str, Field(default='1')]

    Special_Day_Type: Annotated[Literal['Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field(default='Holiday')]
    """Special Day Type selects the schedules appropriate for each day so labeled"""