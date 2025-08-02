from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Functionalmockupunitimport_To_Variable(EpBunch):
    """Declares Erl variable as having global scope"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    Fmu_File_Name: Annotated[str, Field(default=...)]

    Fmu_Instance_Name: Annotated[str, Field(default=...)]

    Fmu_Variable_Name: Annotated[str, Field(default=...)]

    Initial_Value: Annotated[float, Field(default=...)]
    """Used during the first call of EnergyPlus."""