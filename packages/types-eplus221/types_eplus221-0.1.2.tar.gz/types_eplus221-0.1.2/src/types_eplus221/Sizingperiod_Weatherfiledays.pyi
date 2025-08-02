from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizingperiod_Weatherfiledays(EpBunch):
    """Use a weather file period for design sizing calculations."""

    Name: Annotated[str, Field(default=...)]
    """user supplied name for reporting"""

    Begin_Month: Annotated[int, Field(default=..., ge=1, le=12)]

    Begin_Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Month: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]

    Day_of_Week_for_Start_Day: Annotated[Literal['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field(default='Monday')]
    """=[|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|SummerDesignDay|WinterDesignDay|"""

    Use_Weather_File_Daylight_Saving_Period: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If yes or blank, use daylight saving period as specified on Weatherfile."""

    Use_Weather_File_Rain_and_Snow_Indicators: Annotated[Literal['Yes', 'No'], Field(default='Yes')]