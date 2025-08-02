from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Functionalmockupunitexport_From_Variable(EpBunch):
    """This object declares an FMU input variable"""

    Output_Variable_Index_Key_Name: Annotated[str, Field(default=...)]

    Output_Variable_Name: Annotated[str, Field(default=...)]

    Fmu_Variable_Name: Annotated[str, Field(default=...)]