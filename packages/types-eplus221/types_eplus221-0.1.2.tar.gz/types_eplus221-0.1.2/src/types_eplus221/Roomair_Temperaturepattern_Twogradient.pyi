from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Temperaturepattern_Twogradient(EpBunch):
    """Used to model room air with two temperature gradients in the vertical direction."""

    Room_Air_Temperature_Pattern_Two_Gradient_Name: Annotated[str, Field(default=...)]

    Control_Integer_for_Pattern_Control_Schedule_Name: Annotated[int, Field(default=...)]
    """reference this entry in Schedule Name"""

    Thermostat_Height: Annotated[float, Field()]
    """= Distance from floor of zone"""

    Return_Air_Height: Annotated[float, Field()]
    """= Distance from floor of zone"""

    Exhaust_Air_Height: Annotated[float, Field()]
    """= Distance from floor of zone"""

    Temperature_Gradient_Lower_Bound: Annotated[float, Field()]
    """Slope of temperature change in vertical direction"""

    Temperature_Gradient_Upper_Bound: Annotated[float, Field()]
    """Slope of temperature change in vertical direction"""

    Gradient_Interpolation_Mode: Annotated[Literal['OutdoorDryBulbTemperature', 'ZoneDryBulbTemperature', 'ZoneAndOutdoorTemperatureDifference', 'SensibleCoolingLoad', 'SensibleHeatingLoad'], Field()]

    Upper_Temperature_Bound: Annotated[float, Field()]

    Lower_Temperature_Bound: Annotated[float, Field()]

    Upper_Heat_Rate_Bound: Annotated[float, Field()]

    Lower_Heat_Rate_Bound: Annotated[float, Field()]