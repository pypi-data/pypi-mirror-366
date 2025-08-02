from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Weatherproperty_Skytemperature(EpBunch):
    """This object is used to override internal sky temperature calculations."""

    Name: Annotated[str, Field()]
    """blank in this field will apply to all run periods (that is, all objects="""

    Calculation_Type: Annotated[Literal['ScheduleValue', 'DifferenceScheduleDryBulbValue', 'DifferenceScheduleDewPointValue'], Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """if name matches a SizingPeriod:DesignDay, put in a day schedule of this name"""