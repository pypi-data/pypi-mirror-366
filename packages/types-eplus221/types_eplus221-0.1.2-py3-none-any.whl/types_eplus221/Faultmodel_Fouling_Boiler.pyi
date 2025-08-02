from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Fouling_Boiler(EpBunch):
    """This object describes the fouling fault of boilers with water-based heat exchangers"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Boiler_Object_Type: Annotated[Literal['Boiler:HotWater'], Field(default=...)]
    """Enter the type of a boiler object"""

    Boiler_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of a Boiler object"""

    Fouling_Factor: Annotated[float, Field(gt=0, le=1, default=1)]
    """The factor indicates the decrease of the nominal capacity of the boiler"""