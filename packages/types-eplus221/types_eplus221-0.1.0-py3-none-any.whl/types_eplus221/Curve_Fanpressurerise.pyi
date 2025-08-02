from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Fanpressurerise(EpBunch):
    """Special curve type with two independent variables."""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_C1: Annotated[float, Field(default=...)]

    Coefficient2_C2: Annotated[float, Field(default=...)]

    Coefficient3_C3: Annotated[float, Field(default=...)]

    Coefficient4_C4: Annotated[float, Field(default=...)]

    Minimum_Value_Of_Qfan: Annotated[float, Field(default=...)]

    Maximum_Value_Of_Qfan: Annotated[float, Field(default=...)]

    Minimum_Value_Of_Psm: Annotated[float, Field(default=...)]

    Maximum_Value_Of_Psm: Annotated[float, Field(default=...)]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""