from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Humiditysensoroffset_Outdoorair(EpBunch):
    """This object describes outdoor air humidity sensor offset"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Controller_Object_Type: Annotated[Literal['Controller:OutdoorAir'], Field(default=...)]

    Controller_Object_Name: Annotated[str, Field(default=...)]

    Humidity_Sensor_Offset: Annotated[float, Field(gt=-0.02, lt=0.02, default=0.0)]