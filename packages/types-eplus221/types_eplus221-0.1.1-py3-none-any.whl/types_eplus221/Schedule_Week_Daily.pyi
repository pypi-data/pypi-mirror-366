from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Week_Daily(EpBunch):
    """A Schedule:Week:Daily contains 12 Schedule:Day:Hourly objects, one for each day type."""

    Name: Annotated[str, Field(default=...)]

    Sunday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Monday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Tuesday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Wednesday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Thursday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Friday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Saturday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Holiday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Summerdesignday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Winterdesignday_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Customday1_Schedule_Day_Name: Annotated[str, Field(default=...)]

    Customday2_Schedule_Day_Name: Annotated[str, Field(default=...)]