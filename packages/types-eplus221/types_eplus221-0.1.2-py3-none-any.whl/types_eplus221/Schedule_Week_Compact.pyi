from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Week_Compact(EpBunch):
    """Compact definition for Schedule:Day:List"""

    Name: Annotated[str, Field(default=...)]

    DayType_List_1: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field(default=...)]
    """"For" is an optional prefix/start of the For fields. Choices can be combined on single line"""

    ScheduleDay_Name_1: Annotated[str, Field(default=...)]

    DayType_List_2: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    ScheduleDay_Name_2: Annotated[str, Field()]

    DayType_List_3: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    ScheduleDay_Name_3: Annotated[str, Field()]

    DayType_List_4: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    ScheduleDay_Name_4: Annotated[str, Field()]

    DayType_List_5: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    ScheduleDay_Name_5: Annotated[str, Field()]