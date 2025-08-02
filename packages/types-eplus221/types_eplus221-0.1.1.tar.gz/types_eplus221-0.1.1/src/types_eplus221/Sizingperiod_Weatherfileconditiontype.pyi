from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizingperiod_Weatherfileconditiontype(EpBunch):
    """Use a weather file period for design sizing calculations."""

    Name: Annotated[str, Field(default=...)]
    """user supplied name for reporting"""

    Period_Selection: Annotated[Literal['SummerExtreme', 'SummerTypical', 'WinterExtreme', 'WinterTypical', 'AutumnTypical', 'SpringTypical', 'WetSeason', 'DrySeason', 'NoDrySeason', 'NoWetSeason', 'TropicalHot', 'TropicalCold', 'NoDrySeasonMax', 'NoDrySeasonMin', 'NoWetSeasonMax', 'NoWetSeasonMin'], Field(default=...)]
    """Following is a list of all possible types of Extreme and Typical periods that"""

    Day_Of_Week_For_Start_Day: Annotated[Literal['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'SummerDesignDay', 'WinterDesignDay', 'CustomDay1', 'CustomDay2'], Field(default='Monday')]
    """=[|Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|SummerDesignDay|WinterDesignDay|"""

    Use_Weather_File_Daylight_Saving_Period: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If yes or blank, use daylight saving period as specified on Weatherfile."""

    Use_Weather_File_Rain_And_Snow_Indicators: Annotated[Literal['Yes', 'No'], Field(default='Yes')]