from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Fouling_Evaporativecooler(EpBunch):
    """This object describes the fouling fault of the wetted coil evaporative cooler"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Evaporative_Cooler_Object_Type: Annotated[Literal['EvaporativeCooler:Indirect:WetCoil'], Field(default=...)]
    """Enter the type of a Evaporative Cooler object"""

    Evaporative_Cooler_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of aN Evaporative Cooler object"""

    Fouling_Factor: Annotated[float, Field(gt=0, le=1, default=1)]
    """The factor indicates the decrease of the indirect stage efficiency"""