from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Internalvariable(EpBunch):
    """Declares EMS variable as an internal data variable"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    Internal_Data_Index_Key_Name: Annotated[str, Field()]

    Internal_Data_Type: Annotated[str, Field(default=...)]