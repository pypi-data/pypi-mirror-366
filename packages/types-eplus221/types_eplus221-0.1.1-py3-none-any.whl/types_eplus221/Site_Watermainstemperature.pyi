from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Watermainstemperature(EpBunch):
    """Used to calculate water mains temperatures delivered by underground water main pipes."""

    Calculation_Method: Annotated[Literal['Schedule', 'Correlation', 'CorrelationFromWeatherFile'], Field(default='CorrelationFromWeatherFile')]
    """If calculation method is CorrelationFromWeatherFile, the two numeric input"""

    Temperature_Schedule_Name: Annotated[str, Field()]

    Annual_Average_Outdoor_Air_Temperature: Annotated[float, Field()]
    """If calculation method is CorrelationFromWeatherFile or Schedule, this input"""

    Maximum_Difference_In_Monthly_Average_Outdoor_Air_Temperatures: Annotated[float, Field(ge=0)]
    """If calculation method is CorrelationFromWeatherFile or Schedule, this input"""