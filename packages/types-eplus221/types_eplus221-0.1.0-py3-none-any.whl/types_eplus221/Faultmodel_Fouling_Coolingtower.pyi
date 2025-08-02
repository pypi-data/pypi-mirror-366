from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Faultmodel_Fouling_Coolingtower(EpBunch):
    """This object describes the fault of fouling cooling towers"""

    Name: Annotated[str, Field(default=...)]
    """Enter the name of the fault"""

    Availability_Schedule_Name: Annotated[str, Field()]

    Severity_Schedule_Name: Annotated[str, Field()]

    Cooling_Tower_Object_Type: Annotated[Literal['CoolingTower:SingleSpeed', 'CoolingTower:TwoSpeed', 'CoolingTower:VariableSpeed:MERKEL'], Field(default=...)]
    """Enter the type of the cooling tower affected"""

    Cooling_Tower_Object_Name: Annotated[str, Field(default=...)]
    """Enter the name of the cooling tower affected"""

    Reference_Ua_Reduction_Factor: Annotated[float, Field(gt=0.0)]
    """Factor describing the tower UA reduction due to fouling"""