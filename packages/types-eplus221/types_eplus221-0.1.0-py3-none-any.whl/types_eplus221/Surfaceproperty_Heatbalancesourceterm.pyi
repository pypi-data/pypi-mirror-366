from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfaceproperty_Heatbalancesourceterm(EpBunch):
    """Allows an additional heat source term to be added to the inside or outside surface boundary."""

    Surface_Name: Annotated[str, Field(default=...)]

    Inside_Face_Heat_Source_Term_Schedule_Name: Annotated[str, Field()]
    """The value of this schedule is the source term value for the inside face of this surface"""

    Outside_Face_Heat_Source_Term_Schedule_Name: Annotated[str, Field()]
    """The value of this schedule is the source term value for the outside face of this surface"""