from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermostatsetpoint_Thermalcomfort_Fanger_Singleheating(EpBunch):
    """Used for heating only thermal comfort control. The PMV setpoint can be scheduled and"""

    Name: Annotated[str, Field(default=...)]

    Fanger_Thermal_Comfort_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values should be Predicted Mean Vote (PMV)"""