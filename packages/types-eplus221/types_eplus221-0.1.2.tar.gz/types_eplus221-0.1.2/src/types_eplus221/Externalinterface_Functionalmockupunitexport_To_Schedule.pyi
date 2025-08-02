from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Functionalmockupunitexport_To_Schedule(EpBunch):
    """This objects contains only one value, which is used during the first"""

    Schedule_Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Names: Annotated[str, Field()]

    FMU_Variable_Name: Annotated[str, Field(default=...)]

    Initial_Value: Annotated[float, Field(default=...)]
    """Used during the first call of EnergyPlus."""