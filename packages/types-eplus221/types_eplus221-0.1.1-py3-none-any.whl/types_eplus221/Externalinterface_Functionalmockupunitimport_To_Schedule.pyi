from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Functionalmockupunitimport_To_Schedule(EpBunch):
    """This objects contains only one value, which is used during the first"""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Names: Annotated[str, Field()]

    Fmu_File_Name: Annotated[str, Field(default=...)]

    Fmu_Instance_Name: Annotated[str, Field(default=...)]

    Fmu_Variable_Name: Annotated[str, Field(default=...)]

    Initial_Value: Annotated[float, Field(default=...)]
    """Used during the first call of EnergyPlus."""