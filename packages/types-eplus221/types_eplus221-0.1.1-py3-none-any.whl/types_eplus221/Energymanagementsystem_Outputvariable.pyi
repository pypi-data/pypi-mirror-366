from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Outputvariable(EpBunch):
    """This object sets up an EnergyPlus output variable from an Erl variable"""

    Name: Annotated[str, Field(default=...)]

    Ems_Variable_Name: Annotated[str, Field(default=...)]
    """must be an acceptable EMS variable"""

    Type_Of_Data_In_Variable: Annotated[Literal['Averaged', 'Summed'], Field(default=...)]

    Update_Frequency: Annotated[Literal['ZoneTimestep', 'SystemTimestep'], Field(default=...)]

    Ems_Program_Or_Subroutine_Name: Annotated[str, Field()]
    """optional for global scope variables, required for local scope variables"""

    Units: Annotated[str, Field()]
    """optional but will result in dimensionless units for blank"""