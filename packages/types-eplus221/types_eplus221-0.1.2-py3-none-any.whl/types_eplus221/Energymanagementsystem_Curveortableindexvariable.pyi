from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Energymanagementsystem_Curveortableindexvariable(EpBunch):
    """Declares EMS variable that identifies a curve or table"""

    Name: Annotated[str, Field(default=...)]
    """This name becomes a variable for use in Erl programs"""

    Curve_or_Table_Object_Name: Annotated[str, Field(default=...)]