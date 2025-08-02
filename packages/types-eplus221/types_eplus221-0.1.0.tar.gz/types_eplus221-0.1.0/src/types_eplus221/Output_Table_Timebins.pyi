from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Table_Timebins(EpBunch):
    """Produces a bin report in the table output file which shows the amount of time in hours"""

    Key_Value: Annotated[str, Field(default='*')]
    """use '*' (without quotes) to apply this variable to all keys"""

    Variable_Name: Annotated[str, Field(default=...)]

    Interval_Start: Annotated[float, Field()]
    """The lowest value for the intervals being binned into."""

    Interval_Size: Annotated[float, Field()]
    """The size of the bins starting with Interval start."""

    Interval_Count: Annotated[int, Field(ge=1, le=20)]
    """The number of bins used. The number of hours below the start of the"""

    Schedule_Name: Annotated[str, Field()]
    """Optional schedule name. Binning is performed for non-zero hours."""

    Variable_Type: Annotated[Literal['Energy', 'Temperature', 'VolumetricFlow', 'Power'], Field()]
    """Optional input on the type of units for the variable used by other fields in the object."""