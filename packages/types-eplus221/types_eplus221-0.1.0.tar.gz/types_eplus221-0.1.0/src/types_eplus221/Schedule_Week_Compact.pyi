from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Schedule_Week_Compact(EpBunch):
    """Compact definition for Schedule:Day:List"""

    Name: Annotated[str, Field(default=...)]

    Daytype_List_1: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field(default=...)]
    """"For" is an optional prefix/start of the For fields. Choices can be combined on single line"""

    Schedule_Day_Name_1: Annotated[str, Field(default=...)]

    Daytype_List_2: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    Schedule_Day_Name_2: Annotated[str, Field()]

    Daytype_List_3: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    Schedule_Day_Name_3: Annotated[str, Field()]

    Daytype_List_4: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    Schedule_Day_Name_4: Annotated[str, Field()]

    Daytype_List_5: Annotated[Literal['AllDays', 'AllOtherDays', 'Weekdays', 'Weekends', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Holiday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field()]

    Schedule_Day_Name_5: Annotated[str, Field()]