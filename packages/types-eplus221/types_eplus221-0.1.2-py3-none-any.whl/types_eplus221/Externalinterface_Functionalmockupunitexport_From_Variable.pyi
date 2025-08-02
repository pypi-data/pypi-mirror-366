from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Functionalmockupunitexport_From_Variable(EpBunch):
    """This object declares an FMU input variable"""

    OutputVariable_Index_Key_Name: Annotated[str, Field(default=...)]

    OutputVariable_Name: Annotated[str, Field(default=...)]

    FMU_Variable_Name: Annotated[str, Field(default=...)]