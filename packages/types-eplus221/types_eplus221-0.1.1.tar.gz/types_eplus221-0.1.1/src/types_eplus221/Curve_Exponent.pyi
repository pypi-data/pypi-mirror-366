from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Exponent(EpBunch):
    """Exponent curve with one independent variable."""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_Constant: Annotated[float, Field(default=...)]

    Coefficient2_Constant: Annotated[float, Field(default=...)]

    Coefficient3_Constant: Annotated[float, Field(default=...)]

    Minimum_Value_Of_X: Annotated[float, Field(default=...)]
    """Specify the minimum value of the independent variable x allowed"""

    Maximum_Value_Of_X: Annotated[float, Field(default=...)]
    """Specify the maximum value of the independent variable x allowed"""

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_For_X: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Output_Unit_Type: Annotated[Literal['Dimensionless', 'Capacity', 'Power', 'Temperature'], Field(default='Dimensionless')]