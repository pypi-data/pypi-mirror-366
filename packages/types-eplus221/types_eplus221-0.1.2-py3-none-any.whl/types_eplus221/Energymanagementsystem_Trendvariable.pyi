from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Trendvariable(EpBunch):
    """This object sets up an EMS trend variable from an Erl variable"""

    Name: Annotated[str, Field(default=...)]
    """no spaces allowed in name"""

    EMS_Variable_Name: Annotated[str, Field(default=...)]
    """must be a global scope EMS variable"""

    Number_of_Timesteps_to_be_Logged: Annotated[int, Field(default=..., ge=1)]