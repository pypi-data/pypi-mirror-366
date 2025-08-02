from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Runperiod(EpBunch):
    """Specify a range of dates and other parameters for a simulation."""

    Name: Annotated[str, Field(default=...)]
    """descriptive name (used in reporting mainly)"""

    Begin_Month: Annotated[int, Field(default=..., ge=1, le=12)]

    Begin_Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]

    Begin_Year: Annotated[str, Field()]
    """Start year of the simulation, if this field is specified it must agree with the Day of Week for Start Day"""

    End_Month: Annotated[int, Field(default=..., ge=1, le=12)]

    End_Day_of_Month: Annotated[int, Field(default=..., ge=1, le=31)]

    End_Year: Annotated[str, Field()]
    """end year of simulation, if specified"""

    Day_of_Week_for_Start_Day: Annotated[Literal['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], Field()]
    """=[Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday];"""

    Use_Weather_File_Holidays_and_Special_Days: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If yes or blank, use holidays as specified on Weatherfile."""

    Use_Weather_File_Daylight_Saving_Period: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If yes or blank, use daylight saving period as specified on Weatherfile."""

    Apply_Weekend_Holiday_Rule: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """if yes and single day holiday falls on weekend, "holiday" occurs on following Monday"""

    Use_Weather_File_Rain_Indicators: Annotated[Literal['Yes', 'No'], Field(default='Yes')]

    Use_Weather_File_Snow_Indicators: Annotated[Literal['Yes', 'No'], Field(default='Yes')]

    Treat_Weather_as_Actual: Annotated[Literal['Yes', 'No'], Field(default='No')]