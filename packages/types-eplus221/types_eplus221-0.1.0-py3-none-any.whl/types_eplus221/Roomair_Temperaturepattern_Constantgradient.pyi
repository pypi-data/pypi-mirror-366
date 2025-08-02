from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Temperaturepattern_Constantgradient(EpBunch):
    """Used to model room air with a fixed temperature gradient in the vertical direction."""

    Room_Air_Temperature_Pattern_Constant_Gradient_Name: Annotated[str, Field(default=...)]

    Control_Integer_For_Pattern_Control_Schedule_Name: Annotated[int, Field(default=...)]
    """reference this entry in Schedule Name"""

    Thermostat_Offset: Annotated[float, Field()]
    """= (Temp at thermostat- Mean Air Temp)"""

    Return_Air_Offset: Annotated[float, Field()]
    """= (Tleaving - Mean Air Temp )"""

    Exhaust_Air_Offset: Annotated[float, Field()]
    """= (Texhaust - Mean Air Temp) deg C"""

    Temperature_Gradient: Annotated[float, Field()]
    """Slope of temperature change in vertical direction"""