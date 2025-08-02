from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Designspecification_Zoneairdistribution(EpBunch):
    """This object is used to describe zone air distribution in terms of air distribution"""

    Name: Annotated[str, Field(default=...)]

    Zone_Air_Distribution_Effectiveness_in_Cooling_Mode: Annotated[float, Field(gt=0.0, default=1.0)]

    Zone_Air_Distribution_Effectiveness_in_Heating_Mode: Annotated[float, Field(gt=0.0, default=1.0)]

    Zone_Air_Distribution_Effectiveness_Schedule_Name: Annotated[str, Field()]
    """optionally used to replace Zone Air Distribution Effectiveness in Cooling and"""

    Zone_Secondary_Recirculation_Fraction: Annotated[float, Field(ge=0.0, default=0.0)]

    Minimum_Zone_Ventilation_Efficiency: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]