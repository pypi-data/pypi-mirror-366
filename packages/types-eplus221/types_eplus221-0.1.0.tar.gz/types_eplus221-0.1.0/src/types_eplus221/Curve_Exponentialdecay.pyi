from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Exponentialdecay(EpBunch):
    """Exponential decay curve with one independent variable."""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_C1: Annotated[float, Field(default=...)]

    Coefficient2_C2: Annotated[float, Field(default=...)]

    Coefficient3_C3: Annotated[float, Field(default=...)]

    Minimum_Value_Of_X: Annotated[float, Field(default=...)]

    Maximum_Value_Of_X: Annotated[float, Field(default=...)]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_For_X: Annotated[Literal['Dimensionless'], Field(default='Dimensionless')]

    Output_Unit_Type: Annotated[Literal['Dimensionless'], Field(default='Dimensionless')]