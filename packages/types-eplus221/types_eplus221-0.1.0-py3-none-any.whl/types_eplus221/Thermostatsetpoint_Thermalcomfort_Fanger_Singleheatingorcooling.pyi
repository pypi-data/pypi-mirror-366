from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermostatsetpoint_Thermalcomfort_Fanger_Singleheatingorcooling(EpBunch):
    """Used for heating and cooling thermal comfort control with a single setpoint. The PMV"""

    Name: Annotated[str, Field(default=...)]

    Fanger_Thermal_Comfort_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values should be Predicted Mean Vote (PMV)"""