from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Week_Daily(EpBunch):
    """A Schedule:Week:Daily contains 12 Schedule:Day:Hourly objects, one for each day type."""

    Name: Annotated[str, Field(default=...)]

    Sunday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Monday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Tuesday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Wednesday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Thursday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Friday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Saturday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    Holiday_ScheduleDay_Name: Annotated[str, Field(default=...)]

    SummerDesignDay_ScheduleDay_Name: Annotated[str, Field(default=...)]

    WinterDesignDay_ScheduleDay_Name: Annotated[str, Field(default=...)]

    CustomDay1_ScheduleDay_Name: Annotated[str, Field(default=...)]

    CustomDay2_ScheduleDay_Name: Annotated[str, Field(default=...)]